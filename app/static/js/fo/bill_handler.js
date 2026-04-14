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
    selectedIdAddition: 1, // Mặc định là 1
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
        const $container = $('#smile_tabs');
        $container.empty(); // Xóa sạch tab cũ của Folio trước

        if (!tabs || tabs.length === 0) {
            $container.html('<small class="text-muted">No tabs available</small>');
            return;
        }

        tabs.forEach(t => {
            let extraClass = '';
            let icon = 'fa-file-invoice';
            let label = t;

            // Định dạng riêng cho Tab đặc biệt
            if (t === 'V') { extraClass = 'text-danger'; icon = 'fa-trash-alt'; label = 'VOID'; }
            else if (t === 'P') { extraClass = 'text-success'; icon = 'fa-box-open'; label = 'PKG'; }

            const tabHtml = `
                <div class="smile-tab-modern ${extraClass}" data-tab="${t}">
                    <i class="fas ${icon} me-1"></i> ${label}
                </div>`;

            $container.append(tabHtml);
        });

        // Gán sự kiện click cho các tab vừa tạo
        $('.smile-tab-modern').on('click', function () {
            const tabName = $(this).data('tab');
            $('.smile-tab-modern').removeClass('active');
            $(this).addClass('active');

            BILL_ACTIONS.loadTransactions(BILL_STATE.selectedFolio, tabName);
        });
    },
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
    selectFolio: async (data, targetTab = null) => {
        BILL_STATE.selectedFolio = data.FolioNum;
        BILL_STATE.selectedIdAddition = data.IdAddition || 1;
        // 1. Lấy giá trị checkbox hiện tại (để gửi lên Server lấy đúng list Tabs)
        const isShowAll = $('#chk_show_all_bal').is(':checked') ? 1 : 0;

        const url = `/api/v1/fo/bill/details/${data.FolioNum}/${data.IdAddition || 1}?show_all=${isShowAll}`;
        const res = await API.request(url);

        if (res && res.data) {
            const h = res.data;

            // --- Đổ dữ liệu vào vùng Summary (Giữ nguyên logic của bạn) ---
            let ArrDept = BILL_UI.formatVNDates(h.ArrivalTime) + ' ' + BILL_UI.formatVNDates(h.DepartureTime);
            $('#sm_status').text(h.AdtStatus);
            $('#sm_folio').text(h.FolioNum);
            $('#sm_guest_name').text(`${h.FirstName} ${h.LastName}`);
            $('#sm_room').text(h.RoomCode);
            $('#sm_dates').text(ArrDept);
            $('#sm_rate').text(BILL_UI.formatMoney(h.RateAmount));
            $('#sm_exrate').text(BILL_UI.formatMoney(h.FolioExRate));
            $('#sm_balance').text(BILL_UI.formatMoney(data.Balance)); // Lưu ý: data.Balance lấy từ row bên ngoài
            $('#sm_ta_code').text((h.TravelAgent1Code + '-' + h.CompanyName) || '');
            $('#sm_notice').text(h.Notice || '');

            // 2. Vẽ danh sách Tab động
            BILL_UI.renderAvailableTabs(h.Tabs);
            BILL_STATE.lastMaxTransID = h.MaxTransactionID;

            // 3. Xử lý chọn Tab nào để Load dữ liệu
            if (h.Tabs && h.Tabs.length > 0) {
                // ƯU TIÊN: Nếu có targetTab (từ URL khi F5) và nó tồn tại trong list Tabs mới
                // NẾU KHÔNG: Chọn tab đầu tiên [0]
                let tabToActive = (targetTab && h.Tabs.includes(targetTab)) ? targetTab : h.Tabs[0];

                console.log("Loading tab:", tabToActive);

                // Cập nhật giao diện: Active cái tab tương ứng
                $('.smile-tab-modern').removeClass('active');
                $(`.smile-tab-modern[data-tab="${tabToActive}"]`).addClass('active');

                // Gọi hàm tải dữ liệu giao dịch
                BILL_ACTIONS.loadTransactions(data.FolioNum, tabToActive);

                // 4. Cập nhật URL để F5 không bị mất
                BILL_ACTIONS.updateURL();
            } else {
                console.warn("Không tìm thấy danh sách Tab cho Folio này.");
                $('#transaction_table_body').empty();
            }
        }
    },

    loadTransactions: (folio, tab) => {
        BILL_STATE.currentTab = tab;
        // 1. Hủy DataTable cũ nếu đã tồn tại để tránh lỗi re-initialize
        if ($.fn.DataTable.isDataTable('#table_trans')) {
            $('#table_trans').DataTable().destroy();
        }

        $('#trans_list_body').html('<tr><td colspan="12" class="text-center"><div class="text-primary"></div> Loading...</td></tr>');
        // $('#trans_list_body').html('<tr><td colspan="12" class="text-center">Loading...</td></tr>');

        $.get(`/api/v1/fo/bill/transactions/${folio}/${tab}`, function (res) {
            if (res.status === 'success') {
                BILL_ACTIONS.renderTransTable(res.data);
                $('#total_balance_display').text(BILL_UI.formatMoney(res.tab_balance));
                // 4. Khởi tạo DataTable sau khi đã có dữ liệu trong tbody
                $('#table_trans').DataTable({
                    fixedHeader: true,
                    paging: false,
                    responsive: true,
                    info: false,        // Ẩn dòng "Showing 1 of..."
                    // dom: 't',           // Chỉ hiện bảng (Table only)
                    searching: true,    // Bật ô Filter/Search
                    language: {
                        search: "",     // Bỏ chữ "Search:" mặc định
                        searchPlaceholder: "Lọc nhanh giao dịch..."
                    },
                    dom: '<"d-flex justify-content-between align-items-center mb-2"f>t' // Đưa ô Search lên trên
                });
            }
        });
    },

    renderTransTable: (data) => {
        let html = data.map(item => `
            <tr>
                <td class="text-center">${BILL_UI.formatVNDates(item.TransactionDate) || ''}</td>
                <td class="text-center">${item.TransactionCode || ''}</td>
                <td>${item.Description || ''}</td>
                <td>${item.RefNumber || ''}</td>
                <td class="text-end">${BILL_UI.formatMoney(item.SubAmount)}</td>
                <td class="text-end text-primary fw-bold">${BILL_UI.formatMoney(item.TransactionAmount)}</td>
                <td>${item.OriginRoom || ''}</td>
                <td class="text-end">${item.TaxCode || ''}</td>
                <td>${BILL_UI.formatVNDates(item.SystemTime) || ''}</td>
                <td>${item.PostingClerkID || ''}</td>
                <td class="text-start small text-muted">${item.Comment || ''}</td>
            </tr>
        `).join('');
        $('#trans_list_body').html(html || '<tr><td colspan="12" class="text-center">No transactions</td></tr>');

        $('#trans_list_body').on('click', 'tr', function () {
            // Xóa màu của dòng cũ
            $('#trans_list_body tr').removeClass('selected-row');
            // Highlight dòng vừa click
            $(this).addClass('selected-row');
        });
    },
    initOnLoad: async () => {
        const urlParams = new URLSearchParams(window.location.search);
        const folio = urlParams.get('folio');
        const idAdd = urlParams.get('id_addition') || 1;
        const tab = urlParams.get('tab');
        const showAll = urlParams.get('show_all');

        if (folio) {
            $('#chk_show_all_bal').prop('checked', showAll === '1');

            // 1. Chạy search trước để đổ dữ liệu vào bảng danh sách bên trái
            // Đảm bảo hàm search trả về một Promise (có dùng async/await)
            await BILL_ACTIONS.search();

            // 2. Sau khi bảng đã có dữ liệu, tiến hành highlight dòng cũ
            // Tìm dòng <tr> có chứa FolioNum tương ứng (giả sử bạn đặt attr là data-folio)
            const $targetRow = $(`#table_folio tr[data-folio="${folio}"]`);
            if ($targetRow.length > 0) {
                $targetRow.addClass('table-primary active'); // Thêm class highlight

                // Cuộn bảng đến dòng đó nếu danh sách quá dài
                $targetRow[0].scrollIntoView({ block: 'center', behavior: 'smooth' });
            }

            // 3. Load chi tiết bên phải
            await BILL_ACTIONS.selectFolio({ FolioNum: folio, IdAddition: parseInt(idAdd) }, tab);
        }
    },
    // 4. Lắng nghe Checkbox Show All Bal
    initEvents: () => {
        // Gán sự kiện cho checkbox
        $('#chk_show_all_bal').on('change', async function () {
            await BILL_ACTIONS.toggleShowAll();
            BILL_ACTIONS.updateURL(); // Lưu trạng thái checkbox vào URL
        });

        // Đừng quên gọi initOnLoad ở cuối initEvents
        BILL_ACTIONS.initOnLoad();
    },
    toggleShowAll: async function () {
        const folioNum = BILL_STATE.selectedFolio;
        if (!folioNum) return;

        // BƯỚC 1: Lưu lại mã Tab người dùng đang đứng trước khi render lại (ví dụ: 'B')
        const currentTab = $('.smile-tab-modern.active').data('tab');

        // Lấy trạng thái 0/1 từ checkbox
        const isShowAll = $('#chk_show_all_bal').is(':checked') ? 1 : 0;

        try {
            // Gọi API lấy danh sách tab mới
            const res = await API.request(`/api/v1/fo/bill/tabs/${folioNum}/${isShowAll}`);

            if (res && (res.status === "success" || res.data)) {
                const tabs = res.data;

                // BƯỚC 2: Vẽ lại danh sách Tab động dựa trên dữ liệu mới
                BILL_UI.renderAvailableTabs(tabs);

                if (tabs && tabs.length > 0) {
                    // BƯỚC 3: Quyết định Tab nào sẽ được Active
                    // Ưu tiên giữ lại tab cũ nếu nó vẫn tồn tại trong danh sách mới
                    let tabToActive = tabs.includes(currentTab) ? currentTab : tabs[0];

                    // BƯỚC 4: Cập nhật giao diện và load dữ liệu giao dịch
                    $(`.smile-tab-modern`).removeClass('active'); // Xóa hết active cũ
                    $(`.smile-tab-modern[data-tab="${tabToActive}"]`).addClass('active');

                    console.log(`Switching to tab: ${tabToActive}`);
                    BILL_ACTIONS.loadTransactions(folioNum, tabToActive);
                }
            }
        } catch (err) {
            console.error("Lỗi khi tải lại danh sách Tab:", err);
        }
    },
    updateURL: () => {
        const folio = BILL_STATE.selectedFolio;
        const idAdd = BILL_STATE.selectedIdAddition; // Lấy từ state
        const tab = $('.smile-tab-modern.active').data('tab') || 'A';
        const showAll = $('#chk_show_all_bal').is(':checked') ? 1 : 0;

        if (folio) {
            const params = new URLSearchParams();
            params.set('folio', folio);
            params.set('id_addition', idAdd); // Đưa lên URL
            params.set('tab', tab);
            params.set('show_all', showAll);

            const newUrl = `${window.location.pathname}?${params.toString()}`;
            window.history.replaceState({ path: newUrl }, '', newUrl);
        }
    },
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

    BILL_ACTIONS.initEvents();

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
