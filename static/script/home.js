const menuItems = document.querySelectorAll('.menu-item');
const sections = document.querySelectorAll('.main > div');

menuItems.forEach(item => {
    item.addEventListener('click', () => {
        menuItems.forEach(i => i.classList.remove('active'));
        sections.forEach(s => s.classList.remove('active'));

        item.classList.add('active');
        document.querySelector('.' + item.dataset.target).classList.add('active');
    });
});

function loadUsers() {
    fetch('/users')
        .then(response => response.json())
        .then(users => {
            const userTable = document.querySelector('.users tbody');
            userTable.innerHTML = users.map((user, index) => `
                <tr>
                    <td>${index + 1}</td>
                    <td>
                        <button
                            class="approve-button ${user.is_approved ? 'approved' : 'pending'}"
                            data-user-id="${user._id}"
                            onclick="toggleApproveUser('${user._id}')"
                            ${user.is_approved ? 'disabled' : ''} /
                        >
                            ${user.is_approved ? 'Đã duyệt' : 'Chờ duyệt'}
                        </button>
                    </td>
                    <td>${user.fullname}</td>
                    <td>${user.date_of_birth|| 'Chưa cập nhật'}</td>
                    <td>${user.hometown || 'Chưa cập nhật'}</td>
                    <td>${user.phone || 'Chưa cập nhật'}</td>
                    <td>${user.id_document_path || 'Chưa cập nhật'}</td>
                </tr>
            `).join('');
            document.querySelector('.users').classList.add('active');
        })
        .catch(error => console.error('Lỗi khi tải danh sách người dùng:', error));
}
//Phê duyệt user
function toggleApproveUser(userId) {
    fetch(`/admin/approve_user/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' 
            
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Phê duyệt người dùng thành công:', userId);
            
            const button = document.querySelector(`.approve-button[data-user-id="${userId}"]`);
            if (button) {
                button.classList.remove('pending');
                button.classList.add('approved');
                button.textContent = 'Đã duyệt';
                
            }
        } else {
            console.error('Lỗi phê duyệt người dùng:', data.message);
            alert('Lỗi phê duyệt người dùng: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Lỗi khi gửi yêu cầu phê duyệt:', error);
        
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const btnAddCandidate = document.getElementById("btnAddCandidate");
    const candidateForm = document.querySelector(".candidate-registration");
    const form = document.querySelector(".candidate-registration form");
    fetchCandidates();

    if (btnAddCandidate && candidateForm) {
        btnAddCandidate.addEventListener("click", function () {
            // Ẩn tất cả các section khác nếu cần
            document.querySelectorAll(".main > div").forEach(div => div.classList.remove("active"));

            // Hiển thị form đăng ký
            candidateForm.classList.add("active");
        });
    }

    //Gui yeu cau xu ly dang ki candidate
    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = new FormData(form);
        const jsonData = {};
        formData.forEach((value, key) => {
            jsonData[key] = value;
        });

        fetch("/register_candidate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(jsonData)
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || "Có lỗi xảy ra!");
            if (data.message) {
                form.reset(); // Reset form sau khi gửi thành công
            }
        })
        .catch(error => console.error("Lỗi:", error));
    });
});

function fetchCandidates() {
    fetch("/candidates")
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector(".elections tbody");
            tbody.innerHTML = ""; // Xóa dữ liệu cũ

            data.forEach((candidate, index) => {
                const row = `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${candidate.full_name}</td>
                        <td>${candidate.dob}</td>
                        <td>${candidate.gender}</td>
                        <td>${candidate.nationality}</td>
                        <td>${candidate.ethnicity}</td>
                        <td>${candidate.religion}</td>
                        <td>${candidate.hometown}</td>
                        <td>${candidate.current_residence}</td>
                        <td>${candidate.education}</td>
                        <td>${candidate.specialty}</td>
                        <td>${candidate.academic_degree}</td>
                        <td>${candidate.political_theory}</td>
                        <td>${candidate.foreign_language}</td>
                        <td>${candidate.occupation}</td>
                        <td>${candidate.workplace}</td>
                        <td>${candidate.party_join_date}</td>
                        <td><button onclick="editCandidate('${candidate._id}')">Sửa</button></td>
                        <td><button onclick="deleteCandidate('${candidate._id}')">Xóa</button></td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        })
        .catch(error => console.error("Lỗi khi tải danh sách ứng cử viên:", error));
}

function deleteCandidate(candidateId) {
        if (!confirm("Bạn có chắc muốn xóa ứng cử viên này?")) return;

        fetch(`/candidates/${candidateId}`, {
            method: "DELETE"
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Lỗi: " + data.error);
            } else {
                alert("Xóa thành công!");
                location.reload();
            }
        })
        .catch(error => console.error("Lỗi:", error));
    }

function editCandidate(candidateId) {
    console.log("Candidate ID:", candidateId);

    fetch(`/edit_candidates/${candidateId}`)
        .then(response => response.json())
        .then(candidate => {
            console.log("Candidate Data:", candidate);

            document.querySelector(".candidate-edit input[name='full_name']").value = candidate.full_name || "";
            document.querySelector(".candidate-edit input[name='dob']").value = candidate.dob || "";
            document.querySelector(".candidate-edit select[name='gender']").value = candidate.gender || "";
            document.querySelector(".candidate-edit input[name='nationality']").value = candidate.nationality || "";
            document.querySelector(".candidate-edit input[name='ethnicity']").value = candidate.ethnicity || "";
            document.querySelector(".candidate-edit input[name='religion']").value = candidate.religion || "";
            document.querySelector(".candidate-edit input[name='hometown']").value = candidate.hometown || "";
            document.querySelector(".candidate-edit input[name='current_residence']").value = candidate.current_residence || "";
            document.querySelector(".candidate-edit input[name='education']").value = candidate.education || "";
            document.querySelector(".candidate-edit input[name='specialty']").value = candidate.specialty || "";
            document.querySelector(".candidate-edit input[name='academic_degree']").value = candidate.academic_degree || "";
            document.querySelector(".candidate-edit input[name='political_theory']").value = candidate.political_theory || "";
            document.querySelector(".candidate-edit input[name='foreign_language']").value = candidate.foreign_language || "";
            document.querySelector(".candidate-edit input[name='occupation']").value = candidate.occupation || "";
            document.querySelector(".candidate-edit input[name='workplace']").value = candidate.workplace || "";
            document.querySelector(".candidate-edit input[name='party_join_date']").value = candidate.party_join_date || "";

            // Lưu candidateId vào form
            document.querySelector(".candidate-edit form").setAttribute("data-id", candidateId);

            // Hiển thị form chỉnh sửa
            document.querySelector(".candidate-edit").style.display = "block";
        })
        .catch(error => console.error("Lỗi khi lấy dữ liệu ứng viên:", error));
}

// Xử lý submit form chỉnh sửa
document.querySelector(".candidate-edit form").addEventListener("submit", function (event) {
    event.preventDefault();

    const candidateId = document.querySelector(".candidate-edit form").getAttribute("data-id");
    if (!candidateId) {
        console.error("Lỗi: candidateId không xác định!");
        return;
    }

    const formData = new FormData(this);
    const jsonData = {};
    formData.forEach((value, key) => {
        jsonData[key] = value;
    });

    fetch(`/edit_candidates/${candidateId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || "Có lỗi xảy ra!");
        if (data.message) {
            location.reload();
        }
    })
    .catch(error => console.error("Lỗi:", error));
});
