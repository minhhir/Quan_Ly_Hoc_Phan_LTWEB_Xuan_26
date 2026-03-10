import sqlite3

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db_connection

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _verify_password(stored_password, plain_password):
    if stored_password.startswith('pbkdf2:') or stored_password.startswith('scrypt:'):
        return check_password_hash(stored_password, plain_password)
    # Ho tro tai khoan cu dang luu plain text.
    return stored_password == plain_password


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('user_id'):
        return redirect(url_for('client.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not username or not password or not confirm_password:
            flash('Vui long nhap day du thong tin.', 'danger')
            return render_template('auth/signup.html', username=username)

        if len(password) < 6:
            flash('Mat khau toi thieu 6 ky tu.', 'danger')
            return render_template('auth/signup.html', username=username)

        if password != confirm_password:
            flash('Mat khau xac nhan khong khop.', 'danger')
            return render_template('auth/signup.html', username=username)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM role WHERE name = 'user'")
        role = cursor.fetchone()
        if not role:
            conn.close()
            flash('He thong role chua san sang.', 'danger')
            return render_template('auth/signup.html', username=username)

        try:
            cursor.execute(
                'INSERT INTO users (username, password, role_id) VALUES (?, ?, ?)',
                (username, generate_password_hash(password), role['id']),
            )
            conn.commit()
            conn.close()
            flash('Dang ky thanh cong. Vui long dang nhap.', 'success')
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            conn.close()
            flash('Ten dang nhap da ton tai.', 'danger')
            return render_template('auth/signup.html', username=username)

    return render_template('auth/signup.html', username='')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('client.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Vui long nhap ten dang nhap va mat khau.', 'danger')
            return render_template('auth/login.html', username=username)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT u.id, u.username, u.password, r.name AS role_name
            FROM users u
            JOIN role r ON r.id = u.role_id
            WHERE u.username = ?
            ''',
            (username,),
        )
        user = cursor.fetchone()
        conn.close()

        if not user or not _verify_password(user['password'], password):
            flash('Thong tin dang nhap khong dung.', 'danger')
            return render_template('auth/login.html', username=username)

        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role_name']

        flash('Dang nhap thanh cong.', 'success')
        if user['role_name'] == 'admin':
            return redirect(url_for('admin.index'))
        return redirect(url_for('client.index'))

    return render_template('auth/login.html', username='')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Ban da dang xuat.', 'success')
    return redirect(url_for('auth.login'))
