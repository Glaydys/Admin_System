import certifi
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
import bcrypt, os
from datetime import datetime
from web3 import Web3
import json
from dotenv import load_dotenv
import os
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
provider = os.getenv("WEB3_PROVIDER")
contract_address = os.getenv("CONTRACT_ADDRESS")

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

# Kết nối với Ganache
w3 = Web3(Web3.HTTPProvider(provider))

if w3.is_connected():
    print("Kết nối thành công với Ganache!")
    accounts = w3.eth.accounts
    if accounts:
        w3.eth.default_account = accounts[0]
        print("Tài khoản mặc định:", w3.eth.default_account)
    else:
        raise Exception("Không tìm thấy tài khoản nào trong Ganache!")
else:
    raise Exception("Kết nối Web3 thất bại!")

# Chuyển đổi địa chỉ contract sang dạng checksum
contract_address = w3.to_checksum_address(contract_address)
print("Địa chỉ smart contract:", contract_address)


# Tải ABI từ file Election.json
with open('abi/Election.json') as f:
   abi = json.load(f)  # Đọc ABI từ file JSON

contract = w3.eth.contract(address=contract_address, abi=abi)  # Tạo instance của contract

app = Flask(__name__)
app.secret_key = os.urandom(24)

client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())

db = client.get_database('Block')
users_collection = db.users
elections_collection = db.elections
ungcuvien = db.candidates

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
def create_election():
    data = request.json
    try:
        # Chuyển đổi datetime thành timestamp (float)
        start_time = datetime.strptime(data['thoiGianBatDau'], "%Y-%m-%dT%H:%M").timestamp()
        end_time = datetime.strptime(data['thoiGianKetThuc'], "%Y-%m-%dT%H:%M").timestamp()

        # Tạo danh sách ứng cử viên rỗng nếu không có
        if "ungCuVien" not in data:
            data["ungCuVien"] = []

        # Gọi hàm Smart Contract
        tx_hash = contract.functions.createElection(
            data['tenCuocBauCu'],
            data['tinh'],
            data['quan'],
            data['phuong'],
            int(start_time),    # timestamp dạng số nguyên (cho Smart Contract)
            int(end_time)       # timestamp dạng số nguyên (cho Smart Contract)
        ).transact({'from': w3.eth.default_account})

        # Chờ xác nhận giao dịch
        w3.eth.wait_for_transaction_receipt(tx_hash)

        # Lưu timestamp dạng float vào MongoDB
        data['thoiGianBatDau'] = start_time
        data['thoiGianKetThuc'] = end_time

        # Lưu vào MongoDB
        result = elections_collection.insert_one(data)

        return jsonify({
            "message": "Cuộc bầu cử đã được tạo thành công!",
            "id": str(result.inserted_id),
            "transaction_hash": tx_hash.hex()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def format_datetime(dt_value):
    if isinstance(dt_value, float) or isinstance(dt_value, int):
        dt = datetime.fromtimestamp(dt_value)  # Chuyển timestamp (float/int) thành datetime
    elif isinstance(dt_value, str):
        dt = datetime.strptime(dt_value, "%Y-%m-%dT%H:%M")
    else:
        return "Không xác định"
    return dt.strftime("%d/%m/%Y %H:%M")

@app.route('/get_elections', methods=['GET'])
def get_elections():
    try:
        elections = elections_collection.find()
        elections_list = [{
            "_id": str(election["_id"]),
            "tenCuocBauCu": election["tenCuocBauCu"],
            "tinh": election.get("tinh", ""),
            "quan": election.get("quan", ""),
            "phuong": election.get("phuong", ""),
            "ungCuVien": len(election.get("ungCuVien", "")),
            "thoiGianBatDau": format_datetime(election.get("thoiGianBatDau", "")),
            "thoiGianKetThuc": format_datetime(election.get("thoiGianKetThuc", "")),
        } for election in elections]

        return jsonify(elections_list), 200
    except Exception as e:
        return jsonify({"error": f"Lỗi khi lấy danh sách cuộc bầu cử: {str(e)}"}), 500

@app.route('/get_candidates', methods=['GET'])
def get_candidates():
    try:
        candidates = ungcuvien.find()  # Lấy tất cả ứng cử viên từ MongoDB
        candidate_list = []
        for candidate in candidates:
            candidate['_id'] = str(candidate['_id'])  # Chuyển ObjectId thành string
            candidate_list.append(candidate)
        print("Candidate List:", candidate_list)  # In ra danh sách ứng cử viên để kiểm tra
        return jsonify(candidate_list), 200
    except Exception as e:
        print("Error getting candidates:", str(e))  # In ra lỗi nếu có
        return jsonify({"error": str(e)}), 500

@app.route('/add_candidate', methods=['POST'])
def add_candidate():
    try:
        candidate_data = request.json
        result = ungcuvien.insert_one(candidate_data)
        return jsonify({"message": "Ứng cử viên đã được thêm thành công!", "id": str(result.inserted_id)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_elections/<_id>", methods=["GET"])
def get_election_detail(_id):
    election = elections_collection.find_one({"_id": ObjectId(_id)})
    if not election:
        return jsonify({"error": "Election not found"}), 404

    election_detail = {
        "_id": str(election["_id"]),
        "tenCuocBauCu": election["tenCuocBauCu"],
        "tinh": election.get("tinh", ""),
        "quan": election.get("quan", ""),
        "phuong": election.get("phuong", ""),
        "thoiGianBatDau": format_datetime(election.get("thoiGianBatDau", "")),
        "thoiGianKetThuc": format_datetime(election.get("thoiGianKetThuc", "")),
        "ungCuVien": election.get("ungCuVien", [])  # Trả về danh sách ứng cử viên đầy đủ
    }

    return jsonify(election_detail), 200

@app.route("/add_candidate_elections/<_id>", methods=["POST"])
def add_candidate_elections(_id):
    data = request.json  # Nhận dữ liệu ứng viên từ frontend

    election = elections_collection.find_one({"_id": ObjectId(_id)})
    if not election:
        return jsonify({"error": "Election not found"}), 404

    new_candidate = {
        "name": data.get("name"),
        "dob": data.get("dob"),
        "gender": data.get("gender"),
        "nationality": data.get("nationality"),
        "ethnicity": data.get("ethnicity"),
        "religion": data.get("religion"),
        "hometown": data.get("hometown"),
        "currentResidence": data.get("currentResidence"),
        "occupation": data.get("occupation"),
        "workplace": data.get("workplace"),
        "isApproved": False  # Mặc định chưa được phê duyệt
    }

    # Thêm ứng viên vào danh sách ungCuVien
    elections_collection.update_one(
        {"_id": ObjectId(_id)},
        {"$push": {"ungCuVien": new_candidate}}
    )

    return jsonify({"message": "Candidate added successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8800)
