/**
 * FO DASHBOARD HANDLER - ULTRA COMPACT
 */

// 1. CONFIG
const FO_DASH = {
    table: '#tblInHouseDash',
    api: '/fo/inhouse-list'
};

// 2. UI HELPERS (Dạng nhỏ gọn)
const FO_UI = {
    formatDate: (d) => d ? new Date(d).toLocaleDateString('vi-VN') : '',
    renderRoom: (r) => `<span class="badge bg-success-light text-success border border-success fw-bold">${r}</span>`
};

// 3. ACTIONS
const FO_ACTIONS = {
    loadTable: () => {
        $(FO_DASH.table).DataTable({
            ajax: { url: FO_DASH.api, dataSrc: '' },
            columns: [
                { data: 'RoomCode', className: 'dt-center', render: d => FO_UI.renderRoom(d) },
                { data: 'LastName', render: (d, t, row) => `<b>${d}</b> ${row.FirstName || ''}` },
                { data: 'ArrivalDate', render: d => FO_UI.formatDate(d) },
                { data: 'DepartureDate', render: d => FO_UI.formatDate(d) },
                { data: 'CompanyName', className: 'small text-muted' }
            ],
            pageLength: 10,
            dom: 'tp', // Chỉ hiện table và pagination
            language: { url: '/static/js/languages.json' }
        });
    },
    reload: () => {
        if (FO_DASH.tableInstance) {
            FO_DASH.tableInstance.ajax.reload(null, false);
        }
    }
};

// 4. EVENTS
$(document).ready(() => {
    FO_ACTIONS.loadTable();
});
