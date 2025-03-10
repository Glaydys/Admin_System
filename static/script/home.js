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
                    <td>${user.date_of_birth || 'Chưa cập nhật'}</td>
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
        method: 'POST', headers: {
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
    const btnThemCuocBauCu = document.getElementById("btnThemCuocBauCu");
    const formThemCuocBauCu = document.querySelector(".formThemCuocBauCu");
    const form = document.querySelector(".formThemCuocBauCu form");
    fetchElections()

    if (btnThemCuocBauCu && formThemCuocBauCu) {
        btnThemCuocBauCu.addEventListener("click", function () {
            // Ẩn tất cả các section khác nếu cần
            document.querySelectorAll(".main > div").forEach(div => div.classList.remove("active"));

            // Hiển thị form đăng ký
            formThemCuocBauCu.classList.add("active");
        });
    }

    if (btnHuy) {
        btnHuy.addEventListener("click", function () {
            formThemCuocBauCu.classList.remove("active");
        });
    }

    // Ẩn form lúc đầu bằng cách đảm bảo không có class active
    formThemCuocBauCu.classList.remove("active");
});

function hienFormUngCuVien() {
    document.getElementById("formUngCuVien").style.display = "block";
}

function anFormUngCuVien() {
    document.getElementById("formUngCuVien").style.display = "none";
}

function themUngCuVien() {
    let full_name = document.getElementById("full_name").value.trim();
    let dob = document.getElementById("dob").value.trim();
    let gender = document.getElementById("gender").value;
    let nationality = document.getElementById("nationality").value.trim();
    let ethnicity = document.getElementById("ethnicity").value.trim();
    let religion = document.getElementById("religion").value.trim();
    let hometown = document.getElementById("hometown").value.trim();
    let current_residence = document.getElementById("current_residence").value.trim();
    let occupation = document.getElementById("occupation").value.trim();
    let workplace = document.getElementById("workplace").value.trim();

    if (!full_name || !dob || !gender || !nationality || !ethnicity || !religion || !hometown || !current_residence || !occupation || !workplace) {
        alert("Vui lòng nhập đầy đủ thông tin ứng cử viên!");
        return;
    }

    let danhSach = document.getElementById("danhSachUngCuVien");

    let li = document.createElement("li");
    let ungCuVienInfo = [full_name, dob, gender, nationality, ethnicity, religion, hometown, current_residence, occupation, workplace];

    li.dataset.info = JSON.stringify(ungCuVienInfo); // Lưu thông tin dưới dạng JSON

    li.innerHTML = `<b>${full_name}</b>, ${dob}, ${gender}, ${nationality}, ${ethnicity}, ${religion}, ${hometown}, ${current_residence}, ${occupation}, ${workplace} 
                    <button onclick="xoaUngCuVien(this)">🗑 Xóa</button>`;

    danhSach.appendChild(li);

    // Ẩn form và reset dữ liệu nhập (chỉ reset text input)
    anFormUngCuVien();
    document.querySelectorAll("#formUngCuVien input[type='text'], #formUngCuVien input[type='date']").forEach(input => input.value = "");
}


function xoaUngCuVien(button) {
    let li = button.parentElement;
    li.remove(); // Xóa ứng cử viên khỏi danh sách
}

document.getElementById("electionForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    let tenCuocBauCu = document.getElementById("tenCuocBauCu").value;
    let khuVuc = document.getElementById("khuVuc").value;
    let thoiGianBatDau = document.getElementById("thoiGianBatDau").value;
    let thoiGianKetThuc = document.getElementById("thoiGianKetThuc").value;

    let ungCuVien = [];
    document.querySelectorAll("#danhSachUngCuVien li").forEach((li) => {
        ungCuVien.push(JSON.parse(li.dataset.info));
    });

    let data = {
        tenCuocBauCu, khuVuc, ungCuVien, thoiGianBatDau, thoiGianKetThuc
    };

    try {
        let response = await fetch("/add_election", {
            method: "POST", headers: {
                "Content-Type": "application/json"
            }, body: JSON.stringify(data)
        });

        let result = await response.json();
        alert(result.message);
        window.location.reload();
    } catch (error) {
        console.error("Lỗi:", error);
    }
});

function fetchElections() {
    fetch("/get_elections")
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector(".elections tbody");
            tbody.innerHTML = ""; // Xóa dữ liệu cũ

            data.forEach((election, index) => {
                const row = `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${election.tenCuocBauCu}</td>
                        <td>${election.khuVuc}</td>
                        <td>${election.ungCuVien}</td>
                        <td>${election.thoiGianBatDau}</td>
                        <td>${election.thoiGianKetThuc}</td>
                        <td><button onclick="Detail_elections('${election._id}')">Xem</button></td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        })
        .catch(error => console.error("Lỗi khi tải danh sách cuộc bầu cử:", error));
}

function Detail_elections(_id) {
    fetch(`/get_elections/${_id}`)
        .then(response => response.json())
        .then(election => {
            document.getElementById("modal_tenCuocBauCu").innerText = election.tenCuocBauCu;
            document.getElementById("modal_khuVuc").innerText = election.khuVuc;
            document.getElementById("modal_thoiGianBatDau").innerText = election.thoiGianBatDau;
            document.getElementById("modal_thoiGianKetThuc").innerText = election.thoiGianKetThuc;

            const tbody = document.getElementById("modal_ungCuVien");
            tbody.innerHTML = ""; // Xóa dữ liệu cũ

            election.ungCuVien.forEach((ucv, index) => {
                const row = `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${ucv[0]}</td>
                        <td>${ucv[1]}</td>
                        <td>${ucv[2]}</td>
                        <td>${ucv[3]}</td>
                        <td>${ucv[4]}</td>
                        <td>${ucv[5]}</td>
                        <td>${ucv[6]}</td>
                        <td>${ucv[7]}</td>
                        <td>${ucv[8]}</td>
                        <td>${ucv[9]}</td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });

            document.getElementById("electionModal").style.display = "block";
        })
        .catch(error => console.error("Lỗi khi lấy dữ liệu ứng viên:", error));
}

function closeModal() {
    document.getElementById("electionModal").style.display = "none";
}
