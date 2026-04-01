var WAITING = window.WAITING || {};

// --- 1. CẤU HÌNH (CONFIG) ---
WAITING.config = {
    apiBase: '/api/v1/devices', // URL API quản lý thiết bị
    queueBase: '/api/v1/queue', // URL API kiểm tra hồ sơ ký
    heartbeatInterval: 10000, // 10 giây báo danh 1 lần
    checkQueueInterval: 5000, // 5 giây kiểm tra hồ sơ mới 1 lần
    timerHeartbeat: null,
    timerQueue: null
};

// --- 2. PHỤ TRỢ (UI HELPERS) ---
WAITING.helpers = {
    // Lấy hoặc tạo mã định danh duy nhất cho trình duyệt (lưu vĩnh viễn trên máy này)
    getBrowserUUID: function () {
        let uuid = localStorage.getItem('device_browser_uuid');
        if (!uuid) {
            uuid = 'BRW-' + Math.random().toString(36).substr(2, 9).toUpperCase() + '-' + Date.now();
            localStorage.setItem('device_browser_uuid', uuid);
        }
        return uuid;
    },

    updateUIStatus: function (isOnline, deviceId) {
        const dot = $('#dot-status');
        const txt = $('#display-device');
        if (isOnline) {
            dot.addClass('online').removeClass('offline');
            txt.text(deviceId).addClass('text-success');
        } else {
            dot.addClass('offline').removeClass('online');
            txt.text('CHƯA KẾT NỐI').removeClass('text-success');
        }
    },
    // ID định danh máy (Vĩnh viễn trong Browser)
    getBrowserUUID: function () {
        let uuid = localStorage.getItem('device_browser_uuid');
        if (!uuid) {
            uuid = 'BRW-' + Math.random().toString(36).substr(2, 9).toUpperCase();
            localStorage.setItem('device_browser_uuid', uuid);
        }
        return uuid;
    },

    // ID định danh Tab (Duy nhất cho mỗi cửa sổ đang mở)
    getTabID: function () {
        let tabId = sessionStorage.getItem('device_tab_id');
        if (!tabId) {
            tabId = 'TAB-' + Math.random().toString(36).substr(2, 9).toUpperCase();
            sessionStorage.setItem('device_tab_id', tabId);
        }
        return tabId;
    },

    // Tạo chuỗi kết hợp để gửi lên Server
    getFullConnectionID: function () {
        return this.getBrowserUUID() + "|" + this.getTabID();
    }
};

// --- 3. HÀNH ĐỘNG (ACTIONS) ---
WAITING.actions = {
    showSetup: function () {
        // Reset lại các ô nhập liệu cho đúng thực tế hiện tại
        const currentId = localStorage.getItem('current_device_id');
        if (currentId) $('#set-device-id').val(currentId);

        // Hiện hộp thoại cấu hình
        $('#setup-box').fadeIn();
        $('#set-device-id').focus();
    },

    // Đăng ký chiếm quyền quầy
    register: function () {
        const deviceId = $('#set-device-id').val().trim().toUpperCase();
        const module = $('#set-module').val();
        const browserUuid = WAITING.helpers.getFullConnectionID();

        // 1. Kiểm tra nhanh nếu chưa nhập ID quầy
        if (!deviceId) {
            Swal.fire("Lỗi", "Vui lòng nhập Mã quầy (ID)", "error");
            $('#set-device-id').addClass('is-invalid').focus();
            return;
        }

        // 2. LỚP BẢO MẬT: Hiện popup yêu cầu gõ chữ "y"
        Swal.fire({
            title: 'XÁC NHẬN CHIẾM QUYỀN',
            text: `Bạn muốn thiết lập máy này cho quầy ${deviceId}?`,
            input: 'text',
            inputPlaceholder: "Gõ chữ '...' để xác nhận...",
            showCancelButton: true,
            confirmButtonText: 'ĐỒNG Ý',
            cancelButtonText: 'HỦY',
            preConfirm: (value) => {
                // Chỉ cho phép đi tiếp nếu gõ đúng chữ y (không phân biệt hoa thường)
                if (value.toLowerCase() !== 'y') {
                    Swal.showValidationMessage("Bạn phải gõ chữ '...' để thực hiện thao tác này!");
                    return false;
                }
                return true;
            }
        }).then((result) => {
            // 3. NẾU XÁC NHẬN ĐÚNG -> CHẠY AJAX
            if (result.isConfirmed) {
                const payload = {
                    DeviceID: deviceId,
                    ConnectionID: browserUuid,
                    ModuleName: module,
                    DeviceType: /Mobi|Android|iPad/i.test(navigator.userAgent) ? "TABLET" : "DESKTOP"
                };

                $.ajax({
                    url: WAITING.config.apiBase + '/register',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(payload),
                    success: function (res) {
                        localStorage.setItem('current_device_id', deviceId);
                        $('#setup-box').fadeOut();

                        // Cập nhật giao diện iPad ngay lập tức
                        $('#display-device').text(deviceId);
                        WAITING.helpers.updateUIStatus(true, deviceId);

                        // Kích hoạt báo danh ngay
                        WAITING.actions.startMonitoring();

                        Swal.fire("Thành công", `Đã kích hoạt quầy ${deviceId}`, "success");
                    },
                    error: function (err) {
                        const errorDetail = err.responseJSON?.detail || "Không thể đăng ký thiết bị";
                        Swal.fire("Từ chối", errorDetail, "error");
                        $('#set-device-id').addClass('is-invalid').focus();
                    }
                });
            }
        });
    },

    // Báo danh định kỳ & Kiểm tra xem có bị máy khác "đá" ra không
    heartbeat: function () {
        const deviceId = localStorage.getItem('current_device_id');
        // const browserUuid = WAITING.helpers.getBrowserUUID();
        const fullConnId = WAITING.helpers.getFullConnectionID(); // Gửi cả UUID và TabID

        if (!deviceId) return;

        $.ajax({
            url: WAITING.config.apiBase + '/ping',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ DeviceID: deviceId, ConnectionID: fullConnId }),
            success: function (res) {
                // Nếu server báo ConnectionID không khớp -> Máy khác đã chiếm quyền
                if (res.status === 'conflict') {
                    WAITING.actions.stopMonitoring();
                    Swal.fire("Mất quyền", "Thiết bị này đã bị thay thế bởi một máy khác!", "warning");
                    WAITING.helpers.updateUIStatus(false);
                }
            },
            error: function () {
                WAITING.helpers.updateUIStatus(false);
            }
        });
    },

    // Kiểm tra hàng đợi hồ sơ ký
    checkNewDocument: function () {
        const deviceId = localStorage.getItem('current_device_id');
        if (!deviceId) return;

        $.get(`${WAITING.config.queueBase}/check/${deviceId}`, function (res) {
            if (res && res.QueueID) {
                // NẾU CÓ HỒ SƠ MỚI -> Chuyển hướng sang trang ký tên
                window.location.href = `/sign/process/${res.QueueID}`;
            }
        });
    },

    startMonitoring: function () {
        // Xóa các timer cũ nếu có để tránh chạy chồng chéo
        clearInterval(WAITING.config.timerHeartbeat);
        clearInterval(WAITING.config.timerQueue);

        // ĐIỂM QUAN TRỌNG: Gọi ngay lập tức 2 hàm này trước khi đặt setInterval
        this.heartbeat();
        this.checkNewDocument();

        // Sau đó mới thiết lập vòng lặp định kỳ
        WAITING.config.timerHeartbeat = setInterval(() => {
            this.heartbeat();
        }, WAITING.config.heartbeatInterval);

        WAITING.config.timerQueue = setInterval(() => {
            this.checkNewDocument();
        }, WAITING.config.checkQueueInterval);
    },

    stopMonitoring: function () {
        clearInterval(WAITING.config.timerHeartbeat);
        clearInterval(WAITING.config.timerQueue);
    },
    resetDeviceQueue: function () {
        const deviceId = localStorage.getItem('current_device_id');
        if (!deviceId) return;

        $.ajax({
            url: '/api/v1/queue/reset-device',
            type: 'POST',
            contentType: 'application/json', // BẮT BUỘC phải có dòng này
            data: JSON.stringify({ DeviceID: deviceId }), // Chuyển Object thành chuỗi JSON
            success: function (res) {
                console.log("Giải phóng thiết bị thành công");
            },
            error: function (err) {
                console.error("Lỗi 422: Kiểm tra lại tên trường DeviceID trong Schema");
            }
        });
    }
};

// --- 4. SỰ KIỆN (EVENTS) ---
$(document).ready(function () {
    WAITING.actions.resetDeviceQueue();

    const savedId = localStorage.getItem('current_device_id');
    const browserUuid = WAITING.helpers.getBrowserUUID();

    $('#display-uuid').text(`UUID: ${browserUuid}`);

    if (savedId) {
        WAITING.helpers.updateUIStatus(true, savedId);
        WAITING.actions.startMonitoring();
    } else {
        WAITING.actions.showSetup();
    }


});
