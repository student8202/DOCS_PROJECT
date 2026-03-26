var SIGN = window.SIGN || {};

// --- 1. CONFIG ---
SIGN.config = {
    apiBase: '/api/v1/queue',
    padInstance: null
};

// --- 2. HELPERS ---
SIGN.helpers = {
    initPad: function() {
        const canvas = document.getElementById('signature-pad');
        // Điều chỉnh kích thước canvas cho khớp với khung hiển thị
        const ratio = Math.max(window.devicePixelRatio || 1, 1);
        canvas.width = canvas.offsetWidth * ratio;
        canvas.height = canvas.offsetHeight * ratio;
        canvas.getContext("2d").scale(ratio, ratio);

        SIGN.config.padInstance = new SignaturePad(canvas, {
            backgroundColor: 'rgb(255, 255, 255)',
            penColor: 'rgb(0, 0, 0)'
        });
    }
};

// --- 3. ACTIONS ---
SIGN.actions = {
    // Lấy nội dung hồ sơ đã trộn sẵn từ QueueID
    loadData: function() {
        const qid = $('#queue_id').val();
        $.get(`${SIGN.config.apiBase}/get-content/${qid}`, function(res) {
            if (res && res.Html) {
                $('#rendered-content').html(res.Html);
                $('#info-ref').text(`Mã: ${res.RefID}`);
            }
        });
    },

    clear: function() {
        SIGN.config.padInstance.clear();
    },

    submit: function() {
        if (SIGN.config.padInstance.isEmpty()) {
            Swal.fire("Thông báo", "Vui lòng ký tên trước khi xác nhận!", "warning");
            return;
        }

        const base64 = SIGN.config.padInstance.toDataURL(); // Xuất ảnh chữ ký
        const qid = $('#queue_id').val();

        Swal.fire({
            title: 'Xác nhận?',
            text: "Chữ ký của bạn sẽ được lưu chính thức vào hồ sơ.",
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Đồng ý',
            cancelButtonText: 'Kiểm tra lại'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `${SIGN.config.apiBase}/complete`,
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        QueueID: parseInt(qid),
                        Signature_Base64: base64
                    }),
                    success: function() {
                        Swal.fire("Thành công", "Hồ sơ đã được ký và gửi đi!", "success")
                            .then(() => { window.location.href = '/sign/waiting'; });
                    }
                });
            }
        });
    }
};

// --- 4. EVENTS ---
$(document).ready(function() {
    SIGN.helpers.initPad();
    SIGN.actions.loadData();
});
