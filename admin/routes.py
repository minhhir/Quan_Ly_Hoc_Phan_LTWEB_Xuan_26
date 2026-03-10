from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.database import get_db_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/hoc-phan')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Lấy danh sách kèm tên khoa
    cursor.execute('''
        SELECT hp.id, hp.ma_hoc_phan, hp.ten_tieng_viet, hp.so_tin_chi, k.ten_khoa 
        FROM hoc_phan hp 
        LEFT JOIN khoa k ON hp.khoa_id = k.id
        ORDER BY hp.ma_hoc_phan ASC
    ''')
    hoc_phans = cursor.fetchall()
    conn.close()
    return render_template('admin/list.html', hoc_phans=hoc_phans)


@admin_bp.route('/hoc-phan/add', methods=['GET', 'POST'])
def add():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        ma_hoc_phan = request.form['ma_hoc_phan']
        ten_tieng_viet = request.form['ten_tieng_viet']
        ten_tieng_anh = request.form['ten_tieng_anh']
        trinh_do_dao_tao = request.form['trinh_do_dao_tao']
        so_tin_chi = request.form['so_tin_chi']
        khoa_id = request.form['khoa_id']

        cursor.execute('''
            INSERT INTO hoc_phan (ma_hoc_phan, ten_tieng_viet, ten_tieng_anh, trinh_do_dao_tao, so_tin_chi, khoa_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ma_hoc_phan, ten_tieng_viet, ten_tieng_anh, trinh_do_dao_tao, so_tin_chi, khoa_id))
        conn.commit()
        conn.close()

        flash('Đã thêm học phần thành công!', 'success')
        return redirect(url_for('admin.index'))

    # Lấy danh sách khoa để hiển thị ở Dropdown Select
    cursor.execute("SELECT * FROM khoa")
    danh_sach_khoa = cursor.fetchall()
    conn.close()

    return render_template('admin/add.html', danh_sach_khoa=danh_sach_khoa)


@admin_bp.route('/hoc-phan/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        ma_hoc_phan = request.form['ma_hoc_phan']
        ten_tieng_viet = request.form['ten_tieng_viet']
        ten_tieng_anh = request.form['ten_tieng_anh']
        trinh_do_dao_tao = request.form['trinh_do_dao_tao']
        so_tin_chi = request.form['so_tin_chi']
        khoa_id = request.form['khoa_id']

        cursor.execute('''
            UPDATE hoc_phan 
            SET ma_hoc_phan=?, ten_tieng_viet=?, ten_tieng_anh=?, trinh_do_dao_tao=?, so_tin_chi=?, khoa_id=?
            WHERE id=?
        ''', (ma_hoc_phan, ten_tieng_viet, ten_tieng_anh, trinh_do_dao_tao, so_tin_chi, khoa_id, id))
        conn.commit()
        conn.close()

        flash('Cập nhật học phần thành công!', 'success')
        return redirect(url_for('admin.index'))

    # Lấy thông tin môn học hiện tại
    cursor.execute('SELECT * FROM hoc_phan WHERE id = ?', (id,))
    hoc_phan = cursor.fetchone()

    # Lấy danh sách khoa
    cursor.execute("SELECT * FROM khoa")
    danh_sach_khoa = cursor.fetchall()
    conn.close()

    return render_template('admin/edit.html', hoc_phan=hoc_phan, danh_sach_khoa=danh_sach_khoa)


@admin_bp.route('/hoc-phan/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Xóa các mục tiêu học phần liên kết trước (Ràng buộc khóa ngoại)
    cursor.execute('DELETE FROM hoc_phan_muc_tieu WHERE hoc_phan_id = ?', (id,))
    # Xóa học phần
    cursor.execute('DELETE FROM hoc_phan WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Đã xóa học phần thành công!', 'success')
    return redirect(url_for('admin.index'))