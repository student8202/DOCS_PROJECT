const PermissionModule = {
    init: function () {
        // Khởi tạo Select2 cho Modal
        $('#viewDeptsSelect').select2({
            theme: 'bootstrap-5',
            dropdownParent: $('#permModal'),
            width: '100%'
        });
        this.loadTable();
    },

    loadTable: function () {
        $('#permTable').DataTable({
            ajax: { url: '/permissions/api/view-list', dataSrc: '' },
            destroy: true,
            columns: [
                { data: 'FullName' },
                {
                    data: 'ViewDepts',
                    render: d => d ? d.split(', ').map(v => `<span class="badge bg-info text-dark me-1">${v}</span>`).join('') : '<small class="text-muted">Chưa có quyền</small>'
                },
                {
                    data: 'ID',
                    render: id => `<button class="btn btn-sm btn-primary" onclick="PermissionModule.openModal(${id})"><i class="fas fa-edit"></i></button>`
                }
            ]
        });
    },

    // HÀM CHỌN TẤT CẢ CỰC NHANH
    selectAll: function () {
        const allIds = [];
        $('#viewDeptsSelect option').each(function () {
            const val = $(this).val();
            if (val) allIds.push(val); // Lấy hết ID trừ cái option trống đầu tiên
        });
        $('#viewDeptsSelect').val(allIds).trigger('change');
    },

    openModal: async function (empId) {
        $('#permEmpId').val(empId);

        // Load danh mục bộ phận (Nên load 1 lần duy nhất khi trang mở để NHANH)
        const resAllDepts = await fetch('/departments/api/all');
        const allDepts = await resAllDepts.json();

        let html = '<option></option>';
        allDepts.forEach(d => {
            html += `<option value="${d.DeptID}">${d.DeptName}</option>`;
        });
        $('#viewDeptsSelect').html(html);

        // Khởi tạo Select2
        $('#viewDeptsSelect').select2({
            theme: 'bootstrap-5',
            dropdownParent: $('#permModal'),
            width: '100%',
            placeholder: "-- Chọn bộ phận --",
            allowClear: true,      // Nút X để xóa sạch (Clear)
            closeOnSelect: false   // QUAN TRỌNG: Để menu không bị đóng khi click chọn
        });

        // Load quyền cũ
        const resUserRights = await fetch(`/permissions/api/view-rights/${empId}`);
        const selectedIds = await resUserRights.json();

        $('#viewDeptsSelect').val(selectedIds).trigger('change');
        $('#permModal').modal('show');
    },

    save: async function () {
        const payload = {
            employee_id: $('#permEmpId').val(),
            dept_ids: $('#viewDeptsSelect').val()
        };
        const res = await fetch('/permissions/api/save-view-rights', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            Swal.fire(t('save_success'), '', 'success');
            $('#permModal').modal('hide');
            this.loadTable();
        }
    }
};


