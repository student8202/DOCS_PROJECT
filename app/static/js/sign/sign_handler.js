var SIGN = window.SIGN || {};

// --- 1. CẤU HÌNH (CONFIG) ---
SIGN.config = {
    apiBase: '/api/v1/queue',
    deviceApi: '/api/v1/devices', // Thêm đường dẫn API thiết bị
    padInstance: null,
    currentRole: null, // 'guest' hoặc 'reception'
    timerHeartbeat: null // Biến quản lý vòng lặp
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
    },
    getFullConnectionID: function () {
        let browserId = localStorage.getItem('device_browser_uuid');
        let tabId = sessionStorage.getItem('device_tab_id');
        return browserId + "|" + tabId;
    },
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

        if (!guestSig || guestSig === "" || guestSig.length < 100) {
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
                // --- BƯỚC 1: HIỆN LOADING ĐỂ THÔNG NÒNG CẢM GIÁC CHỜ ĐỢI ---
                Swal.fire({
                    title: 'Đang xử lý...',
                    html: 'Hệ thống đang đóng gói hồ sơ PDF, vui lòng đợi trong giây lát.',
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading(); // Hiện icon xoay
                    }
                });

                // --- BƯỚC 2: GỬI DỮ LIỆU ---
                $.ajax({
                    url: `${SIGN.config.apiBase}/complete`,
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        QueueID: parseInt(qid),
                        Guest_Signature: guestSig,
                        Reception_Signature: recepSig
                    }),
                    success: function (res) {
                        // Tắt loading và báo thành công
                        Swal.fire({
                            icon: 'success',
                            title: 'Thành công',
                            text: 'Hồ sơ đã được lưu trữ!',
                            timer: 2000,
                            showConfirmButton: false
                        }).then(() => {
                            window.location.href = '/sign/waiting';
                        });
                    },
                    error: function (err) {
                        // Tắt loading và báo lỗi chi tiết từ Server
                        const msg = err.responseJSON?.detail || "Không thể lưu hồ sơ, vui lòng thử lại.";
                        Swal.fire("Lỗi hệ thống", msg, "error");
                    }
                });
            }
        });
    },
    // --- HÀM MỚI: HEARTBEAT KIỂM TRA QUYỀN ---
    heartbeat: function () {
        const deviceId = localStorage.getItem('current_device_id');
        const fullConnId = SIGN.helpers.getFullConnectionID();

        if (!deviceId) return;

        $.ajax({
            url: SIGN.config.deviceApi + '/ping',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ DeviceID: deviceId, ConnectionID: fullConnId }),
            success: function (res) {
                if (res.status === 'conflict') {
                    // PHÁT HIỆN CHIẾM QUYỀN: Khóa nút hoàn tất ngay lập tức
                    $('#btn-final-submit').prop('disabled', true).addClass('btn-secondary').removeClass('btn-danger');

                    clearInterval(SIGN.config.timerHeartbeat); // Dừng ping

                    // 3. Hiện thông báo có nút điều hướng
                    Swal.fire({
                        title: "Mất kết nối quầy!",
                        text: "Thiết bị này đã bị thay thế hoặc mất quyền điều khiển. Bạn muốn làm gì?",
                        icon: "warning",
                        showCancelButton: true,
                        confirmButtonText: '<i class="fas fa-sync"></i> Thử kết nối lại',
                        cancelButtonText: '<i class="fas fa-home"></i> Về màn hình chờ',
                        confirmButtonColor: '#28a745',
                        cancelButtonColor: '#6c757d',
                        allowOutsideClick: false,
                        allowEscapeKey: false
                    }).then((result) => {
                        if (result.isConfirmed) {
                            // Thử đăng ký lại chính quầy này (Chiếm lại quyền)
                            location.reload();
                        } else {
                            // Quay về trang waiting để nhân viên cấu hình lại hoặc chờ khách mới
                            window.location.href = '/sign/waiting';
                        }
                    });
                }
            }
        });
    },
};

// --- 4. SỰ KIỆN (EVENTS) ---
$(document).ready(function () {
    SIGN.actions.loadData();

    // Kích hoạt Heartbeat ngay khi vào trang ký
    SIGN.config.timerHeartbeat = setInterval(SIGN.actions.heartbeat, 10000); // 10 giây/lần
    SIGN.actions.heartbeat(); // Chạy ngay lần đầu
});
