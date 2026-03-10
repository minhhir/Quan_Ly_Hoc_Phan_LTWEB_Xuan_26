import sqlite3

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
def require_admin_role():
    if not session.get('user_id'):
        flash('Vui long dang nhap de truy cap khu vuc admin.', 'danger')
        return redirect(url_for('auth.login'))

    if session.get('role') != 'admin':
        flash('Ban khong co quyen truy cap khu vuc admin.', 'danger')
        return redirect(url_for('client.index'))


def _parse_objectives(raw_text):
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


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
        ma_hoc_phan = request.form['ma_hoc_phan'].strip()
        ten_tieng_viet = request.form['ten_tieng_viet'].strip()
        ten_tieng_anh = request.form['ten_tieng_anh'].strip()
        trinh_do_dao_tao = request.form['trinh_do_dao_tao'].strip()
        so_tin_chi = request.form['so_tin_chi'].strip()
        khoa_id = request.form['khoa_id'].strip()
        muc_tieu_text = request.form['muc_tieu_text'].strip()
        muc_tieu_list = _parse_objectives(muc_tieu_text)

        if not all([ma_hoc_phan, ten_tieng_viet, ten_tieng_anh, trinh_do_dao_tao, so_tin_chi, khoa_id]) or not muc_tieu_list:
            flash('Vui lòng nhập đầy đủ thông tin học phần và ít nhất 1 mục tiêu.', 'danger')
            cursor.execute('SELECT * FROM khoa')
            danh_sach_khoa = cursor.fetchall()
            conn.close()
            hoc_phan_data = {
                'ma_hoc_phan': ma_hoc_phan,
                'ten_tieng_viet': ten_tieng_viet,
                'ten_tieng_anh': ten_tieng_anh,
                'trinh_do_dao_tao': trinh_do_dao_tao,
                'so_tin_chi': so_tin_chi,
                'khoa_id': int(khoa_id) if khoa_id.isdigit() else None,
            }
            return render_template(
                'admin/form.html',
                action='Thêm',
                hoc_phan=hoc_phan_data,
                danh_sach_khoa=danh_sach_khoa,
                muc_tieu_text=muc_tieu_text,
            )

        try:
            cursor.execute('''
                INSERT INTO hoc_phan (ma_hoc_phan, ten_tieng_viet, ten_tieng_anh, trinh_do_dao_tao, so_tin_chi, khoa_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ma_hoc_phan, ten_tieng_viet, ten_tieng_anh, trinh_do_dao_tao, so_tin_chi, khoa_id))
            hoc_phan_id = cursor.lastrowid
            cursor.executemany(
                'INSERT INTO hoc_phan_muc_tieu (hoc_phan_id, noi_dung) VALUES (?, ?)',
                [(hoc_phan_id, mt) for mt in muc_tieu_list],
            )
            conn.commit()
            conn.close()
            flash('Đã thêm học phần thành công!', 'success')
            return redirect(url_for('admin.index'))
        except sqlite3.IntegrityError:
            cursor.execute('SELECT * FROM khoa')
            danh_sach_khoa = cursor.fetchall()
            conn.close()
            flash('Mã học phần đã tồn tại. Vui lòng dùng mã khác.', 'danger')
            hoc_phan_data = {
                'ma_hoc_phan': ma_hoc_phan,
                'ten_tieng_viet': ten_tieng_viet,
                'ten_tieng_anh': ten_tieng_anh,
                'trinh_do_dao_tao': trinh_do_dao_tao,
                'so_tin_chi': so_tin_chi,
                'khoa_id': int(khoa_id) if khoa_id.isdigit() else None,
            }
            return render_template(
                'admin/form.html',
                action='Thêm',
                hoc_phan=hoc_phan_data,
                danh_sach_khoa=danh_sach_khoa,
                muc_tieu_text=muc_tieu_text,
            )

    # Lấy danh sách khoa để hiển thị ở Dropdown Select
    cursor.execute("SELECT * FROM khoa")
    danh_sach_khoa = cursor.fetchall()
    conn.close()

    return render_template('admin/form.html', action='Thêm', hoc_phan=None, danh_sach_khoa=danh_sach_khoa, muc_tieu_text='')


@admin_bp.route('/hoc-phan/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        ma_hoc_phan = request.form['ma_hoc_phan'].strip()
        ten_tieng_viet = request.form['ten_tieng_viet'].strip()
        ten_tieng_anh = request.form['ten_tieng_anh'].strip()
        trinh_do_dao_tao = request.form['trinh_do_dao_tao'].strip()
        so_tin_chi = request.form['so_tin_chi'].strip()
        khoa_id = request.form['khoa_id'].strip()
        muc_tieu_text = request.form['muc_tieu_text'].strip()
        muc_tieu_list = _parse_objectives(muc_tieu_text)

        if not all([ma_hoc_phan, ten_tieng_viet, ten_tieng_anh, trinh_do_dao_tao, so_tin_chi, khoa_id]) or not muc_tieu_list:
            flash('Vui lòng nhập đầy đủ thông tin học phần và ít nhất 1 mục tiêu.', 'danger')
            cursor.execute('SELECT * FROM khoa')
            danh_sach_khoa = cursor.fetchall()
            conn.close()
            hoc_phan_data = {
                'id': id,
                'ma_hoc_phan': ma_hoc_phan,
                'ten_tieng_viet': ten_tieng_viet,
                'ten_tieng_anh': ten_tieng_anh,
                'trinh_do_dao_tao': trinh_do_dao_tao,
                'so_tin_chi': so_tin_chi,
                'khoa_id': int(khoa_id) if khoa_id.isdigit() else None,
            }
            return render_template(
                'admin/form.html',
                action='Sửa',
                hoc_phan=hoc_phan_data,
                danh_sach_khoa=danh_sach_khoa,
                muc_tieu_text=muc_tieu_text,
            )

        try:
            cursor.execute('''
                UPDATE hoc_phan
                SET ma_hoc_phan=?, ten_tieng_viet=?, ten_tieng_anh=?, trinh_do_dao_tao=?, so_tin_chi=?, khoa_id=?
                WHERE id=?
            ''', (ma_hoc_phan, ten_tieng_viet, ten_tieng_anh, trinh_do_dao_tao, so_tin_chi, khoa_id, id))
            cursor.execute('DELETE FROM hoc_phan_muc_tieu WHERE hoc_phan_id = ?', (id,))
            cursor.executemany(
                'INSERT INTO hoc_phan_muc_tieu (hoc_phan_id, noi_dung) VALUES (?, ?)',
                [(id, mt) for mt in muc_tieu_list],
            )
            conn.commit()
            conn.close()
            flash('Cập nhật học phần thành công!', 'success')
            return redirect(url_for('admin.index'))
        except sqlite3.IntegrityError:
            cursor.execute('SELECT * FROM khoa')
            danh_sach_khoa = cursor.fetchall()
            conn.close()
            flash('Mã học phần đã tồn tại. Vui lòng dùng mã khác.', 'danger')
            hoc_phan_data = {
                'id': id,
                'ma_hoc_phan': ma_hoc_phan,
                'ten_tieng_viet': ten_tieng_viet,
                'ten_tieng_anh': ten_tieng_anh,
                'trinh_do_dao_tao': trinh_do_dao_tao,
                'so_tin_chi': so_tin_chi,
                'khoa_id': int(khoa_id) if khoa_id.isdigit() else None,
            }
            return render_template(
                'admin/form.html',
                action='Sửa',
                hoc_phan=hoc_phan_data,
                danh_sach_khoa=danh_sach_khoa,
                muc_tieu_text=muc_tieu_text,
            )

    # Lấy thông tin môn học hiện tại
    cursor.execute('SELECT * FROM hoc_phan WHERE id = ?', (id,))
    hoc_phan = cursor.fetchone()
    cursor.execute('SELECT noi_dung FROM hoc_phan_muc_tieu WHERE hoc_phan_id = ? ORDER BY id ASC', (id,))
    muc_tieu_rows = cursor.fetchall()
    muc_tieu_text = '\n'.join(mt['noi_dung'] for mt in muc_tieu_rows)

    # Lấy danh sách khoa
    cursor.execute("SELECT * FROM khoa")
    danh_sach_khoa = cursor.fetchall()
    conn.close()

    return render_template('admin/form.html', action='Sửa', hoc_phan=hoc_phan, danh_sach_khoa=danh_sach_khoa, muc_tieu_text=muc_tieu_text)


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
