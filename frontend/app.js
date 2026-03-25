const API_BASE = "http://localhost:8000";

let addDeviceModal;
let checkoutModal;
let returnModal;
let historyModal;

document.addEventListener("DOMContentLoaded", () => {
    // Initialize Modals
    addDeviceModal = new bootstrap.Modal(document.getElementById('addDeviceModal'));
    checkoutModal = new bootstrap.Modal(document.getElementById('checkoutModal'));
    returnModal = new bootstrap.Modal(document.getElementById('returnModal'));
    historyModal = new bootstrap.Modal(document.getElementById('historyModal'));

    fetchDevices();

    // Default dates
    document.getElementById('checkoutDate').valueAsDate = new Date();
    document.getElementById('returnDate').valueAsDate = new Date();
});

async function fetchDevices() {
    try {
        const res = await fetch(`${API_BASE}/devices/`);
        const data = await res.json();
        renderDevices(data);
    } catch (e) {
        console.error("無法載入資料，請確認後端是否啟動: ", e);
        document.getElementById("deviceTableBody").innerHTML = 
            `<tr><td colspan="7" class="text-danger text-center">連線失敗！請檢查後端 (FastAPI) 與資料庫是否成功啟動。</td></tr>`;
    }
}

function renderDevices(devices) {
    const tbody = document.getElementById("deviceTableBody");
    tbody.innerHTML = "";
    
    if (devices.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">目前沒有設備資料</td></tr>`;
        return;
    }

    devices.forEach(d => {
        let statusBadge = d.status === "Available" 
            ? `<span class="status-badge status-available">可使用</span>` 
            : `<span class="status-badge status-in-use">使用中</span>`;

        let timeStr = d.status === "In Use" && d.checkout_date
            ? `<small class="text-muted">領出: ${d.checkout_date}</small>`
            : d.return_date ? `<small class="text-muted">歸還: ${d.return_date}</small>` : `-`;

        let buttons = "";
        if (d.status === "Available") {
            buttons += `<button class="btn btn-sm btn-outline-success me-1" onclick="openCheckout(${d.id})">領用</button>`;
        } else {
            buttons += `<button class="btn btn-sm btn-outline-warning me-1" onclick="openReturn(${d.id})">歸還</button>`;
        }
        buttons += `<button class="btn btn-sm btn-outline-info me-1" onclick="viewHistory(${d.id})">歷史</button>`;
        buttons += `<button class="btn btn-sm btn-outline-danger" onclick="deleteDevice(${d.id})">刪除</button>`;

        tbody.innerHTML += `
            <tr>
                <td>${statusBadge}</td>
                <td class="fw-bold">${d.asset_tag}</td>
                <td>${d.name}<br><small class="text-muted">${d.system_model || ''}</small></td>
                <td>${d.department || '-'}</td>
                <td>${d.assignee || '-'}</td>
                <td>${timeStr}</td>
                <td class="text-end">${buttons}</td>
            </tr>
        `;
    });
}

// 建立設備
async function createDevice() {
    const form = document.getElementById('addDeviceForm');
    if(!form.checkValidity()){
        form.reportValidity();
        return;
    }
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        const res = await fetch(`${API_BASE}/devices/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        if(res.ok) {
            addDeviceModal.hide();
            form.reset();
            fetchDevices();
        } else {
            alert("新增失敗");
        }
    } catch(e) {
        console.error(e);
        alert("網路錯誤");
    }
}

// 開啟領用清單
function openCheckout(id) {
    document.getElementById('checkoutDeviceId').value = id;
    document.getElementById('checkoutAssignee').value = "";
    document.getElementById('checkoutDepartment').value = "";
    checkoutModal.show();
}

async function checkoutDevice() {
    const id = document.getElementById('checkoutDeviceId').value;
    const assignee = document.getElementById('checkoutAssignee').value;
    const dept = document.getElementById('checkoutDepartment').value;
    const date = document.getElementById('checkoutDate').value;
    
    if(!assignee || !dept || !date) return alert("請填寫完整資訊");

    try {
        const res = await fetch(`${API_BASE}/devices/${id}/checkout?assignee=${encodeURIComponent(assignee)}&department=${encodeURIComponent(dept)}&checkout_date=${date}`, {
            method: 'PUT'
        });
        if(res.ok){
            checkoutModal.hide();
            fetchDevices();
        } else {
            alert("領用失敗");
        }
    } catch(e) { console.error(e); }
}

// 開啟歸還清單
function openReturn(id) {
    document.getElementById('returnDeviceId').value = id;
    returnModal.show();
}

async function returnDevice() {
    const id = document.getElementById('returnDeviceId').value;
    const date = document.getElementById('returnDate').value;
    
    if(!date) return alert("請填寫歸還日期");

    try {
        const res = await fetch(`${API_BASE}/devices/${id}/return?return_date=${date}`, {
            method: 'PUT'
        });
        if(res.ok){
            returnModal.hide();
            fetchDevices();
        } else {
            alert("歸還失敗");
        }
    } catch(e) { console.error(e); }
}

// 查詢歷史
async function viewHistory(id) {
    try {
        const res = await fetch(`${API_BASE}/devices/${id}`);
        if(res.ok) {
            const data = await res.json();
            const tbody = document.getElementById('historyTableBody');
            tbody.innerHTML = "";
            let records = data.history_records || [];
            
            if(records.length === 0) {
                tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">無歷史紀錄</td></tr>`;
            } else {
                records.reverse().forEach(r => {
                    let actionBadge = "";
                    if(r.action==="Checkout") actionBadge = '<span class="badge bg-warning text-dark">領用</span>';
                    else if(r.action==="Return") actionBadge = '<span class="badge bg-success">歸還</span>';
                    else if(r.action==="Add") actionBadge = '<span class="badge bg-primary">新增</span>';
                    else actionBadge = `<span class="badge bg-secondary">${r.action}</span>`;

                    const dateStr = new Date(r.action_date).toLocaleString('zh-TW');

                    tbody.innerHTML += `
                        <tr>
                            <td class="text-muted">${dateStr}</td>
                            <td>${actionBadge}</td>
                            <td>${r.assignee || '-'}</td>
                            <td>${r.notes || '-'}</td>
                        </tr>
                    `;
                });
            }
            historyModal.show();
        }
    } catch(e) {
        console.error(e);
        alert("無法讀取歷史紀錄");
    }
}

// 刪除設備
async function deleteDevice(id) {
    if(!confirm("確定要刪除此設備及其所有紀錄嗎？此動作無法復原。")) return;
    try {
        const res = await fetch(`${API_BASE}/devices/${id}`, { method: 'DELETE' });
        if(res.ok) fetchDevices();
        else alert("刪除失敗");
    } catch(e) { console.error(e); }
}
