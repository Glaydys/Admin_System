import certifi
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
import bcrypt, os
from datetime import datetime


def admin_login(request):
    fullname = request.form.get('fullname')
    password = request.form.get('password')

    print(f"Thông tin đăng nhập admin: fullname={fullname}")

    if not fullname or not password:
        print("Lỗi: Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu admin")
        return None

    admin_user_data = users_collection.find_one({
        'fullname': fullname,
        'is_admin': True
    })

    if admin_user_data:
        if bcrypt.checkpw(password.encode('utf-8'), admin_user_data['password']):
            print("Đăng nhập admin thành công")
            return admin_user_data
        else:
            print("Lỗi: Mật khẩu admin không chính xác")
            return None
    else:
        print('Lỗi: Không tìm thấy tài khoản admin với tên đăng nhập này hoặc không có quyền admin')
        return None


def approve_user_endpoint(user_id):
    try:

        try:
            user_object_id = ObjectId(user_id)
        except Exception:
            print(f"User ID không hợp lệ: {user_id}")
            return jsonify({'success': False, 'message': 'ID người dùng không hợp lệ'}), 400  # Bad Request

        # Tìm user trong collection dựa trên _id
        user = users_collection.find_one({'_id': user_object_id})
        if not user:
            print(f"Không tìm thấy người dùng với ID: {user_id}")
            return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404  # Not Found

        # Cập nhật trường is_approved thành True
        result = users_collection.update_one(
            {'_id': user_object_id},
            {'$set': {'is_approved': True}}
        )

        if result.modified_count > 0:
            print(f"Đã phê duyệt người dùng thành công: {user_id}")
            return jsonify({'success': True, 'message': 'Phê duyệt người dùng thành công'}), 200  # OK
        else:
            # Trường hợp này có thể xảy ra nếu is_approved đã là True rồi
            print(f"Không thể phê duyệt người dùng (có thể đã được phê duyệt rồi): {user_id}")
            return jsonify({'success': False,
                            'message': 'Không thể phê duyệt người dùng. Có thể đã được phê duyệt trước đó.'}), 400  # Bad Request

    except Exception as e:
        print(f"Lỗi khi phê duyệt người dùng: {e}")
        return jsonify({'success': False, 'message': f'Lỗi hệ thống khi phê duyệt người dùng: {str(e)}'}), 500


def admin_logout():
    session.pop('admin_logged_in', None)  # Xóa session variable 'admin_logged_in'
    return jsonify({'success': True, 'message': 'Đăng xuất admin thành công'}), 200  # OK


app = Flask(__name__)
app.secret_key = os.urandom(24)

client = MongoClient("mongodb+srv://Nhom07:Nhom07VAA@cluster0.fg6a2.mongodb.net/?retryWrites=true&w=majority",
                     tlsCAFile=certifi.where())

db = client.get_database('Block')
users_collection = db.users
elections_collection = db.elections


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        admin = admin_login(request)
        if admin:
            session['fullname'] = admin['fullname']
            session['is_admin'] = admin['is_admin']
            return redirect(url_for('home'))
        else:
            print('login thất bại ở main')
            return render_template('index.html')
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = users_collection.find({'is_admin': False})
        user_list = [{
            "_id": str(user["_id"]),
            "is_approved": user.get("is_approved", False),
            "fullname": user.get("fullname", "Không có tên"),
            "date_of_birth": user.get("date_of_birth", "Chưa cập nhật"),
            "hometown": user.get("hometown", "Chưa cập nhật"),
            "phone": user.get("phone", "Chưa cập nhật"),
            "id_document_path": user.get("id_document_path", "Chưa cập nhật"),
            "blockchain_hash": user.get("blockchain_hash", "Chưa cập nhật")
        } for user in users]
        return jsonify(user_list)
    except Exception as e:
        return jsonify({"error": f"Lỗi khi lấy dữ liệu: {str(e)}"}), 500


app.add_url_rule('/admin/approve_user/<user_id>', view_func=approve_user_endpoint, methods=['POST'])


@app.route("/add_election", methods=["POST"])
def add_election():
    data = request.json
    result = elections_collection.insert_one(data)
    return jsonify({"message": "Thêm thành công!", "id": str(result.inserted_id)})


def format_datetime(dt_str):
    dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
    return dt.strftime("%d/%m/%Y %H:%M")


@app.route('/get_elections', methods=['GET'])
def get_elections():
    try:
        elections = elections_collection.find()
        elections_list = [{
            "_id": str(election["_id"]),
            "tenCuocBauCu": election["tenCuocBauCu"],
            "khuVuc": election.get("khuVuc", ""),
            "ungCuVien": len(election.get("ungCuVien", "")),
            "thoiGianBatDau": format_datetime(election.get("thoiGianBatDau", "")),
            "thoiGianKetThuc": format_datetime(election.get("thoiGianKetThuc", "")),
        } for election in elections]

        return jsonify(elections_list), 200
    except Exception as e:
        return jsonify({"error": f"Lỗi khi lấy danh sách cuộc bầu cử: {str(e)}"}), 500


@app.route("/get_elections/<_id>", methods=["GET"])
def get_election_detail(_id):
    election = elections_collection.find_one({"_id": ObjectId(_id)})
    if not election:
        return jsonify({"error": "Election not found"}), 404

    election_detail = {
        "_id": str(election["_id"]),
        "tenCuocBauCu": election["tenCuocBauCu"],
        "khuVuc": election.get("khuVuc", ""),
        "thoiGianBatDau": format_datetime(election.get("thoiGianBatDau", "")),
        "thoiGianKetThuc": format_datetime(election.get("thoiGianKetThuc", "")),
        "ungCuVien": election.get("ungCuVien", [])  # Trả về danh sách ứng cử viên đầy đủ
    }

    return jsonify(election_detail), 200


if __name__ == '__main__':
    app.run(debug=True, port=8800)
