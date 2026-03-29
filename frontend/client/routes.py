import requests
from flask import Blueprint, render_template, request

API_URL = "http://127.0.0.1:5001/api"
client_bp = Blueprint('client', __name__)

def load_data_from_db(search_text):
    try:
        response = requests.get(f"{API_URL}/hoc-phan", params={"q": search_text})
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        return []


@client_bp.route('/', methods=['GET', 'POST'])
def index():
    search_text = ""
    product_table = []

    if request.method == 'POST':
        search_text = request.form['searchInput'].strip()
        product_table = load_data_from_db(search_text)
    elif request.method == 'GET' and 'q' in request.args:
        search_text = request.args.get('q', '').strip()
        product_table = load_data_from_db(search_text)
    else:
        product_table = load_data_from_db("")

    return render_template('client/search.html', search_text=search_text, hoc_phans=product_table)


@client_bp.route('/hoc-phan/<int:id>')
def detail(id):
    try:
        response = requests.get(f"{API_URL}/hoc-phan/{id}")
        if response.status_code == 404:
            return "Không tìm thấy thông tin học phần", 404
        if response.status_code == 200:
            data = response.json()
            hoc_phan = data
            # API trả về list string cho mục tiêu, template có thể đang lặp qua dict có key 'noi_dung'
            muc_tieu = [{'noi_dung': mt} for mt in data.get('muc_tieu', [])]
            return render_template('client/detail.html', hoc_phan=hoc_phan, muc_tieu=muc_tieu)
        return "Lỗi Server", 500
    except Exception as e:
        return "Không thể kết nối đến máy chủ API", 500