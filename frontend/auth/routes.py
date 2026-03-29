import requests
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

API_URL = "http://127.0.0.1:5001/api"
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


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

        try:
            response = requests.post(f"{API_URL}/users", json={"username": username, "password": password})
            if response.status_code == 200:
                flash('Dang ky thanh cong. Vui long dang nhap.', 'success')
                return redirect(url_for('auth.login'))
            elif response.status_code == 409:
                flash('Ten dang nhap da ton tai.', 'danger')
                return render_template('auth/signup.html', username=username)
            else:
                flash('Lỗi từ server đăng ký.', 'danger')
                return render_template('auth/signup.html', username=username)
        except Exception as e:
            flash('Không thể kết nối với API backend.', 'danger')
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

        try:
            response = requests.post(f"{API_URL}/auth/token", json={"username": username, "password": password})
            if response.status_code == 200:
                user_data = response.json()
                session.clear()
                session['user_id'] = user_data['user_id']
                session['username'] = user_data['username']
                session['role'] = user_data['role']

                flash('Dang nhap thanh cong.', 'success')
                if user_data['role'] == 'admin':
                    return redirect(url_for('admin.index'))
                return redirect(url_for('client.index'))
            else:
                flash('Thong tin dang nhap khong dung.', 'danger')
                return render_template('auth/login.html', username=username)
        except Exception as e:
            flash('Không thể kết nối với API backend.', 'danger')
            return render_template('auth/login.html', username=username)

    return render_template('auth/login.html', username='')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Ban da dang xuat.', 'success')
    return redirect(url_for('auth.login'))
