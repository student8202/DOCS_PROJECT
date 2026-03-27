// Đảm bảo đối tượng cha và đối tượng config luôn tồn tại
var TPL_SYS = window.TPL_SYS || {};

TPL_SYS.config = {
    tableId: '#tblTplSystem',
    apiBase: '/fo/templates',
    editorContainer: 'container-monaco',
    monacoInstance: null, // Tên biến tường minh theo ý bạn
    currentId: null
};
// --- 2. PHỤ TRỢ (UI HELPERS) ---
TPL_SYS.helpers = {
    // 1. Kiểm tra Mã hệ thống (Chỉ cho phép CHỮ HOA, SỐ và GẠCH DƯỚI)
    isValidSysCode: function (code) {
        const regex = /^[a-zA-Z0-9_]+$/;
        return regex.test(code);
    },

    // 2. Kiểm tra đường dẫn file (Phải có đuôi .html hoặc .jinja2)
    isValidPath: function (path) {
        if (!path) return false;
        const validExtensions = ['.html', '.jinja2', '.htm'];
        return validExtensions.some(ext => path.toLowerCase().endsWith(ext));
    },

    // 3. Làm sạch mã hệ thống
    sanitizeSysCode: function (str) {
        if (!str) return "";
        return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
            .replace(/[^a-zA-Z0-9_]/g, '')
            .toUpperCase().trim();
    }
};

TPL_SYS.actions = {
    init: () => {
        // 1. Kiểm tra xem loader đã tồn tại chưa để tránh Uncaught SyntaxError
        if (typeof require === 'undefined') {
            const loaderScript = document.createElement('script');
            loaderScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.46.0/min/vs/loader.min.js';
            loaderScript.onload = () => TPL_SYS.actions.setupMonaco();
            document.head.appendChild(loaderScript);
        } else {
            // Nếu require đã có sẵn, thiết lập luôn
            TPL_SYS.actions.setupMonaco();
        }
    },

    setupMonaco: () => {
        // Cấu hình Monaco (Trỏ đến thư mục /min/vs thay vì file js)
        require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.46.0/min/vs' } });

        require(['vs/editor/editor.main'], function () {
            // Tránh khởi tạo đè nếu đã có instance
            if (!TPL_SYS.config.monacoInstance) {
                TPL_SYS.config.monacoInstance = monaco.editor.create(document.getElementById('container-monaco'), {
                    value: '',
                    language: 'html',
                    theme: 'vs-dark',
                    automaticLayout: true
                });
                console.log("✅ Monaco Editor đã sẵn sàng!");
            }
        });
    },
    load: () => {
        // 1. Kiểm tra xem bảng đã tồn tại chưa để tránh lỗi re-initialize
        if ($.fn.DataTable.isDataTable(TPL_SYS.config.tableId)) {
            $(TPL_SYS.config.tableId).DataTable().ajax.reload();
            return;
        }

        // 2. Nạp dữ liệu vào Table
        TPL_SYS.instance = $(TPL_SYS.config.tableId).DataTable({
            ajax: { url: `${TPL_SYS.config.apiBase}/list?is_custom=0`, dataSrc: '' },
            columns: [
                { data: 'TemplateID' }, // 1
                { data: 'ModuleName' }, // 2
                { data: 'SubModule' },  // 3
                { data: 'TemplateCode' }, // 4
                { data: 'TemplateName' }, // 5
                { data: 'FilePath', render: d => `<code class="small text-muted">${d || ''}</code>` }, // 6
                 // Hiển thị trạng thái Active
                {
                    data: 'IsActive',
                    render: d => d ? '<span class="text-success"><i class="fas fa-check-circle"></i> dùng</span>'
                        : '<span class="text-muted"><i class="fas fa-times-circle"></i> ngưng</span>'
                },
                {
                    data: 'TemplateID', // 7
                    className: 'text-center',
                    render: d => `<button class="btn btn-sm btn-outline-danger py-0" onclick="TPL_SYS.actions.openModal(${d})"><i class="fas fa-code"></i> Sửa Code</button>`
                }
            ]
        });
    },
    openModal: (id) => {
        // 1. Kiểm tra nếu Editor chưa sẵn sàng
        if (!TPL_SYS.config.monacoInstance) {
            alert("Trình soạn thảo Code đang được tải, vui lòng thử lại sau 1 giây!");
            return;
        }
        if (!id) {
            // THÊM MỚI
            $('#tpl_sys_id').val(''); // Xóa ID cũ
            $('#sys_code, #sys_name').val('');
            // Gán mặc định đường dẫn vào ô input
            $('#sys_path').val('');
            TPL_SYS.config.monacoInstance.setValue('<!-- New System Template -->');
            $('#modalSystem').modal('show');
        }

        else {
            // cập nhật
            $.get(`${TPL_SYS.config.apiBase}/system-detail/${id}`, (res) => {
                $('#tpl_sys_id').val(res.TemplateID);
                $('#sys_code').val(res.TemplateCode);
                $('#sys_name').val(res.TemplateName);
                $('#sys_path').val(res.FilePath || '');
                $('#sys_category').val(res.Category);
                $('#sys_active').val(res.IsActive ? "1" : "0");

                // Gán nội dung code vào Editor
                TPL_SYS.config.monacoInstance.setValue(res.HtmlContent || '');

                $('#modalSystem').modal('show');
            });
        }
    },
    preview: () => {
        if (!TPL_SYS.config.monacoInstance) return;

        const code = TPL_SYS.config.monacoInstance.getValue();
        if (!code) {
            Swal.fire("Code trống", "Vui lòng nhập mã nguồn trước khi xem!", "warning");
            return;
        }

        // Tạo cửa sổ preview mới
        const win = window.open('', '_blank');

        // Mock data để bạn thấy vị trí các biến nhảy ra sao
        let renderedCode = code
            .replace(/{{ LastName }}/g, "PHẠM")
            .replace(/{{ FirstName }}/g, "THỊ MỸ HẠNH")
            .replace(/{{ FRoomCode }}/g, "101")
            .replace(/{{ ArrivalDate }}/g, "19/03/2026")
            .replace(/{{ DepartureDate }}/g, "20/03/2026")
            .replace(/{{ FolioNum }}/g, "123456")
            .replace(/{{ SignatureData }}/g, "https://via.placeholder.com");

        win.document.write(renderedCode);
        win.document.close();
    },

    save: () => {
        // const data = {
        //     TemplateCode: $('#sys_code').val(),
        //     TemplateName: $('#sys_name').val(),
        //     FilePath: $('#sys_path').val(),
        //     HtmlContent: TPL_SYS.config.monacoInstance.getValue()
        // };
        // // AJAX POST về server lưu vào db...
        // console.log("Saving data...", data);
        // Xóa vết đỏ cũ
        $('.form-control').removeClass('is-invalid');
        // Kiểm tra "gác cổng"
        if (!TPL_SYS.config.monacoInstance) {
            Swal.fire("Lỗi", "Trình soạn thảo Monaco chưa khởi tạo xong!", "error");
            return;
        }

        // Lấy nội dung code từ monacoInstance
        const content = TPL_SYS.config.monacoInstance.getValue();

        const codeInput = $('#sys_code');
        const nameInput = $('#sys_name');
        const pathInput = $('#sys_path');
        const cateInput = $('#sys_category');

        const code = TPL_SYS.helpers.sanitizeSysCode(codeInput.val());
        const cate = cateInput.val();
        const name = nameInput.val().trim();
        const path = pathInput.val().trim();

        // VALIDATE CATEGORY (BẮT LỖI Ở ĐÂY)
        if (!cate || cate === "" || cate === null) {
            cateInput.addClass('is-invalid').focus();
            Swal.fire('Lỗi Phân loại', 'Vui lòng chọn loại template (Category)!', 'error');
            return;
        }
        // 1. Validate MÃ HỆ THỐNG
        if (code.length < 3 || !TPL_SYS.helpers.isValidSysCode(code)) {
            codeInput.addClass('is-invalid').focus();
            Swal.fire("Lỗi Mã", "Mã hệ thống phải từ 3 ký tự (A-Z, 0-9, _)", "error");
            return;
        }

        // 2. Validate TÊN MẪU
        if (name.length < 5) {
            nameInput.addClass('is-invalid').focus();
            Swal.fire("Lỗi Tên", "Tên mẫu hệ thống phải rõ nghĩa (ít nhất 5 ký tự)", "error");
            return;
        }

        // 3. Validate ĐƯỜNG DẪN FILE (PATH) - CỰC KỲ QUAN TRỌNG CHO DEV
        if (!TPL_SYS.helpers.isValidPath(path)) {
            pathInput.addClass('is-invalid').focus();
            Swal.fire("Lỗi Path", "Đường dẫn file phải kết thúc bằng .html hoặc .jinja2", "error");
            return;
        }

        // 4. Validate NỘI DUNG CODE
        if (!content || content.length < 10) {
            Swal.fire("Code trống", "Vui lòng nhập mã nguồn trước khi lưu!", "warning");
            return;
        }

        // Gán lại mã sạch vào giao diện
        codeInput.val(code);
        // (Lấy từ input ẩn đã có data):
        const currentId = $('#tpl_sys_id').val();
        const payload = {
            TemplateID: currentId ? parseInt(currentId) : 0,
            TemplateCode: code,
            TemplateName: name,
            ModuleName: $('#sys_module').val(),
            SubModule: $('#sys_sub').val(),
            Category: $('#sys_category').val(),
            FilePath: path,
            HtmlContent: content,
            IsCustom: 0
        };

        // Gọi Ajax lưu (Ghi file vật lý)
        $.ajax({
            url: TPL_SYS.config.apiBase + '/save-system',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(payload),
            success: function (res) {
                Swal.fire("Thành công", "Đã ghi file hệ thống!", "success");
                $('#modalSystem').modal('hide');
                TPL_SYS.actions.load();
            },
            error: function (err) {
                Swal.fire("Lỗi Ghi File", err.responseJSON?.detail || "Kiểm tra lại quyền truy cập file trên Server", "error");
            }
        });
    }
    // save: () => { /* Logic AJAX POST như cũ, IsCustom: 0 */ }
};
$(document).ready(() => {
    TPL_SYS.actions.init();
    TPL_SYS.actions.load();

    // Tự động làm sạch mã khi Dev rời khỏi ô nhập
    $(document).on('blur', '#sys_code', function () {
        $(this).val(TPL_SYS.helpers.sanitizeSysCode($(this).val()));
    });

    $(document).on('input', '.is-invalid', function () {
        $(this).removeClass('is-invalid');
    });
});
