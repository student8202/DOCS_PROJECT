/**
 * DASHBOARD IN-HOUSE MODULE
 */

// --- 1. CẤU HÌNH (Config) ---
const DASH_CONFIG = {
    table: '#tblInHouseDash',
    apiUrl: '/fo/inhouse-list'
};

// --- 2. PHỤ TRỢ (UI Helpers) ---
const DASH_UI = {
    formatDate: (dateStr) => {
        if(!dateStr) return '';
        const d = new Date(dateStr);
        return d.toLocaleDateString('vi-VN');
    },
    renderStatus: (room) => {
        return `<span class="badge bg-success-light text-success fw-bold">${room}</span>`;
    }
};

// --- 3. HÀNH ĐỘNG (Actions) ---
const DASH_ACTIONS = {
    initTable: () => {
        $(DASH_CONFIG.table).DataTable({
            ajax: { url: DASH_CONFIG.apiUrl, dataSrc: '' },
            columns: [
                { data: 'RoomCode', className: 'dt-center', render: d => DASH_UI.renderStatus(d) },
                { data: 'LastName', render: (d, t, row) => `<b>${row.LastName}</b> ${row.FirstName}` },
                { data: 'ArrivalDate', render: d => DASH_UI.formatDate(d) },
                { data: 'DepartureDate', render: d => DASH_UI.formatDate(d) },
                { data: 'CompanyName', className: 'small' }
            ],
            pageLength: 5, // Dashboard chỉ hiện 5 khách mới nhất hoặc quan trọng
            dom: 't',      // Chỉ hiện bảng, ẩn các nút search/phân trang cho gọn
            order: [[0, 'asc']]
        });
    }
};

// --- 4. SỰ KIỆN (Events) ---
$(document).ready(function () {
    DASH_ACTIONS.initTable();
});
