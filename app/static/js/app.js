let empTable, deptTable;

$(document).ready(function () {
    // 0. Kiểm tra đăng nhập (Bảo mật Frontend)
    const userPerms = localStorage.getItem('userPerms');
    if (!userPerms && window.location.pathname !== '/auth/login') {
       //console.log('I am here')
        window.location.href = '/auth/login';
        return;
    }

    // Hiển thị tên người dùng nếu có (giúp nút đăng xuất thân thiện hơn)
    // Lấy tên từ "kho lưu trữ" localStorage
    const name = localStorage.getItem('userName');

    // Nếu có tên thì hiển thị vào thẻ có id="user-display-name"
    if (name) {
        $('#user-display-name').text(name);
    } else {
        $('#user-display-name').text('Guest');
    }

    // 1. Quản lý Tab (Ghi nhớ tab cũ)
    const lastTab = localStorage.getItem('activeTab');
    if (lastTab) {
        const tabTriggerEl = document.querySelector(`#${lastTab}`);
        if (tabTriggerEl) {
            const tab = new bootstrap.Tab(tabTriggerEl);
            tab.show();
        }
        // QUAN TRỌNG: Nếu tab cũ là Phân quyền, phải gọi khởi tạo bảng ngay
        if (lastTab === 'perm-tab-btn') {
            PermissionModule.init();
        }
    }

    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        localStorage.setItem('activeTab', e.target.id);
    });
    // Cập nhật giá trị hiển thị cho dropdown đúng với ngôn ngữ đang dùng
    $('#langSwitcher').val(currentLang);

    // Logic load ngôn ngữ cũ của bạn
    loadLanguage(currentLang);

    // Sự kiện thay đổi ngôn ngữ
    $('#langSwitcher').change(function () {
        const selected = $(this).val();
        localStorage.setItem('appLang', selected);
        loadLanguage(selected);
    });
    // 2. Khởi tạo dữ liệu ban đầu
    // Lưu ý: Việc khởi tạo Table nên để hàm loadLanguage (trong languages.js) quyết định 
    // để tránh việc bảng hiện ra tiếng Việt rồi mới đổi sang tiếng Anh.
    loadDeptsToDropdown();

    // 3. Áp dụng quyền để ẩn/hiện nút ngay khi load trang
    applyPermissions();

    // mở tab phân quyền
    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        const targetId = e.target.id;
        console.log("Đã bấm vào tab:", targetId); // KIỂM TRA DÒNG NÀY TRONG CONSOLE (F12)
        localStorage.setItem('activeTab', targetId);

        // Nếu nhấn vào tab Phân quyền thì khởi tạo bảng Perm
        if (targetId === 'perm-tab-btn') {
            PermissionModule.init();
        }
    });

});

// Hàm khởi tạo bảng Nhân viên (Dùng chung cho cả lần đầu và reload ngôn ngữ)
function initEmpTable(langUrl) {
    if ($.fn.DataTable.isDataTable('#empTable')) {
        $('#empTable').DataTable().destroy();
    }

    empTable = $('#empTable').DataTable({
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf', 'print'],
        ajax: { url: '/employees/api/all', dataSrc: '' },
        language: { url: langUrl },
        columns: [
            { data: 'ID' },
            { data: 'FullName' },
            { data: 'DeptName' },
            {
                data: null,
                render: row => `
                    <button class="btn btn-sm btn-warning" onclick='editEmp(${JSON.stringify(row)})'>${t('btn_edit') || 'Sửa'}</button>
                    <button class="btn btn-sm btn-danger" onclick='delEmp(${JSON.stringify(row)})'>${t('btn_delete') || 'Xóa'}</button>`
            }
        ]
    });
}

// Hàm khởi tạo bảng Bộ phận
function initDeptTable(langUrl) {
    if ($.fn.DataTable.isDataTable('#deptTable')) {
        $('#deptTable').DataTable().destroy();
    }

    deptTable = $('#deptTable').DataTable({
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf', 'print'],
        ajax: { url: '/departments/api/all', dataSrc: '' },
        language: { url: langUrl },
        columns: [
            { data: 'DeptID' },
            { data: 'DeptName' },
            {
                data: null,
                render: row => `
                    <button class="btn btn-sm btn-warning" onclick='editDept(${JSON.stringify(row)})'>${t('btn_edit') || 'Sửa'}</button>
                    <button class="btn btn-sm btn-danger" onclick='delDept(${JSON.stringify(row)})'>${t('btn_delete') || 'Xóa'}</button>`
            }
        ]
    });
}

// Hàm này sẽ được gọi từ languages.js sau khi tải xong JSON
function reloadDataTableLanguage() {
    const langUrl = currentLang === 'vi'
        ? "//cdn.datatables.net/plug-ins/1.13.4/i18n/vi.json"
        : "//cdn.datatables.net/plug-ins/1.13.4/i18n/en-GB.json";

    initEmpTable(langUrl);
    initDeptTable(langUrl);

    // Nếu đang ở tab phân quyền thì reload cả bảng đó
    // Kiểm tra tab đang mở từ localStorage thay vì check class
    const activeTab = localStorage.getItem('activeTab');
    if (activeTab === 'perm-tab-btn') {
        PermissionModule.initTable();
    }
}

// Load dropdown bộ phận với Select2 search
function loadDeptsToDropdown() {
    $.ajax({
        url: '/departments/api/all',
        type: 'GET',
        success: function (data) {
            let html = `<option value="">${t('placeholder_dept') || '-- Chọn bộ phận --'}</option>`;
            data.forEach(d => {
                html += `<option value="${d.DeptID}">${d.DeptName}</option>`;
            });

            $('#empDeptSelect').html(html).select2({
                theme: 'bootstrap-5',
                placeholder: t('placeholder_dept'),
                allowClear: true,
                width: '100%',
                dropdownParent: $('#empModal')
            });
        }
    });
}

function applyPermissions() {
    $('[data-perm]').each(function () {
        const requiredPerm = $(this).attr('data-perm');
        if (!Auth.has(requiredPerm)) {
            $(this).remove(); // Xóa hẳn nút khỏi giao diện nếu không có quyền
        } else {
            $(this).show(); // Hiện nút nếu có quyền
        }
    });
}