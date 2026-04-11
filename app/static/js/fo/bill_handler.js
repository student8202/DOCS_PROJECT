/**
 * FO BILL MANAGEMENT MODULE
 * Kết hợp cấu trúc Namespace và sức mạnh của DataTable
 * 
 <script>
    // Khai báo global để các file JS sau này dùng được
    window.GLOBAL_HOTEL_DATE = "{{ get_hotel_date(request) }}";
    window.HotelDate = moment(window.GLOBAL_HOTEL_DATE, "MM/DD/YYYY").toDate();
</script>
 */

const BILL_CONFIG = {
    tableFolio: '#table_folio',
    tableTrans: '#table_trans',
    apiSearch: '/api/v1/fo/bill/search-folio',
    apiDetails: '/api/v1/fo/bill/details',
    apiTrans: '/api/v1/fo/bill/transactions'
};

const BILL_STATE = {
    // Lưu 25 tham số SP
    filter: {
        noShow: 0,
        reserved: 0,
        canceled: 0,
        inHouse: 1,      // Mặc định luôn là In-House (F5)
        arrivalToday: 0,
        checkOutToday: 0,
        checkOut: 0,
        sNumInfo: '',    // Dùng cho Folio hoặc Room#
        name: '',
        firstName: '',
        lastName: '',
        companyID: '',
        groupID: '',
        countryID: '',
        roomCode: '',
        arrivalDateFrom: '',
        arrivalDateTo: '',
        departureDateFrom: '',
        departureDateTo: '',
        hotelDate: GLOBAL_HOTEL_DATE, // "MM/DD/YYYY" 
        exactly: 0,
        includePf: 0,
        sTAorARNum: '',  // Travel Agent Code
        isNotBalance: 0,
        cruiseCode: ''
    },
    selectedFolio: null,
    currentTab: 'A',
    lastMaxTransID: 0
};

const BILL_UI = {
    formatMoney: (num) => new Intl.NumberFormat('vi-VN').format(num || 0),

    // Highlight dòng đang chọn (Thay cho cách làm thủ công)
    rowSelected: (row) => {
        $(BILL_CONFIG.tableFolio).find('tr').removeClass('selected-row');
        $(row).addClass('selected-row');
    },
    // Hàm này giúp điền nhanh ngày Hotel Date vào các ô input khi Lễ tân cần lọc
    presetDates: function () {
        const dateFormatted = moment(HotelDate).format('YYYY-MM-DD'); // Chuyển sang format của <input type="date">
        $('#arr_from, #arr_to, #dep_from, #dep_to').val(dateFormatted);
    },
    renderAvailableTabs: (tabs) => {
        // Mặc định ẩn V và P
        $('#tab-v, #tab-p').addClass('d-none');

        // Duyệt danh sách Tab từ Server trả về
        tabs.forEach(t => {
            if (t === 'V') $('#tab-v').removeClass('d-none');
            if (t === 'P') $('#tab-p').removeClass('d-none');
        });
    }
};

const BILL_ACTIONS = {
    // 1. Khởi tạo DataTable (Hiệu suất cực cao cho bảng nhiều dữ liệu)
    initFolioTable: () => {
        $(BILL_CONFIG.tableFolio).DataTable({
            paging: false,      // Vì SP đã lọc sẵn, không cần phân trang phía client
            scrollY: '200px',   // Cố định chiều cao bảng
            scrollCollapse: true,
            info: false,        // Ẩn dòng "Showing 1 of..."
            dom: 't',           // Chỉ hiện bảng (Table only)
            columns: [
                { data: 'Status', className: 'dt-center' },
                { data: 'FolioNum' },
                { data: 'ConfirmNum' },
                { data: 'GuestName', className: 'fw-bold' },
                { data: 'RoomNum', className: 'dt-center' },
                { data: 'Balance', className: 'dt-right text-danger fw-bold', render: d => BILL_UI.formatMoney(d) },
                { data: 'Mcf' },
                { data: 'GroupName' },
                { data: 'Arrival' },
                { data: 'Departure' }
            ],
            // Sự kiện khi Click vào 1 dòng
            createdRow: (row, data) => {
                $(row).css('cursor', 'pointer').on('click', () => {
                    BILL_UI.rowSelected(row);
                    BILL_ACTIONS.selectFolio(data);
                });
            }
        });
    },

    // 2. Hàm Search (Gọi lại AJAX cho DataTable)
    search: () => {
        // Tạo bản copy của filter để ép kiểu an toàn
        const sendData = { ...BILL_STATE.filter };

        // Ép kiểu toàn bộ các trường Boolean/Int sang Number
        const intFields = ['noShow', 'reserved', 'canceled', 'inHouse', 'arrivalToday',
            'checkOutToday', 'checkOut', 'exactly', 'includePf', 'isNotBalance'];

        intFields.forEach(field => {
            sendData[field] = Number(sendData[field]);
        });

        // Cập nhật giá trị từ Input
        sendData.sNumInfo = String($('#search_guest').val() || "");
        sendData.groupID = String($('#search_group').val() || "");
        sendData.sTAorARNum = String($('#search_ta').val() || "");

        $.ajax({
            url: BILL_CONFIG.apiSearch,
            type: 'POST',
            data: JSON.stringify(sendData), // Ép thành chuỗi JSON
            contentType: 'application/json; charset=utf-8', // Chỉ định rõ JSON
            dataType: 'json',
            success: function (res) {
                const table = $(BILL_CONFIG.tableFolio).DataTable();
                table.clear().rows.add(res.data).draw();
            },
            error: function (xhr) {
                // ĐÂY LÀ CHỖ ĐỂ XEM CHI TIẾT LỖI 422
                console.log("Lỗi chi tiết từ Server:", xhr.responseJSON);
            }
        });
    },
    selectFolio: (data) => {
        BILL_STATE.selectedFolio = data.FolioNum;

        // Gọi API lấy chi tiết Header (Tên khách, Company, Tabs, MaxID)
        $.get(`/api/v1/fo/bill/details/${data.FolioNum}/${data.IdAddition || 1}`, function (res) {
            if (res.status === 'success') {
                const h = res.data;
                // Đổ dữ liệu vào vùng Summary bên trái
                $('#sm_folio').text(h.FolioNum);
                $('#sm_guest_name').text(`${h.FirstName} ${h.LastName}`);
                $('#sm_room').text(h.RoomCode);
                $('#sm_balance').text(BILL_UI.formatMoney(data.Balance));
                $('#sm_notice').text(h.Notice || 'None');

                // Hiển thị/Ẩn các Tab dựa trên dữ liệu từ SP CHGetFolioBalanceCode
                BILL_UI.renderAvailableTabs(h.Tabs);

                // Lưu MaxID để theo dõi giao dịch mới
                BILL_STATE.lastMaxTransID = h.MaxTransactionID;
            }
        });

        // Tự động load giao dịch Tab A
        BILL_ACTIONS.loadTransactions(data.FolioNum, 'A');
    },

    loadTransactions: (folio, tab) => {
        BILL_STATE.currentTab = tab;
        $('#trans_list_body').html('<tr><td colspan="12" class="text-center">Loading...</td></tr>');

        $.get(`/api/v1/fo/bill/transactions/${folio}/${tab}`, function (res) {
            if (res.status === 'success') {
                BILL_ACTIONS.renderTransTable(res.data);
                $('#total_balance_display').text(BILL_UI.formatMoney(res.tab_balance));
            }
        });
    },

    renderTransTable: (data) => {
        let html = data.map(item => `
            <tr>
                <td class="text-center">${item.Date || ''}</td>
                <td class="text-center">${item.SvcCode || ''}</td>
                <td>${item.Description || ''}</td>
                <td>${item.RefNo || ''}</td>
                <td class="text-end">${BILL_UI.formatMoney(item.SubAmount)}</td>
                <td class="text-end text-primary fw-bold">${BILL_UI.formatMoney(item.Amount)}</td>
                <td>${item.OrgCode || ''}</td>
                <td class="text-center">${item.RoomNum || ''}</td>
                <td class="text-end">${item.Tax || 0}</td>
                <td>${item.InvDate || ''}</td>
                <td>${item.UserName || ''}</td>
                <td class="small text-muted">${item.Comment || ''}</td>
            </tr>
        `).join('');
        $('#trans_list_body').html(html || '<tr><td colspan="12" class="text-center">No transactions</td></tr>');
    }
};

// --- SỰ KIỆN (Events) ---
$(document).ready(function () {
    // 2. IN CONSOLE ĐỂ KIỂM TRA TRƯỚC KHI GỌI API
    console.log("--- DEBUG PAYLOAD BEFORE SEARCH ---");
    console.table(BILL_STATE.filter); // Dùng table để nhìn cho rõ 25 tham số
    console.log("JSON gửi đi:", JSON.stringify(BILL_STATE.filter));

    BILL_ACTIONS.initFolioTable();

    // Nút Search chính
    $('#btn-main-search').on('click', BILL_ACTIONS.search);

    // Xử lý Tab A, B, V, P
    $('.smile-tab-modern').on('click', function () {
        $('.smile-tab-modern').removeClass('active');
        $(this).addClass('active');
        BILL_STATE.currentTab = $(this).data('tab');
        if (BILL_STATE.selectedFolio) {
            BILL_ACTIONS.loadTransactions(BILL_STATE.selectedFolio, BILL_STATE.currentTab);
        }
    });
    $('#btn-apply-more').on('click', function () {
        const f = BILL_STATE.filter;
        // Đồng bộ checkbox
        f.reserved = $('#st_reserved').is(':checked') ? 1 : 0;
        f.inHouse = $('#st_inhouse').is(':checked') ? 1 : 0;
        f.checkOutToday = $('#st_cotoday').is(':checked') ? 1 : 0;
        f.checkOut = $('#st_allco').is(':checked') ? 1 : 0;
        f.isNotBalance = $('#st_notbalance').is(':checked') ? 1 : 0;

        // Đồng bộ ngày tháng
        f.arrivalDateFrom = $('#arr_from').val();
        f.arrivalDateTo = $('#arr_to').val();
        f.departureDateFrom = $('#dep_from').val();
        f.departureDateTo = $('#dep_to').val();

        $('#modalSearchMore').modal('hide');
        BILL_ACTIONS.search();
    });
});
