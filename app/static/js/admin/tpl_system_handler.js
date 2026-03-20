let monacoInstance = null;
const TPL_SYS = {
    tableId: '#tblTplSystem',
    apiBase: '/fo/templates'
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
        
        TPL_SYS.actions.load();
    },

    setupMonaco: () => {
        // Cấu hình Monaco (Trỏ đến thư mục /min/vs thay vì file js)
        require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.46.0/min/vs' } });
        
        require(['vs/editor/editor.main'], function () {
            // Tránh khởi tạo đè nếu đã có instance
            if (!monacoInstance) {
                monacoInstance = monaco.editor.create(document.getElementById('container-monaco'), {
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
        TPL_SYS.instance = $(TPL_SYS.tableId).DataTable({
            ajax: { url: `${TPL_SYS.apiBase}/list?is_custom=0`, dataSrc: '' },
            columns: [
                { data: 'TemplateID' },
                { data: 'TemplateCode', render: d => `<span class="badge bg-danger">${d}</span>` },
                { data: 'TemplateName' },
                { data: 'FilePath', className: 'font-monospace small' },
                { data: 'TemplateID', render: d => `<button class="btn btn-sm btn-outline-danger py-0" onclick="TPL_SYS.actions.openModal(${d})">Code</button>` }
            ]
        });
    },
    openModal: (id) => {
        // 1. Kiểm tra nếu Editor chưa sẵn sàng
        if (!monacoInstance) {
            alert("Trình soạn thảo Code đang được tải, vui lòng thử lại sau 1 giây!");
            return;
        }

        if (!id) {
            $('#sys_code, #sys_name, #sys_path').val('');
            monacoInstance.setValue(''); // Bây giờ đã an toàn để gọi
            $('#modalSystem').modal('show');
        }
        else {
            $.get(`${TPL_SYS.apiBase}/detail/${id}`, (res) => {
                $('#sys_code').val(res.TemplateCode);
                $('#sys_name').val(res.TemplateName);
                $('#sys_path').val(res.FilePath || '');

                // Gán nội dung code vào Editor
                monacoInstance.setValue(res.HtmlContent || '');

                $('#modalSystem').modal('show');
            });
        }
    },
    preview: () => {
        if (!monacoInstance) return;
        
        const code = monacoInstance.getValue();
        if (!code) {
            alert("Vui lòng nhập code trước khi xem!");
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
        const data = {
            TemplateCode: $('#sys_code').val(),
            TemplateName: $('#sys_name').val(),
            FilePath: $('#sys_path').val(),
            HtmlContent: monacoInstance.getValue()
        };
        // AJAX POST về server lưu vào db...
        console.log("Saving data...", data);
    }
    // save: () => { /* Logic AJAX POST như cũ, IsCustom: 0 */ }
};
$(document).ready(() => TPL_SYS.actions.init());
