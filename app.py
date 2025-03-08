import certifi
from flask import Flask, render_template, jsonify, request,session,redirect,url_for
from pymongo import MongoClient
from bson import ObjectId
import bcrypt,os

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
            return jsonify({'success': False, 'message': 'Không thể phê duyệt người dùng. Có thể đã được phê duyệt trước đó.'}), 400  # Bad Request

    except Exception as e:
        print(f"Lỗi khi phê duyệt người dùng: {e}")
        return jsonify({'success': False, 'message': f'Lỗi hệ thống khi phê duyệt người dùng: {str(e)}'}), 500
def admin_logout():
    session.pop('admin_logged_in', None) # Xóa session variable 'admin_logged_in'
    return jsonify({'success': True, 'message': 'Đăng xuất admin thành công'}), 200 # OK


app = Flask(__name__)
app.secret_key = os.urandom(24)

client = MongoClient("mongodb+srv://Nhom07:Nhom07VAA@cluster0.fg6a2.mongodb.net/?retryWrites=true&w=majority",
                     tlsCAFile=certifi.where())

db = client.get_database('Block')
users_collection = db.users
candidate_collection = db.candidates


@app.route('/', methods=['GET', 'POST']) 
def index():
    if request.method == 'POST':
        admin  = admin_login(request)
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
        users = users_collection.find({'is_admin': False }) 
        user_list = [{
            "_id": str(user["_id"]),
            "is_approved": user.get("is_approved", False ),
            "fullname": user.get("fullname", "Không có tên"),
            "date_of_birth": user.get("date_of_birth", "Chưa cập nhật"),
            "hometown": user.get("hometown", "Chưa cập nhật"),
            "phone": user.get("phone", "Chưa cập nhật"),
            "id_document_path" : user.get("id_document_path","Chưa cập nhật"),
            "blockchain_hash": user.get("blockchain_hash", "Chưa cập nhật")
        } for user in users]
        return jsonify(user_list)
    except Exception as e:
        return jsonify({"error": f"Lỗi khi lấy dữ liệu: {str(e)}"}), 500
    
app.add_url_rule('/admin/approve_user/<user_id>', view_func=approve_user_endpoint, methods=['POST'])


@app.route('/register_candidate', methods=['POST'])
def register_candidate():
    try:
        data = request.json

        # Lấy ID lớn nhất hiện tại để tạo ID tự tăng
        last_candidate = candidate_collection.find_one(sort=[("candidate_id", -1)])
        new_id = (last_candidate["candidate_id"] + 1) if last_candidate else 1

        candidate_data = {
            "candidate_id": new_id,
            "full_name": data.get("full_name"),
            "dob": data.get("dob"),
            "gender": data.get("gender"),
            "nationality": data.get("nationality"),
            "ethnicity": data.get("ethnicity"),
            "religion": data.get("religion"),
            "hometown": data.get("hometown"),
            "current_residence": data.get("current_residence"),
            "education": data.get("education"),
            "specialty": data.get("specialty"),
            "academic_degree": data.get("academic_degree"),
            "political_theory": data.get("political_theory"),
            "foreign_language": data.get("foreign_language"),
            "occupation": data.get("occupation"),
            "workplace": data.get("workplace"),
            "party_join_date": data.get("party_join_date")
        }

        candidate_collection.insert_one(candidate_data)

        return jsonify({"message": "Đăng ký thành công!", "candidate_id": new_id}), 201
    except Exception as e:
        return jsonify({"error": f"Lỗi khi lưu dữ liệu: {str(e)}"}), 500


@app.route('/candidates', methods=['GET'])
def get_candidates():
    try:
        candidates = candidate_collection.find()
        candidate_list = [{
            "_id": str(candidate["_id"]),
            "candidate_id": candidate["candidate_id"],
            "full_name": candidate.get("full_name", ""),
            "dob": candidate.get("dob", ""),
            "gender": candidate.get("gender", ""),
            "nationality": candidate.get("nationality", ""),
            "ethnicity": candidate.get("ethnicity", ""),
            "religion": candidate.get("religion", ""),
            "hometown": candidate.get("hometown", ""),
            "current_residence": candidate.get("current_residence", ""),
            "education": candidate.get("education", ""),
            "specialty": candidate.get("specialty", ""),
            "academic_degree": candidate.get("academic_degree", ""),
            "political_theory": candidate.get("political_theory", ""),
            "foreign_language": candidate.get("foreign_language", ""),
            "occupation": candidate.get("occupation", ""),
            "workplace": candidate.get("workplace", ""),
            "party_join_date": candidate.get("party_join_date", "")
        } for candidate in candidates]

        return jsonify(candidate_list)
    except Exception as e:
        return jsonify({"error": f"Lỗi khi lấy danh sách ứng cử viên: {str(e)}"}), 500


@app.route("/candidates/<candidate_id>", methods=["DELETE"])
def delete_candidate(candidate_id):
    try:
        print(f"Deleting candidate with ID: {candidate_id}")  # Debug xem ID đúng không

        if not ObjectId.is_valid(candidate_id):
            return jsonify({"error": "Invalid ID format"}), 400

        result = candidate_collection.delete_one({"_id": ObjectId(candidate_id)})

        if result.deleted_count == 0:
            return jsonify({"error": "Candidate not found"}), 404

        return jsonify({"message": "Candidate deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/edit_candidates/<candidate_id>", methods=["GET"])
def get_candidate(candidate_id):
    try:
        if not ObjectId.is_valid(candidate_id):
            return jsonify({"error": "Invalid ID format"}), 400

        candidate = candidate_collection.find_one({"_id": ObjectId(candidate_id)})
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        candidate["_id"] = str(candidate["_id"])
        return jsonify(candidate)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/edit_candidates/<candidate_id>', methods=['PUT'])
def edit_candidate(candidate_id):
    try:
        if not ObjectId.is_valid(candidate_id):
            return jsonify({"error": "Invalid candidate ID"}), 400

        candidate_id = ObjectId(candidate_id)
        data = request.json

        candidate_collection.update_one({"_id": candidate_id}, {"$set": data})
        return jsonify({"message": "Candidate updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,port=8800)
