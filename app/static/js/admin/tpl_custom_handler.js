var TPL_CUSTOM = window.TPL_CUSTOM || {};

// --- 1. CẤU HÌNH (CONFIG) ---
TPL_CUSTOM.config = {
    tableId: '#tblTplCustom',
    apiBase: '/fo/templates',
    editorId: 'editor-ck' // Phải có dòng này
};

// --- 2. PHỤ TRỢ (UI HELPERS) ---
TPL_CUSTOM.helpers = {
    insertTag: function (tag) {
        // Sử dụng trực tiếp ID từ config để tránh undefined
        var oEditor = CKEDITOR.instances[TPL_CUSTOM.config.editorId];
        if (oEditor && oEditor.mode === 'wysiwyg') {
            oEditor.focus(); // Ép editor nhận focus trước khi chèn
            oEditor.insertText(tag);
        } else {
            alert("Vui lòng click vào vùng soạn thảo trước!");
        }
    },

    filterTagsByModule: function (module) {
        $('.tag-group').hide();
        $(`.tag-group[data-module="${module}"]`).show();
    },
    // 1. Kiểm tra tính hợp lệ: Chỉ cho phép Chữ cái không dấu, Số và Gạch dưới
    isValidCode: function (code) {
        const regex = /^[a-zA-Z0-9_]+$/;
        return regex.test(code);
    },
    // Chỉ làm sạch Mã (Code)
    sanitizeCode: function (str) {
        if (!str) return "";
        return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
            .replace(/[^a-zA-Z0-9_]/g, '')
            .toUpperCase();
    },

    // Làm sạch Tên (Name): Giữ nguyên Tiếng Việt, chỉ bỏ khoảng trắng thừa
    sanitizeName: function (str) {
        if (!str) return "";
        return str.trim().replace(/\s+/g, ' '); // "  Chào   Bạn  " -> "Chào Bạn"
    }
};

// --- 3. HÀNH ĐỘNG (ACTIONS) ---
TPL_CUSTOM.actions = {
    initEditor: () => {
        const id = TPL_CUSTOM.config.editorId;
        if (CKEDITOR.instances[id]) return;

        CKEDITOR.replace(id, {
            extraPlugins: 'youtube,letterspacing,lineheight,textmatch,autolink,chart,loremipsum,ckawesome,slideshow,html5audio',
            baseFloatZIndex: 10005,
            allowedContent: true,
            filebrowserBrowseUrl: '/admin/ckeditor/browser',
            filebrowserUploadUrl: '/admin/ckeditor/upload',
            filebrowserUploadMethod: 'form',
            filebrowserWindowWidth: '900',
            filebrowserWindowHeight: '700'
        });
    },

    loadTable: function () {
        if ($.fn.DataTable.isDataTable(TPL_CUSTOM.config.tableId)) {
            $(TPL_CUSTOM.config.tableId).DataTable().ajax.reload(null, false);
            return;
        }

        $(TPL_CUSTOM.config.tableId).DataTable({
            ajax: { url: TPL_CUSTOM.config.apiBase + '/list', dataSrc: '' },
            columns: [
                { data: 'TemplateID' },
                // Hiển thị Module (FO, POS...) với màu sắc khác nhau cho dễ nhìn
                {
                    data: 'ModuleName',
                    render: d => {
                        let cls = d === 'FO' ? 'bg-success' : (d === 'POS' ? 'bg-primary' : 'bg-info');
                        return `<span class="badge ${cls}">${d}</span>`;
                    }
                },
                { data: 'SubModule', render: d => `<small class="fw-bold">${d}</small>` },
                {
                    data: 'Category',
                    render: d => `<span class="text-dark"><i class="fas fa-folder-open me-1 text-warning"></i>${d || ''}</span>`
                },
                { data: 'TemplateCode', render: d => `<code class="text-danger">${d}</code>` },
                { data: 'TemplateName' },
                // Hiển thị trạng thái Active
                {
                    data: 'IsActive',
                    render: d => d ? '<span class="text-success"><i class="fas fa-check-circle"></i> dùng</span>'
                        : '<span class="text-muted"><i class="fas fa-times-circle"></i> ngưng</span>'
                },
                { data: 'CreatedBy', render: d => `<small>${d || ''}</small>` },
                {
                    data: 'TemplateID',
                    render: d => `<button class="btn btn-sm btn-outline-success py-0" onclick="TPL_CUSTOM.actions.openModal(${d})"><i class="fas fa-edit"></i> Sửa</button>`
                }
            ],
            order: [[0, 'desc']], // Mẫu mới nhất lên đầu
            // language: { url: "//cdn.datatables.net/plug-ins/1.10.24/i18n/Vietnamese.json" }
        });
    },

    openModal: (id) => {
        // 1. Hiện Modal trước
        $('#modalCustom').modal('show');

        // 2. Khởi tạo Editor (nếu chưa có)
        TPL_CUSTOM.actions.initEditor();

        if (!id) {
            // TRƯỜNG HỢP THÊM MỚI: Reset sạch form
            $('#tpl_id, #cust_code, #cust_name').val('');
            $('#sel_module').val('FO').trigger('change');
            $('#sel_sub').val('RESERVATION');
            $('#sel_category').val('REG_CARD');
            $('#sel_active').val('1');

            if (CKEDITOR.instances[TPL_CUSTOM.config.editorId]) {
                CKEDITOR.instances[TPL_CUSTOM.config.editorId].setData('');
            }
        } else {
            // TRƯỜNG HỢP CHỈNH SỬA: Lấy dữ liệu từ API
            $.get(`${TPL_CUSTOM.config.apiBase}/detail/${id}`, function (res) {
                // LƯU Ý: 'res' phải khớp chính xác với Key trong SQL/Schema trả về
                $('#tpl_id').val(res.TemplateID);
                $('#cust_code').val(res.TemplateCode);
                $('#cust_name').val(res.TemplateName);

                // Đổ dữ liệu vào các ô Select và Trigger Change để Helper nhận diện
                $('#sel_module').val(res.ModuleName).trigger('change');
                $('#sel_sub').val(res.SubModule);
                $('#sel_category').val(res.Category);

                // Xử lý IsActive (Boolean -> String "1"/"0")
                $('#sel_active').val(res.IsActive ? "1" : "0");

                // Đổ nội dung vào CKEditor
                if (CKEDITOR.instances[TPL_CUSTOM.config.editorId]) {
                    // Sử dụng setData để nạp mã HTML từ Database vào vùng soạn thảo
                    CKEDITOR.instances[TPL_CUSTOM.config.editorId].setData(res.HtmlContent || '');
                }
            }).fail(function () {
                Swal.fire("Lỗi", "Không thể tải dữ liệu chi tiết mẫu!", "error");
            });
        }
    },
    loadTags: function () {
        const apiBase = TPL_CUSTOM.config ? TPL_CUSTOM.config.apiBase : TPL_CUSTOM.apiBase;

        $.get(apiBase + '/tags', function (res) {
            let html = '';

            // 1. Phân nhóm Tags theo ModuleName
            const grouped = res.reduce((acc, obj) => {
                const key = obj.ModuleName;
                if (!acc[key]) acc[key] = [];
                acc[key].push(obj);
                return acc;
            }, {});

            // 2. Duyệt qua từng nhóm để tạo HTML danh sách nút bấm
            for (let module in grouped) {
                let badgeClass = module === 'FO' ? 'bg-success' : (module === 'POS' ? 'bg-primary' : 'bg-info');
                html += `
                <div class="tag-group mb-3" data-module="${module}">
                    <div class="badge ${badgeClass} w-100 mb-2 text-start px-2 py-1">${module}</div>
                    <div class="list-group">
            `;
                grouped[module].forEach(tag => {
                    html += `
                    <button class="list-group-item list-group-item-action p-2 small border-0 shadow-sm mb-1 rounded" 
                        onclick="TPL_CUSTOM.helpers.insertTag('${tag.TagCode}')">
                        <i class="fas fa-plus-circle text-muted me-1 small"></i> ${tag.TagName}
                    </button>
                `;
                });
                html += `</div></div>`;
            }

            // 3. Đổ HTML vào vùng chứa Tags
            $('#list-tags').html(html);

            // 4. Lọc theo Module hiện tại đang chọn ở ô select
            TPL_CUSTOM.helpers.filterTagsByModule($('#sel_module').val());
        });
    },
    save: () => {
        // Lấy dữ liệu và làm sạch sơ bộ
        // 1. Lấy instance của Editor dựa trên ID đã cấu hình
        // Bước 1: Xác định ID (Thử cả 2 cách để chắc chắn không chết)
        const id = TPL_CUSTOM.config ? TPL_CUSTOM.config.editorId : TPL_CUSTOM.editorId;

        // Bước 2: Lấy đối tượng Editor
        const oEditor = CKEDITOR.instances[id];

        // Bước 3: Lấy dữ liệu
        const html = oEditor ? oEditor.getData() : '';
        // Xóa sạch các vết đỏ (error) cũ trước khi kiểm tra mới
        $('.form-control').removeClass('is-invalid');
        $('.form-control, .form-select').removeClass('is-invalid');

        const codeInput = $('#cust_code');
        const nameInput = $('#cust_name');
        const cateInput = $('#sel_category'); // Ô chọn Category

        const code = TPL_CUSTOM.helpers.sanitizeCode(codeInput.val());
        const cate = cateInput.val();
        const name = nameInput.val().trim();
        codeInput.val(code);

        // ALIDATE CATEGORY (BẮT LỖI Ở ĐÂY)
        if (!cate || cate === "" || cate === null) {
            cateInput.addClass('is-invalid').focus();
            Swal.fire('Lỗi Phân loại', 'Vui lòng chọn loại template (Category)!', 'error');
            return;
        }
        // --- VALIDATE MÃ MẪU ---
        if (code.length < 2 || !TPL_CUSTOM.helpers.isValidCode(code)) {
            codeInput.addClass('is-invalid'); // Đổi khung thành màu đỏ
            codeInput.focus();                // Tự động nhảy con trỏ vào ô lỗi
            Swal.fire({
                icon: 'error',
                title: 'Lỗi Mã mẫu',
                text: 'Mã không được trống và chỉ chứa chữ IN HOA, số, dấu gạch dưới (_)',
                confirmButtonText: 'Để tôi sửa lại'
            });
            return;
        }

        // --- VALIDATE TÊN MẪU ---
        if (name.length < 5) {
            nameInput.addClass('is-invalid'); // Đổi khung thành màu đỏ
            nameInput.focus();
            Swal.fire({
                icon: 'error',
                title: 'Lỗi Tên mẫu',
                text: 'Vui lòng nhập tên hiển thị rõ nghĩa (ít nhất 5 ký tự)',
                confirmButtonText: 'OK'
            });
            return;
        }

        // --- VALIDATE NỘI DUNG EDITOR ---
        if (!html || html.length < 20) {
            Swal.fire('Nội dung trống', 'Bạn chưa thiết kế gì cho mẫu này!', 'warning');
            return;
        }


        const payload = {
            TemplateID: $('#tpl_id').val() || null,
            TemplateCode: $('#cust_code').val(),
            TemplateName: $('#cust_name').val(),
            ModuleName: $('#sel_module').val(),
            SubModule: $('#sel_sub').val(),

            // BẮT BUỘC PHẢI THÊM DÒNG NÀY VÀO PAYLOAD
            Category: $('#sel_category').val() || "OTHER",

            IsActive: $('#sel_active').val() === "1",
            HtmlContent: CKEDITOR.instances[TPL_CUSTOM.config.editorId].getData(),
            IsCustom: 1,
            Username: "Admin"
        };
        $.ajax({
            url: `${TPL_CUSTOM.config.apiBase}/save`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(payload),
            success: function (res) {
                // Trường hợp lưu thành công (HTTP 200)
                Swal.fire("Thành công", "Mẫu đã được lưu vào hệ thống!", "success");
                $('#modalCustom').modal('hide');
                TPL_CUSTOM.actions.loadTable();
            },
            error: function (err) {
                // TRƯỜNG HỢP LỖI (HTTP 400, 500...)
                // Lấy thông tin lỗi từ Backend trả về trong "detail"
                const errorMsg = err.responseJSON && err.responseJSON.detail
                    ? err.responseJSON.detail
                    : "Lỗi không xác định từ máy chủ";

                // Nếu lỗi là trùng mã, ta focus lại vào ô mã và đổi màu đỏ
                if (errorMsg.includes("Mã mẫu")) {
                    $('#cust_code').addClass('is-invalid').focus();
                }

                Swal.fire({
                    icon: 'error',
                    title: 'Không thể lưu',
                    text: errorMsg, // Hiển thị: "Mã mẫu 'REGCARD' đã tồn tại."
                    confirmButtonColor: '#d33'
                });
            }
        });
    }
};

// --- 4. SỰ KIỆN (EVENTS) ---
$(document).ready(() => {
    TPL_CUSTOM.actions.loadTable();
    TPL_CUSTOM.actions.loadTags();

    $('#sel_module').on('change', function () {
        TPL_CUSTOM.helpers.filterTagsByModule($(this).val());
    });

    $('#modalCustom').on('shown.bs.modal', function () {
        TPL_CUSTOM.actions.initEditor();
    });

    // --- 4. SỰ KIỆN (EVENTS) ---
    $(document).on('blur', '#cust_code', function () {
        $(this).val(TPL_CUSTOM.helpers.sanitizeCode($(this).val()));
    });

    $(document).on('blur', '#cust_name', function () {
        $(this).val(TPL_CUSTOM.helpers.sanitizeName($(this).val()));
    });
});
