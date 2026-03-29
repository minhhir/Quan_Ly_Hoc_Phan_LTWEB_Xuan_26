from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
CORS(app)

def _verify_password(stored_password, plain_password):
    if stored_password.startswith('pbkdf2:') or stored_password.startswith('scrypt:'):
        return check_password_hash(stored_password, plain_password)
    return stored_password == plain_password

@app.route('/api/auth/token', methods=['POST'])
def token():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username, u.password, r.name AS role_name
        FROM users u
        JOIN role r ON r.id = u.role_id
        WHERE u.username = ?
    ''', (username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not _verify_password(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role_name']
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username, r.name AS role_name
        FROM users u
        JOIN role r ON r.id = u.role_id
    ''')
    users = cursor.fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or len(password) < 6:
        return jsonify({'error': 'Invalid data'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM role WHERE name = 'user'")
    role = cursor.fetchone()
    if not role:
        conn.close()
        return jsonify({'error': 'Role not found'}), 500

    try:
        cursor.execute(
            'INSERT INTO users (username, password, role_id) VALUES (?, ?, ?)',
            (username, generate_password_hash(password), role['id'])
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username exists'}), 409
    
    user_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': user_id, 'message': 'User created'})

@app.route('/api/users/<int:id>', methods=['PUT'])
def update_user_role(id):
    data = request.json
    role_name = data.get('role_name', '').strip()
    if role_name not in ['admin', 'user']:
        return jsonify({'error': 'Invalid role'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM role WHERE name = ?", (role_name,))
    role = cursor.fetchone()
    if not role:
        conn.close()
        return jsonify({'error': 'Role not found'}), 500
    cursor.execute('UPDATE users SET role_id = ? WHERE id = ?', (role['id'], id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Role updated'})

@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'User deleted'})

@app.route('/api/hoc-phan', methods=['GET'])
def get_hoc_phans():
    search_text = request.args.get('q', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    if search_text:
        search_param = f"%{search_text}%"
        cursor.execute('''
            SELECT hp.*, k.ten_khoa 
            FROM hoc_phan hp 
            LEFT JOIN khoa k ON hp.khoa_id = k.id
            WHERE hp.ma_hoc_phan LIKE ? OR hp.ten_tieng_viet LIKE ?
            ORDER BY hp.ma_hoc_phan ASC
        ''', (search_param, search_param))
    else:
        cursor.execute('''
            SELECT hp.*, k.ten_khoa 
            FROM hoc_phan hp 
            LEFT JOIN khoa k ON hp.khoa_id = k.id
            ORDER BY hp.ma_hoc_phan ASC
        ''')
    hoc_phans = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in hoc_phans])

@app.route('/api/hoc-phan/<int:id>', methods=['GET'])
def get_hoc_phan(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM hoc_phan WHERE id = ?', (id,))
    hoc_phan = cursor.fetchone()
    if not hoc_phan:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    
    cursor.execute('SELECT noi_dung FROM hoc_phan_muc_tieu WHERE hoc_phan_id = ? ORDER BY id ASC', (id,))
    muc_tieu = [row['noi_dung'] for row in cursor.fetchall()]
    conn.close()
    
    res = dict(hoc_phan)
    res['muc_tieu'] = muc_tieu
    return jsonify(res)

@app.route('/api/hoc-phan', methods=['POST'])
def add_hoc_phan():
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO hoc_phan (ma_hoc_phan, ten_tieng_viet, ten_tieng_anh, trinh_do_dao_tao, so_tin_chi, khoa_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('ma_hoc_phan'), data.get('ten_tieng_viet'), data.get('ten_tieng_anh'), 
            data.get('trinh_do_dao_tao'), data.get('so_tin_chi'), data.get('khoa_id')
        ))
        hoc_phan_id = cursor.lastrowid
        if data.get('muc_tieu'):
            cursor.executemany(
                'INSERT INTO hoc_phan_muc_tieu (hoc_phan_id, noi_dung) VALUES (?, ?)',
                [(hoc_phan_id, mt) for mt in data.get('muc_tieu')]
            )
        conn.commit()
        conn.close()
        return jsonify({'id': hoc_phan_id, 'message': 'Created'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Mã học phần đã tồn tại'}), 409

@app.route('/api/hoc-phan/<int:id>', methods=['PUT'])
def update_hoc_phan(id):
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE hoc_phan
            SET ma_hoc_phan=?, ten_tieng_viet=?, ten_tieng_anh=?, trinh_do_dao_tao=?, so_tin_chi=?, khoa_id=?
            WHERE id=?
        ''', (
            data.get('ma_hoc_phan'), data.get('ten_tieng_viet'), data.get('ten_tieng_anh'), 
            data.get('trinh_do_dao_tao'), data.get('so_tin_chi'), data.get('khoa_id'), id
        ))
        
        cursor.execute('DELETE FROM hoc_phan_muc_tieu WHERE hoc_phan_id = ?', (id,))
        if data.get('muc_tieu'):
            cursor.executemany(
                'INSERT INTO hoc_phan_muc_tieu (hoc_phan_id, noi_dung) VALUES (?, ?)',
                [(id, mt) for mt in data.get('muc_tieu')]
            )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Updated'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Mã học phần đã tồn tại'}), 409

@app.route('/api/hoc-phan/<int:id>', methods=['DELETE'])
def delete_hoc_phan(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM hoc_phan_muc_tieu WHERE hoc_phan_id = ?', (id,))
    cursor.execute('DELETE FROM hoc_phan WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Deleted'})

@app.route('/api/khoa', methods=['GET'])
def get_khoa():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM khoa")
    khoa = cursor.fetchall()
    conn.close()
    return jsonify([dict(k) for k in khoa])

if __name__ == '__main__':
    from database import init_auth_tables
    init_auth_tables()
    app.run(port=5001, debug=True)
