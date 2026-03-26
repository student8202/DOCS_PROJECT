var SIGN = window.SIGN || {};

// --- 1. CẤU HÌNH (CONFIG) ---
SIGN.config = {
    apiBase: '/api/v1/queue',
    padInstance: null,
    currentRole: null // 'guest' hoặc 'reception'
};

// --- 2. PHỤ TRỢ (HELPERS) ---
SIGN.helpers = {
    initPad: function () {
        const canvas = document.getElementById('signature-pad-canvas');
        if (!canvas) return;

        // Reset lại kích thước canvas để không bị méo nét ký trên iPad
        const ratio = Math.max(window.devicePixelRatio || 1, 1);
        canvas.width = canvas.offsetWidth * ratio;
        canvas.height = canvas.offsetHeight * ratio;
        canvas.getContext("2d").scale(ratio, ratio);

        // Khởi tạo hoặc xóa cũ tạo mới nếu đã tồn tại
        if (SIGN.config.padInstance) {
            SIGN.config.padInstance.clear();
        } else {
            SIGN.config.padInstance = new SignaturePad(canvas, {
                backgroundColor: 'rgba(255, 255, 255, 0)', // Nền trong suốt để không đè chữ trên giấy
                penColor: 'rgb(0, 0, 128)' // Màu mực xanh truyền thống
            });
        }
    }
};

// --- 3. HÀNH ĐỘNG (ACTIONS) ---
SIGN.actions = {
    // Nạp hồ sơ từ Queue
    loadData: function () {
        const qid = $('#queue_id').val();
        $.get(`${SIGN.config.apiBase}/get-content/${qid}`, function (res) {
            if (res && res.Html) {
                $('#rendered-content').html(res.Html);
                $('#info-ref').text(`Hồ sơ: ${res.RefID}`);
            }
        });
    },

    // Mở khung ký (Khi click vào vùng {{GuestSignatureImg}} trên tờ giấy)
    openPad: function (role) {
        SIGN.config.currentRole = role;
        const title = role === 'guest' ? "KHÁCH HÀNG KÝ TÊN" : "LỄ TÂN XÁC NHẬN";
        $('#pad-title').text(title);

        $('#modal-pad').css('display', 'flex').fadeIn(200);

        // Quan trọng: Phải initPad sau khi Modal hiện ra thì mới lấy được chiều rộng canvas
        setTimeout(() => { SIGN.helpers.initPad(); }, 100);
    },

    closePad: function () {
        $('#modal-pad').fadeOut(200);
    },

    clear: function () {
        SIGN.config.padInstance.clear();
    },

    // BƯỚC 1: Lưu chữ ký từ Pad "nhảy" vào tờ giấy (Lưu tạm Client-side)
    saveToDoc: function () {
        if (SIGN.config.padInstance.isEmpty()) {
            Swal.fire("Lưu ý", "Vui lòng ký tên vào khung trắng!", "warning");
            return;
        }

        const signatureBase64 = SIGN.config.padInstance.toDataURL();
        const role = SIGN.config.currentRole;

        // Tìm đúng ID ảnh mà Service đã cấy vào để "đập" ảnh vào đó
        const targetImg = (role === 'guest') ? $('#img-guest-sig') : $('#img-recep-sig');

        if (targetImg.length > 0) {
            targetImg.attr('src', signatureBase64).show();
            // Ẩn dòng chữ "Touch to sign" nếu có
            targetImg.siblings('.placeholder-text').hide();
        }

        this.closePad();
    },

    // BƯỚC 2: Nhấn nút Hoàn tất ở dưới cùng để gửi toàn bộ về Server
    finalSubmit: function () {
        const guestSig = $('#img-guest-sig').attr('src');
        const recepSig = $('#img-recep-sig').attr('src');
        const qid = $('#queue_id').val();

        if (!guestSig || guestSig === "") {
            Swal.fire("Chưa ký", "Khách hàng vui lòng ký tên trước khi hoàn tất!", "error");
            return;
        }

        Swal.fire({
            title: 'Xác nhận hoàn tất?',
            text: "Hồ sơ sẽ được lưu vĩnh viễn kèm chữ ký.",
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Đồng ý',
            cancelButtonText: 'Hủy'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `${SIGN.config.apiBase}/complete`,
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        QueueID: parseInt(qid),
                        Guest_Signature: guestSig,
                        Reception_Signature: recepSig
                    }),
                    success: function () {
                        Swal.fire("Thành công", "Hồ sơ đã được lưu trữ!", "success")
                            .then(() => { window.location.href = '/sign/waiting'; });
                    },
                    error: function () {
                        Swal.fire("Lỗi", "Không thể lưu hồ sơ, vui lòng thử lại.", "error");
                    }
                });
            }
        });
    }
};

// --- 4. SỰ KIỆN (EVENTS) ---
$(document).ready(function () {
    SIGN.actions.loadData();
});
