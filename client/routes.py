from flask import Blueprint, render_template, request
from database import get_db_connection

client_bp = Blueprint('client', __name__)


def load_data_from_db(search_text):
    conn = get_db_connection()
    cursor = conn.cursor()

    if search_text != "":
        # Tìm kiếm theo mã hoặc tên môn học
        sqlcommand = "SELECT * FROM hoc_phan WHERE ma_hoc_phan LIKE ? OR ten_tieng_viet LIKE ?"
        search_param = f"%{search_text}%"
        cursor.execute(sqlcommand, (search_param, search_param))
    else:
        # Mặc định hiển thị 15 môn
        sqlcommand = "SELECT * FROM hoc_phan LIMIT 15"
        cursor.execute(sqlcommand)

    data = cursor.fetchall()
    conn.close()
    return data


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
    conn = get_db_connection()
    cursor = conn.cursor()

    # Sửa lại câu query: Tìm đúng theo cột id
    cursor.execute("SELECT * FROM hoc_phan WHERE id = ?", (id,))
    hoc_phan = cursor.fetchone()

    if not hoc_phan:
        conn.close()
        return "Không tìm thấy thông tin học phần", 404

    # Lấy thêm mục tiêu học phần nếu có
    cursor.execute("SELECT noi_dung FROM hoc_phan_muc_tieu WHERE hoc_phan_id = ?", (id,))
    muc_tieu = cursor.fetchall()

    conn.close()

    return render_template('client/detail.html', hoc_phan=hoc_phan, muc_tieu=muc_tieu)