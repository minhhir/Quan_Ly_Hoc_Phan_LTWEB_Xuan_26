import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

API_URL = "http://127.0.0.1:5001/api"
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
    try:
        response = requests.get(f"{API_URL}/hoc-phan")
        hoc_phans = response.json() if response.status_code == 200 else []
    except Exception:
        hoc_phans = []
        flash('Không thể kết nối đến máy chủ API', 'danger')
    return render_template('admin/list.html', hoc_phans=hoc_phans)


@admin_bp.route('/hoc-phan/add', methods=['GET', 'POST'])
def add():
    # Lấy danh sách khoa để hiển thị ở Dropdown Select
    danh_sach_khoa = []
    try:
        khoa_res = requests.get(f"{API_URL}/khoa")
        if khoa_res.status_code == 200:
            danh_sach_khoa = khoa_res.json()
    except Exception:
        flash('Không thể tải danh sách khoa từ API', 'danger')

    if request.method == 'POST':
        ma_hoc_phan = request.form['ma_hoc_phan'].strip()
        ten_tieng_viet = request.form['ten_tieng_viet'].strip()
        ten_tieng_anh = request.form['ten_tieng_anh'].strip()
        trinh_do_dao_tao = request.form['trinh_do_dao_tao'].strip()
        so_tin_chi = request.form['so_tin_chi'].strip()
        khoa_id = request.form['khoa_id'].strip()
        muc_tieu_text = request.form['muc_tieu_text'].strip()
        muc_tieu_list = _parse_objectives(muc_tieu_text)

        hoc_phan_data = {
            'ma_hoc_phan': ma_hoc_phan,
            'ten_tieng_viet': ten_tieng_viet,
            'ten_tieng_anh': ten_tieng_anh,
            'trinh_do_dao_tao': trinh_do_dao_tao,
            'so_tin_chi': so_tin_chi,
            'khoa_id': int(khoa_id) if khoa_id.isdigit() else None,
            'muc_tieu': muc_tieu_list
        }

        if not all([ma_hoc_phan, ten_tieng_viet, ten_tieng_anh, trinh_do_dao_tao, so_tin_chi, khoa_id]) or not muc_tieu_list:
            flash('Vui lòng nhập đầy đủ thông tin học phần và ít nhất 1 mục tiêu.', 'danger')
            return render_template(
                'admin/form.html',
                action='Thêm',
                hoc_phan=hoc_phan_data,
                danh_sach_khoa=danh_sach_khoa,
                muc_tieu_text=muc_tieu_text,
            )

        try:
            response = requests.post(f"{API_URL}/hoc-phan", json=hoc_phan_data)
            if response.status_code == 200:
                flash('Đã thêm học phần thành công!', 'success')
                return redirect(url_for('admin.index'))
            elif response.status_code == 409:
                flash('Mã học phần đã tồn tại. Vui lòng dùng mã khác.', 'danger')
                return render_template(
                    'admin/form.html',
                    action='Thêm',
                    hoc_phan=hoc_phan_data,
                    danh_sach_khoa=danh_sach_khoa,
                    muc_tieu_text=muc_tieu_text,
                )
            else:
                flash('Lỗi khi thêm học phần.', 'danger')
        except Exception:
            flash('Lỗi kết nối đến API backend.', 'danger')

        return render_template(
            'admin/form.html',
            action='Thêm',
            hoc_phan=hoc_phan_data,
            danh_sach_khoa=danh_sach_khoa,
            muc_tieu_text=muc_tieu_text,
        )

    return render_template('admin/form.html', action='Thêm', hoc_phan=None, danh_sach_khoa=danh_sach_khoa, muc_tieu_text='')


@admin_bp.route('/hoc-phan/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    danh_sach_khoa = []
    try:
        khoa_res = requests.get(f"{API_URL}/khoa")
        if khoa_res.status_code == 200:
            danh_sach_khoa = khoa_res.json()
    except Exception:
        pass

    if request.method == 'POST':
        ma_hoc_phan = request.form['ma_hoc_phan'].strip()
        ten_tieng_viet = request.form['ten_tieng_viet'].strip()
        ten_tieng_anh = request.form['ten_tieng_anh'].strip()
        trinh_do_dao_tao = request.form['trinh_do_dao_tao'].strip()
        so_tin_chi = request.form['so_tin_chi'].strip()
        khoa_id = request.form['khoa_id'].strip()
        muc_tieu_text = request.form['muc_tieu_text'].strip()
        muc_tieu_list = _parse_objectives(muc_tieu_text)

        hoc_phan_data = {
            'id': id,
            'ma_hoc_phan': ma_hoc_phan,
            'ten_tieng_viet': ten_tieng_viet,
            'ten_tieng_anh': ten_tieng_anh,
            'trinh_do_dao_tao': trinh_do_dao_tao,
            'so_tin_chi': so_tin_chi,
            'khoa_id': int(khoa_id) if khoa_id.isdigit() else None,
            'muc_tieu': muc_tieu_list
        }

        if not all([ma_hoc_phan, ten_tieng_viet, ten_tieng_anh, trinh_do_dao_tao, so_tin_chi, khoa_id]) or not muc_tieu_list:
            flash('Vui lòng nhập đầy đủ thông tin học phần và ít nhất 1 mục tiêu.', 'danger')
            return render_template(
                'admin/form.html',
                action='Sửa',
                hoc_phan=hoc_phan_data,
                danh_sach_khoa=danh_sach_khoa,
                muc_tieu_text=muc_tieu_text,
            )

        try:
            response = requests.put(f"{API_URL}/hoc-phan/{id}", json=hoc_phan_data)
            if response.status_code == 200:
                flash('Cập nhật học phần thành công!', 'success')
                return redirect(url_for('admin.index'))
            elif response.status_code == 409:
                flash('Mã học phần đã tồn tại. Vui lòng dùng mã khác.', 'danger')
            else:
                flash('Có lỗi xảy ra khi cập nhật.', 'danger')
        except Exception:
            flash('Lỗi kết nối đến API.', 'danger')

        return render_template(
            'admin/form.html',
            action='Sửa',
            hoc_phan=hoc_phan_data,
            danh_sach_khoa=danh_sach_khoa,
            muc_tieu_text=muc_tieu_text,
        )

    # Lấy thông tin hiện tại nếu là GET
    hoc_phan = None
    muc_tieu_text = ''
    try:
        hp_res = requests.get(f"{API_URL}/hoc-phan/{id}")
        if hp_res.status_code == 200:
            hoc_phan = hp_res.json()
            muc_tieu_list = hoc_phan.get('muc_tieu', [])
            muc_tieu_text = '\n'.join(muc_tieu_list)
        else:
            flash('Không tìm thấy học phần', 'danger')
            return redirect(url_for('admin.index'))
    except Exception:
        flash('Lỗi kết nối đến API.', 'danger')
        return redirect(url_for('admin.index'))

    return render_template('admin/form.html', action='Sửa', hoc_phan=hoc_phan, danh_sach_khoa=danh_sach_khoa, muc_tieu_text=muc_tieu_text)


@admin_bp.route('/hoc-phan/delete/<int:id>', methods=['POST'])
def delete(id):
    try:
        response = requests.delete(f"{API_URL}/hoc-phan/{id}")
        if response.status_code == 200:
            flash('Đã xóa học phần thành công!', 'success')
        else:
            flash('Có lỗi xảy ra khi xóa học phần.', 'danger')
    except Exception:
        flash('Lỗi kết nối đến API backend.', 'danger')

    return redirect(url_for('admin.index'))
