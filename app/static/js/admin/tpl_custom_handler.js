var TPL_CUSTOM = window.TPL_CUSTOM || {};
TPL_CUSTOM.tableId = '#tblTplCustom';
TPL_CUSTOM.apiBase = '/fo/templates';

TPL_CUSTOM.actions = {
    // 1. Khởi tạo CKEditor 4 thay vì bản 5
    initEditor: () => {
        const id = 'editor-ck';
        if (CKEDITOR.instances[id]) return; // Đã khởi tạo rồi thì bỏ qua

        CKEDITOR.replace(id, {
            // height: 500,
            // Thêm các plugin bạn đang có trong thư mục static
            extraPlugins: 'youtube,letterspacing,lineheight,textmatch,autolink,chart,loremipsum,ckawesome,slideshow,html5audio',

            // 1. Ép z-index của hộp thoại Editor cao hơn Modal (thường Modal là 1050)
            baseFloatZIndex: 10005,

            // 2. Mở khóa bộ lọc để gõ số xong nó không tự xóa style
            allowedContent: true,

            // Đường dẫn mới đến FastAPI Router
            filebrowserBrowseUrl: '/admin/ckeditor/browser',
            filebrowserUploadUrl: '/admin/ckeditor/upload',

            // Cấu hình quan trọng để FastAPI nhận diện đúng file
            filebrowserUploadMethod: 'form',
            filebrowserBrowseUrl: '/admin/ckeditor/browser',
            filebrowserUploadUrl: '/admin/ckeditor/upload',
            filebrowserWindowWidth: '900',
            filebrowserWindowHeight: '700',

            // Chỉnh lại kích thước cửa sổ Browse Server cho điện thoại process...
           
        });
    },

    load: () => {
        // ... (Giữ nguyên logic DataTable của bạn)
    },

    openModal: (id) => {
        $('#modalCustom').modal('show');

        // Khởi tạo Editor ngay khi mở modal
        TPL_CUSTOM.actions.initEditor();

        if (!id) {
            $('#cust_code, #cust_name').val('');
            if (CKEDITOR.instances['editor-ck']) CKEDITOR.instances['editor-ck'].setData('');
        } else {
            $.get(`${TPL_CUSTOM.apiBase}/detail/${id}`, (res) => {
                $('#cust_code').val(res.TemplateCode);
                $('#cust_name').val(res.TemplateName);
                if (CKEDITOR.instances['editor-ck']) {
                    CKEDITOR.instances['editor-ck'].setData(res.HtmlContent || '');
                }
            });
        }
    },

    save: () => {
        // Lấy dữ liệu từ CKEditor 4
        const html = CKEDITOR.instances['editor-ck'] ? CKEDITOR.instances['editor-ck'].getData() : '';
        const payload = {
            TemplateCode: $('#cust_code').val(),
            TemplateName: $('#cust_name').val(),
            HtmlContent: html,
            IsCustom: 1
        };
        $.ajax({
            url: `${TPL_CUSTOM.apiBase}/save`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(payload),
            success: () => {
                alert("Đã lưu thiết kế!");
                $('#modalCustom').modal('hide');
                TPL_CUSTOM.actions.load();
            }
        });
    }
};

// Đảm bảo Editor focus khi modal mở
$('#modalCustom').on('shown.bs.modal', function () {
    TPL_CUSTOM.actions.initEditor();
});
