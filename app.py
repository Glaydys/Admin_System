import certifi
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb+srv://Nhom07:Nhom07VAA@cluster0.fg6a2.mongodb.net/?retryWrites=true&w=majority",
                     tlsCAFile=certifi.where())

db = client.get_database('Block')
users_collection = db.users
candidate_collection = db.candidates

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = users_collection.find()
        user_list = [{
            "_id": str(user["_id"]),
            "fullname": user.get("fullname", "Không có tên"),
            "date_of_birth": user.get("date_of_birth", "Chưa cập nhật"),
            "hometown": user.get("hometown", "Chưa cập nhật"),
            "phone_number": user.get("phone_number", "Chưa cập nhật"),
             "id_document_path" : user.get("id_document_path","Chưa cập nhật"),
            "blockchain_hash": user.get("blockchain_hash", "Chưa cập nhật")
        } for user in users]
        return jsonify(user_list)
    except Exception as e:
        return jsonify({"error": f"Lỗi khi lấy dữ liệu: {str(e)}"}), 500


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
    app.run(debug=True)
