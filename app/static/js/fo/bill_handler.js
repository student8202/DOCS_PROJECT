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
const API = {
    // Hàm cốt lõi để gọi API
    request: async (url, options = {}) => {
        // Mặc định là hiện Alert nếu có lỗi, trừ khi ta chủ động tắt đi
        const config = { showError: true, ...options };
        try {
            const response = await $.ajax({
                url: url,
                type: options.type || 'GET',
                data: config.data ? JSON.stringify(config.data) : null,
                contentType: 'application/json; charset=utf-8',
                dataType: 'json'
            });

            // Nếu status từ Backend là success
            if (response.status === 'success') {
                return response; // Trả về nguyên object {status, data, ...}
            } else {
                // CHỈ HIỆN ALERT NẾU showError = true
                if (config.showError) {
                    Swal.fire({
                        icon: 'warning',
                        title: 'Thông báo',
                        text: response.message
                    });
                }
                return response;
            }
        } catch (xhr) {
            // Xử lý lỗi hệ thống (404, 500, 422...)
            const errorMsg = xhr.responseJSON?.message || "Lỗi kết nối Server";
            if (config.showError) {
                Swal.fire({ icon: 'error', title: 'Lỗi', text: errorMsg });
            }
            console.error("System Error:", xhr.responseJSON);
            return null;
        }
    }
};
/* // example use custom sweet alert 2 sử dụng interface api
const res = await API.request('/api/sign', { showError: false });
if (res && res.status === 'error') {
    Swal.fire({
        title: 'Ký số thất bại!',
        html: `Lỗi: <b>${res.message}</b>. <br>Vui lòng kiểm tra lại thiết bị ký.`,
        icon: 'critical'
    });
}
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
    // format date
    formatVNDates: function (data) {
        const dateFormatted = moment(data).format('DD/MM/YY'); // Chuyển sang format của <input type="date">
        return dateFormatted;
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
        let currentFlag = false; // Biến cờ để bật/tắt màu
        let lastFolio = null;
        $(BILL_CONFIG.tableFolio).DataTable({
            data: [],
            fixedHeader: true,
            paging: false,
            responsive: true,
            info: false,        // Ẩn dòng "Showing 1 of..."
            dom: 't',           // Chỉ hiện bảng (Table only)
            // Sắp xếp theo RoomCode (Index 4)
            order: [[4, 'asc']],
            columns: [
                { data: 'AdtStatus', className: 'dt-center' },
                { data: 'FolioNum' },
                { data: 'ConfirmNum' },
                { data: 'LastName', className: 'fw-bold' },
                { data: 'RoomCode', className: 'dt-center' },
                {
                    data: 'Balance',
                    className: 'dt-right text-danger fw-bold',
                    render: (data, type, row, meta) => {
                        // Lấy danh sách tất cả dữ liệu sau khi đã Sort/Filter
                        const allData = meta.settings.aoData;
                        const currentIndex = meta.row;

                        // Nếu là dòng đầu tiên của bảng, luôn hiển thị
                        if (currentIndex === 0) {
                            return BILL_UI.formatMoney(data);
                        }

                        // Kiểm tra dòng ngay phía trước (index - 1)
                        // Nếu FolioNum dòng này giống hệt dòng trước -> Ẩn Balance
                        const previousRowData = allData[currentIndex - 1]._aData;
                        if (row.FolioNum === previousRowData.FolioNum) {
                            return "";
                        }

                        return BILL_UI.formatMoney(data);
                    }
                },
                { data: 'CMF' },
                { data: 'GroupCode' },
                { data: 'ArrivalTime', render: d => d ? moment(d).format('DD/MM/YYYY') : '' },
                { data: 'DepartureTime', render: d => d ? moment(d).format('DD/MM/YYYY') : '' },
                { data: 'IdAddition', visible: false, searchable: false, defaultContent: "1" },//  Cột ẩn
            ],
            // Cần vẽ lại bảng mỗi khi sort/filter để logic render Balance chạy lại chính xác
            drawCallback: function () {
                // Callback này đảm bảo khi người dùng nhấn sort thủ công, 
                // dòng đầu tiên mới của mỗi Folio vẫn sẽ hiện Balance.
                currentFlag = false; // Reset khi vẽ lại bảng
                lastFolio = null;
            },
            // Sự kiện khi Click vào 1 dòng
            createdRow: (row, data) => {
                // Nếu sang Folio mới thì đảo ngược "công tắc"
                if (lastFolio !== null && data.FolioNum !== lastFolio) {
                    currentFlag = !currentFlag;
                }
                lastFolio = data.FolioNum;

                // Nếu công tắc đang BẬT thì thêm class màu nền
                if (currentFlag) {
                    $(row).addClass('folio-alt-bg');
                }
                $(row).css('cursor', 'pointer').on('click', () => {
                    BILL_UI.rowSelected(row);
                    BILL_ACTIONS.selectFolio(data);
                });
            }
        });
    },

    // 2. Hàm Search (Gọi lại AJAX cho DataTable)
    search: async () => {
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

        // GỌI QUA HELPER
        const res = await API.request(BILL_CONFIG.apiSearch, {
            type: 'POST',
            data: sendData
        });

        // Nếu res hợp lệ (không phải null), ta mới đổ vào Table
        if (res) {
            const table = $(BILL_CONFIG.tableFolio).DataTable();
            // Bạn không cần lo data là gì nữa, vì Backend đã cam kết trả về [] nếu không có dữ liệu
            table.clear().rows.add(res.data).draw();
        }
    },
    selectFolio: async (data) => {
        BILL_STATE.selectedFolio = data.FolioNum;
        // console.log(data);
        const url = `/api/v1/fo/bill/details/${data.FolioNum}/${data.IdAddition || 1}`;
        const res = await API.request(url);

        if (res) {
            const h = res.data;
            let ArrDept = BILL_UI.formatVNDates(h.ArrivalTime) + ' ' + BILL_UI.formatVNDates(h.DepartureTime);
            let TACompany = h.TravelAgent1Code + '-' + h.CompanyName;
            // Đổ dữ liệu vào vùng Summary bên trái
            $('#sm_status').text(h.AdtStatus);
            $('#sm_folio').text(h.FolioNum);
            $('#sm_guest_name').text(`${h.FirstName} ${h.LastName}`);
            $('#sm_room').text(h.RoomCode);
            $('#sm_dates').text(ArrDept);
            $('#sm_rate').text(BILL_UI.formatMoney(h.RateAmount));
            $('#sm_exrate').text(BILL_UI.formatMoney(h.FolioExRate));
            $('#sm_balance').text(BILL_UI.formatMoney(data.Balance));
            $('#sm_ta_code').text(TACompany || '');
            $('#sm_notice').text(h.Notice || '');
            // Hiển thị/Ẩn các Tab dựa trên dữ liệu từ SP CHGetFolioBalanceCode
            BILL_UI.renderAvailableTabs(h.Tabs);

            // Lưu MaxID để theo dõi giao dịch mới
            BILL_STATE.lastMaxTransID = h.MaxTransactionID;
        }
        
        console.log(res.data.Tabs);
        if (res.data.Tabs && res.data.Tabs.length > 0) {
            const firstTab = res.data.Tabs[0]; // Lấy phần tử đầu tiên (ví dụ: 'A')

            console.log("Auto loading tab:", firstTab);
            BILL_ACTIONS.loadTransactions(data.FolioNum, firstTab);
            // Đừng quên cập nhật giao diện: Active cái tab tương ứng
            $(`.smile-tab-modern[data-tab="${firstTab}"]`).addClass('active');
        } else {
            console.warn("Không tìm thấy danh sách Tab cho Folio này.");
        }
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
