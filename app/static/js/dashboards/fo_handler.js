/**
 * FO DASHBOARD MODULE
 * Cấu hình -> Phụ trợ -> Hành động -> Sự kiện
 */

// 1. CONFIG
const FO_DASH = {
    tableId: '#tblInHouseDash',
    apiUrl: '/fo/inhouse-list2',
    instance: null,
    // Lấy module đã lưu, nếu chưa có gì (mới mở máy) thì lấy 'ih'
    currentModule: localStorage.getItem('fo_last_module') || 'ih'
};

// 2. UI HELPERS
const FO_DASH_UI = {
    fmtDate: (d) => d ? moment(d).format('DD/MM/YY') : '',
    fmtTime: (d) => d ? moment(d).format('HH:mm') : '',
    fmtMoney: (v) => {
        if (!v) return '0';
        let num = parseFloat(v.replace(/,/g, ''));
        return num.toLocaleString('vi-VN');
    },
    renderRoom: (room, type) => {
        let color = (type === 'BFD') ? 'text-success' : 'text-primary';
        return `<i class="fas fa-circle ${color} me-1" style="font-size:7px"></i><b>${room}</b>`;
    }
};
// Hàm dùng chung để xử lý ẩn dòng lặp nhưng vẫn Sort đúng theo nhóm Folio
const renderSmileGroup = (data, type, row, meta, isBold = false) => {
    // 1. KHI SẮP XẾP/LỌC: Luôn trả về FFolioNum thật để nhóm không bị xé lẻ
    if (type === 'sort' || type === 'type' || type === 'filter') {
        return row.FFolioNum;
    }

    // 2. KHI HIỂN THỊ: Nếu trùng FFolioNum với dòng ngay phía trên thì ẩn đi
    // if (meta.row > 0) {
    //     const prevData = meta.settings.aoData[meta.row - 1]._aData;
    //     if (prevData.FFolioNum === row.FFolioNum) {
    //         return ''; 
    //     }
    // }

    // Trả về dữ liệu có in đậm hoặc không
    const displayData = data || '';
    return isBold ? `<b>${displayData}</b>` : displayData;
};
let currentFilter = 'all'; // Biến lưu trạng thái lọc: all, git, group

// 1. CẤU HÌNH BỘ LỌC SEARCH.PUSH (Lọc theo GIT/Group)
$.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
    if (settings.nTable.id !== 'tblInHouseDash') return true;

    const rowData = settings.aoData[dataIndex]._aData;
    const hasGroup = (rowData.SortGroup && rowData.SortGroup.trim() !== "");

    if (currentFilter === 'git') return !hasGroup;    // Chỉ hiện khách lẻ (không có SortGroup)
    if (currentFilter === 'group') return hasGroup;  // Chỉ hiện khách đoàn (có SortGroup)
    return true; // Mặc định hiện tất cả
});
// Thêm hàm bổ trợ tính toán Pax
const calcPax = (dataList) => {
    let adt = 0, chl = 0, enf = 0;
    dataList.forEach(i => {
        adt += parseInt(i.NumAdt || 0);
        chl += parseInt(i.NumChild || 0);
        enf += parseInt(i.NumEnf || 0);
    });
    return `Pax: ${adt + chl + enf} (Adt: ${adt}, Chl: ${chl}, Enf: ${enf})`;
};
// 3. ACTIONS
FO_DASH.actions = {
    init: () => {
        const hotelDateStr = GLOBAL_HOTEL_DATE;

        // CÁCH 1: Gắn sự kiện TRƯỚC KHI init DataTable (Khuyên dùng)
        $(FO_DASH.tableId).on('preXhr.dt', function (e, settings, data) {
            // Hiện loader ngay khi bắt đầu gọi API
            $('#global-loader').css('display', 'flex').show();
        });

        $(FO_DASH.tableId).on('xhr.dt', function (e, settings, json, xhr) {
            // Ẩn loader khi server trả về kết quả (thành công hoặc lỗi)
            $('#global-loader').fadeOut(300);
        });

        FO_DASH.instance = $(FO_DASH.tableId).DataTable({
            ajax: { url: FO_DASH.apiUrl, dataSrc: '' },
            scrollX: true,
            fixedColumns: { left: 2 },
            columns: [
                {
                    data: 'FolioNum',
                    className: 'text-nowrap py-1',
                    render: (data, type, row) => {
                        const folio = row.FFolioNum;
                        const sGroup = row.SortGroup ? `'${row.SortGroup}'` : 'null';
                        const idAdd = row.IdAddition;

                        // GIẢ SỬ: 0-Chưa gửi, 1-Đang chờ ký, 2-Đã ký, 3-Hoàn tất (Đã vào SMILE)
                        const sts = row.SignStatus || 0;

                        let mainBtn = '';

                        // --- LOGIC NÚT BẤM CHÍNH (PRIMARY ACTION) ---
                        switch (sts) {
                            case 1: // Đang chờ khách ký
                                mainBtn = `<button class="btn btn-xs btn-warning btn-status-action py-0" 
                            onclick="FO_DASH.actions.resetAndResend('${folio}', ${sGroup}, ${idAdd})">GỬI LẠI</button>`;
                                break;
                            case 2: // Khách đã ký xong
                                mainBtn = `<button class="btn btn-xs btn-success btn-status-action py-0" 
                            onclick="FO_DASH.actions.openReview('${folio}', ${idAdd})">DUYỆT</button>`;
                                break;
                            case 3: // Đã hoàn tất đẩy vào SMILE
                                mainBtn = `<button class="btn btn-xs btn-secondary btn-status-action py-0" 
                            onclick="FO_DASH.actions.viewFinal('${folio}')"><i class="fas fa-eye"></i> XEM</button>`;
                                break;
                            default: // Chưa làm gì (Status 0 hoặc Null)
                                mainBtn = `<button class="btn btn-xs btn-primary btn-status-action py-0" 
                            onclick="FO_DASH.actions.openSignProcess('${folio}', ${sGroup}, ${idAdd})">KÝ</button>`;
                        }

                        // --- CẤU TRÚC 3 CHẤM (SECONDARY ACTIONS) ---
                        return `
        <div class="d-flex align-items-center">
            ${mainBtn}
            <div class="dropdown ms-2 position-static">
                <!-- Dùng thẻ <a> như cách cũ của bạn cho nhạy -->
                <a class="text-muted p-1 dropdown-toggle no-caret" href="#" role="button" 
                data-bs-toggle="dropdown" 
                data-bs-boundary="viewport"  data-bs-display="static"
                aria-expanded="false">
                    <i class="fas fa-ellipsis-v"></i>
                </a>
                <ul class="dropdown-menu shadow border-0" style="z-index: 99999; min-width: 150px;">
                    <li><a class="dropdown-item py-2" href="javascript:void(0)" onclick="FO_DASH.actions.openSignProcess('${folio}', ${sGroup}, ${idAdd})">
                        <i class="fas fa-pen-nib me-2 text-primary"></i> Gửi hồ sơ mới</a></li>
                    <li><a class="dropdown-item py-2" href="javascript:void(0)" onclick="FO_DASH.actions.changeDevice('${folio}')">
                        <i class="fas fa-tablet-alt me-2 text-info"></i> Chuyển máy ký</a></li>
                    <hr class="dropdown-divider">
                    <li><a class="dropdown-item py-2 text-danger" href="javascript:void(0)" onclick="FO_DASH.actions.forceCancel('${folio}')">
                        <i class="fas fa-trash-alt me-2"></i> Hủy hồ sơ</a></li>
                </ul>
            </div>
        </div>`;
                    }
                },// 0
                {
                    data: 'AdtStatus',
                    render: function (data, type, row) {
                        const status = parseInt(data);
                        const depDate = row.DepartureDate ? moment(row.DepartureDate).format('MM/DD/YYYY') : '';
                        if (status === 1) return '<span class="text-primary">RS</span>';
                        if (status === 3) return '<span class="text-muted">CO</span>';
                        if (status === 2) {
                            return (depDate === hotelDateStr) ? '<span class="text-danger fw-bold">DO</span>' : '<span class="text-success">IH</span>';
                        }
                        return data;
                    }
                }, // 1
                { data: 'AdtStatus', defaultContent: "" }, // 2
                {
                    data: 'FolioNum', defaultContent: "",
                    render: function (data, type, row, meta) {
                        // KHI SẮP XẾP: Trả về FFolioNum để các dòng rỗng không bị tách khỏi nhóm
                        if (type === 'sort') {
                            return row.FFolioNum;
                        }

                        // KHI HIỂN THỊ: Giữ nguyên giá trị rỗng của SMILE cho đúng giao diện hình ảnh
                        return data ? `<b>${data}</b>` : '';
                    }
                }, // 3
                { data: 'ConfirmNum', render: (d, t, r, m) => renderSmileGroup(d, t, r, m, true) }, // 4
                { data: 'Title', defaultContent: "" }, // 5
                { data: 'LastName', defaultContent: "" }, // 6
                {
                    data: 'FirstName', defaultContent: "",
                    className: 'text-end fw-bold text-primary',
                    render: function (data, type, row) {
                        if (!data || data === "0") return "-";

                        // Ví dụ: "4,000,000.00" -> "4000000.00"
                        let cleanData = data.toString().replace(/,/g, '');

                        const num = parseFloat(cleanData);
                        // Kiểm tra xem sau khi dọn dẹp có phải là số không
                        const isNumeric = !isNaN(num) && isFinite(cleanData);

                        if (isNumeric) {
                            // ĐỊNH DẠNG SỐ VIỆT NAM - KHÔNG SỐ LẺ
                            return new Intl.NumberFormat('vi-VN', {
                                maximumFractionDigits: 0
                            }).format(num);
                        }

                        // NẾU LÀ CHỮ (Ví dụ "FIT", "CORP") -> Giữ nguyên chuỗi
                        return data;
                    }
                }, // 7 (Giá)
                { data: 'VipLevel', defaultContent: "" }, // 8
                { data: 'FRoomCode', defaultContent: "" }, // 9
                { data: 'RoomTypeCode', render: (d, t, r, m) => renderSmileGroup(d, t, r, m, true) }, // 10
                { data: 'RoomTypeBooked', render: (d, t, r, m) => renderSmileGroup(d, t, r, m, true) }, // 11
                {
                    data: 'ArrivalDate',
                    render: (d, t, r, m) => renderSmileGroup(d ? moment(d).format('DD/MM/YYYY') : '', t, r, m)
                }, // 12
                {
                    data: 'DepartureDate',
                    render: (d, t, r, m) => renderSmileGroup(d ? moment(d).format('DD/MM/YYYY') : '', t, r, m)
                }, // 13
                { data: 'NumGuest', defaultContent: "" }, // 14
                { data: 'ViewShare', defaultContent: "" }, // 15
                {
                    data: null, // 16: CMT/MSG/FLG
                    render: function (data, type, row) {
                        let labels = [];
                        if (parseInt(row.Cmt) === 1) labels.push('<span class="text-info">CMT</span>');
                        if (parseInt(row.Msg) === 1) labels.push('<span class="text-warning">MSG</span>');
                        if (parseInt(row.Flg) === 1) labels.push('<span class="text-danger">FLG</span>');
                        return labels.join(', ');
                    }
                },
                {
                    data: 'GroupCode',
                    render: function (data, type, row, meta) {
                        // KHI SẮP XẾP: Trả về FFolioNum để các dòng rỗng không bị tách khỏi nhóm
                        if (type === 'sort' || type === 'type') {
                            return row.SortGroup;
                        }
                        // KHI HIỂN THỊ: Giữ nguyên giá trị rỗng của SMILE cho đúng giao diện hình ảnh
                        return data ? `<b>${data}</b>` : '';
                    }
                }, // 17
                {
                    data: 'CompanyName',
                    render: function (data, type, row, meta) {
                        // KHI SẮP XẾP: Trả về FFolioNum để các dòng rỗng không bị tách khỏi nhóm
                        if (type === 'sort' || type === 'type') {
                            return row.SortCompany;
                        }
                        // KHI HIỂN THỊ: Giữ nguyên giá trị rỗng của SMILE cho đúng giao diện hình ảnh
                        return data ? `<b>${data}</b>` : '';
                    }
                }, // 18
                { data: 'SalesPerson', defaultContent: "" }, // 19
                { data: 'BookStatus', defaultContent: "" }, // 20
                { data: 'NAT', defaultContent: "" }, // 21
                { data: 'CompFlag', render: d => d ? 'Y' : '', defaultContent: "" }, // 22
                { data: 'HUFlag', render: d => d ? 'Y' : '', defaultContent: "" }, // 23
                { data: 'ArrivalDate', render: d => d ? moment(d).format('DD/MM/YYYY HH:mm') : '' }, // 24
                { data: 'DepartureDate', render: d => d ? moment(d).format('DD/MM/YYYY HH:mm') : '' }, // 25
                { data: 'BookTime', render: d => d ? moment(d).format('DD/MM/YYYY HH:mm') : '' }, // 26
                { data: 'NumAdt', defaultContent: "0" }, // 27
                { data: 'NumChild', defaultContent: "0" }, // 28
                { data: 'NumEnf', defaultContent: "0" }, // 29
                { data: 'SpecialService', defaultContent: "" }, // 30
                { data: 'Notice', defaultContent: "" }, // 31
                { data: 'FFolioNum', visible: false, searchable: true }, // 32: Cột ẩn
                { data: 'IdAddition', visible: false, searchable: false },// 33: Cột ẩn
                { data: 'SortGroup', defaultContent: "", visible: false, searchable: true }, // 34: Cột ẩn
                { data: 'SortCompany', defaultContent: "", visible: false, searchable: true }, // 35: Cột ẩn
            ],
            // BƯỚC 1: Reset trạng thái trước mỗi lần vẽ lại bảng (sort/filter)
            preDrawCallback: function () {
                lastFolioGroup = null;
                currentGroupClass = 'group-odd';
            },

            // BƯỚC 2: Kiểm tra FFolioNum để gán class màu cho từng dòng
            rowCallback: function (row, data) {
                // Nếu FFolioNum hiện tại khác với dòng trước đó -> Đổi màu
                if (data.FFolioNum !== lastFolioGroup) {
                    currentGroupClass = (currentGroupClass === 'group-even') ? 'group-odd' : 'group-even';
                    lastFolioGroup = data.FFolioNum;
                }
                // Xóa các class mặc định của DataTable và gán class nhóm
                $(row).removeClass('odd even').addClass(currentGroupClass);
            },
            order: [[9, 'asc'], [32, 'asc']],
            // BƯỚC 2: Logic "Gom nhóm" khi nhấn Sort (Dùng columnDefs)
            columnDefs: [
                { targets: '_all', className: 'align-middle' },

                // Cấu hình gom nhóm cho các cột quan trọng (Ví dụ: Folio, Conf, Name, Room)
                // Khi click vào cột 3 (Folio), nó sẽ xếp theo cột 3 rồi đến cột 32
                { targets: 3, orderData: [32, 3] },
                // Khi click vào cột 4 (Confirm), nó sẽ xếp theo cột 4 rồi đến cột 32
                { targets: 4, orderData: [32, 4] },
                // Khi click vào cột 9 (Room), nó sẽ xếp theo cột 9 rồi đến cột 32
                { targets: 10, orderData: [32, 10] },
                // Bạn có thể thêm các cột khác tương tự: 10, 12, 13...
                { targets: 11, orderData: [32, 11] },
                { targets: 12, orderData: [32, 12] },

            ],
            // BƯỚC 1: Cấu hình Phân trang & Search
            lengthMenu: [[10, 20, 50, 100, -1], [10, 20, 50, 100, "Tất cả"]],
            pageLength: 20,
            dom: '<"d-flex justify-content-between align-items-center mb-1"lf>rtip',
            drawCallback: function (settings) {
                const api = this.api();
                const allData = api.rows({ filter: 'applied' }).data().toArray();
                if (allData.length === 0) return;

                // 1. Hàm tính Pax (Giữ nguyên của bạn)
                const getSummary = (dataList) => {
                    let adt = 0, chl = 0, enf = 0;
                    const uniqueRooms = new Set();
                    for (let i = 0; i < dataList.length; i++) {
                        uniqueRooms.add(dataList[i].FFolioNum);
                        adt += (parseInt(dataList[i].NumAdt) || 0);
                        chl += (parseInt(dataList[i].NumChild) || 0);
                        enf += (parseInt(dataList[i].NumEnf) || 0);
                    }
                    return {
                        rooms: uniqueRooms.size,
                        pax: `Pax: ${adt + chl + enf} (A:${adt}|C:${chl}|E:${enf})`
                    };
                };

                // 2. Tính toán
                const allSum = getSummary(allData);
                const fitSum = getSummary(allData.filter(i => !i.SortGroup || i.SortGroup.trim() === ""));
                const groupSum = getSummary(allData.filter(i => i.SortGroup && i.SortGroup.trim() !== ""));

                // 3. Cập nhật con số Badge
                $('#lblTotalRooms').text(allSum.rooms);
                $('#lblTotalGit').text(fitSum.rooms);
                $('#lblTotalGroup').text(groupSum.rooms);

                // 4. CẬP NHẬT DỮ LIỆU (Desktop dùng title, Mobile dùng data-pax)
                const updateUI = (id, label, sum) => {
                    const text = `${label} - ${sum.pax}`;
                    $(id).attr('title', text).attr('data-pax', text);
                };

                updateUI('#btnFilterAll', 'TOTAL', allSum);
                updateUI('#btnFilterGit', 'FIT', fitSum);
                updateUI('#btnFilterGroup', 'GROUP', groupSum);

                // --- ĐOẠN FIX LỖI MẤT NEO CỘT (FIXEDCOLUMNS) --
                setTimeout(() => {
                    if (FO_DASH.instance && FO_DASH.instance.fixedColumns) {
                        // Với bản 5.x, chỉ cần gọi hàm này để nó tính toán lại vị trí các cột dính (sticky)
                        FO_DASH.instance.fixedColumns();

                        // Nếu vẫn thấy lệch, ép trình duyệt vẽ lại phần header ảo
                        $(window).trigger('resize');
                    }
                }, 50);
            },
            language: {
                // url: '/static/js/languages.json',
                search: "Tìm:",
                lengthMenu: "Xem _MENU_"
            }
        });
    },
    // HÀM LỌC KHI NHẤN VÀO BADGE
    filterType: (type) => {
        currentFilter = type;
        // Cập nhật UI (active badge)
        $('.btn-filter').removeClass('bg-secondary text-white bg-info bg-warning').addClass('text-secondary text-info text-warning');
        if (type === 'all') $('#btnFilterAll').addClass('bg-secondary text-white');
        if (type === 'git') $('#btnFilterGit').addClass('bg-info text-white');
        if (type === 'group') $('#btnFilterGroup').addClass('bg-warning text-white');

        FO_DASH.instance.draw(); // Vẽ lại bảng để thực thi search.push
    },
    // hàm show reservation name
    // HÀM ĐIỀU HƯỚNG URL LINH HOẠT
    switchUrl: (isShowRes) => {
        let baseUrl = '';

        // 1. Xác định Base URL dựa trên Module đang đứng (RS, IH, hay RSIH)
        switch (FO_DASH.currentModule) {
            case 'rs': baseUrl = 'reservation-list'; break;
            case 'ih': baseUrl = 'inhouse-list'; break;
            case 'rsih': baseUrl = 'reservation-ih-list'; break;
        }

        // 2. Ghép hậu tố: Nếu Uncheck (Gom nhóm) thì thêm số '2'
        const suffix = isShowRes ? '' : '2';
        const finalUrl = `/fo/${baseUrl}${suffix}`;

        console.log("==> Gọi API:", finalUrl);

        // 3. Thực thi nạp dữ liệu (DataTables tự động hiện Loading)
        if (FO_DASH.instance) {
            FO_DASH.instance.ajax.url(finalUrl).load();
        }
    },

    reload: () => {
        if (FO_DASH.instance) FO_DASH.instance.ajax.reload(null, false);
    },

    // HÀM RELOAD 
    reload: function () {
        if (FO_DASH.instance) {
            // 1. Hiệu ứng xoay icon cho chuyên nghiệp
            const $btn = $('.fa-sync-alt');
            $btn.addClass('fa-spin');

            // 2. Gọi DataTables nạp lại JSON từ Backend
            // null: giữ nguyên trang hiện tại, false: không reset phân trang
            FO_DASH.instance.ajax.reload(() => {
                $btn.removeClass('fa-spin'); // Dừng xoay khi xong
                Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Đã cập nhật dữ liệu mới', showConfirmButton: false, timer: 1500 });
            }, false);
        }
    },
    switchModule: (type) => {
        FO_DASH.currentModule = type; // Lưu lại phân hệ vừa chọn
        // LƯU LẠI VÀO TRÌNH DUYỆT
        localStorage.setItem('fo_last_module', type);

        const isShowRes = $('#chkShowResName').is(':checked');

        let url = '';
        let label = '';
        let colorClass = '';

        switch (type) {
            case 'rs': // Mode 1
                $('#chkShowResName').prop('checked', false);
                url = '/fo/reservation-list2';
                label = '<i class="fas fa-calendar-alt me-1"></i> RESERVATION';
                colorClass = 'text-primary';
                break;
            case 'ih': // Mode 2
                $('#chkShowResName').prop('checked', false);
                url = '/fo/inhouse-list2';
                label = '<i class="fas fa-bed me-1"></i> IN-HOUSE';
                colorClass = 'text-success';
                break;
            case 'rsih': // Mode 0
                $('#chkShowResName').prop('checked', false);
                url = '/fo/reservation-ih-list2';
                label = '<i class="fas fa-history me-1"></i> RES_IH';
                colorClass = 'text-info';
                break;
        }
        console.log('call ' + url)
        // 1. Cập nhật giao diện nút Dropdown (đổi chữ và đổi màu)
        $('#ddlModule').html(label)
            .removeClass('text-primary text-success text-info')
            .addClass(colorClass);

        // 2. Gọi API load lại dữ liệu (Cấu trúc JSON giống hệt nên bảng tự vẽ lại)
        if (FO_DASH.instance) {
            FO_DASH.instance.ajax.url(url).load();
        }
    },
    // xử lý phần sign
    // Biến tạm để giữ thông tin dòng đang chọn
    selectedRow: {},

    openSignProcess: function (folio, group, idAdd) {
        // 1. Lưu thông tin để dùng cho bước Gửi
        this.selectedRow = { folio, group, idAdd };

        // Gán chính xác vào selectedData
        this.selectedData = {
            folio: folio,    // Chính là row.FFolioNum truyền vào
            group: group,    // Chính là row.SortGroup truyền vào
            idAdd: idAdd     // Chính là row.IdAddition truyền vào
        };

        console.log("Dữ liệu đã nạp:", this.selectedData); // Debug kiểm tra
        // Tự động load danh sách thiết bị Online ngay khi mở modal
        this.loadOnlineDevices();

        // 2. Hiện Modal chọn Mẫu & Thiết bị (Modal này bạn đã tạo ở bước trước)
        $('#modalSelectSign').modal('show');
        $('#info-booking-sign').text(`Đang xử lý Folio: ${folio} | Group: ${group || 'Lẻ'}`);

        // 3. Tải danh sách Mẫu (Chỉ lấy FO - REGCARD/CONFIRM)
        $.get('/fo/templates/list?module=FO', (res) => {
            let html = res.map(t => `<option value="${t.TemplateID}">${t.TemplateName}</option>`).join('');
            $('#sign-select-tpl').html(html);
        });

        // 4. Tải danh sách iPad đang Online tại quầy
        $.get('/api/v1/devices/online-list?module=FO', (res) => {
            let html = res.map(d => `
                <button class="list-group-item list-group-item-action p-2 small device-item" 
                        onclick="FO_DASH.actions.selectDevice('${d.DeviceID}', this)">
                    <i class="fas fa-tablet-alt me-2"></i> ${d.DeviceName} [${d.DeviceID}]
                </button>
            `).join('');
            $('#list-devices-online').html(html || '<div class="text-danger p-2">Không có iPad nào Online!</div>');
        });

    },

    loadOnlineDevices: function () {
        $.get('/api/v1/devices/online-list?module=FO', (res) => {
            let html = '';
            res.forEach(d => {
                // Giả sử API trả về thêm trạng thái IsBusy (1 nếu có hồ sơ chưa ký)
                let statusCls = d.IsBusy ? 'bg-warning' : 'bg-success';
                let statusTxt = d.IsBusy ? 'ĐANG KÝ' : 'RẢNH';
                let disabledAttr = d.IsBusy ? 'disabled style="opacity:0.6; cursor:not-allowed;"' : '';

                html += `
                <button type="button" class="list-group-item list-group-item-action p-2 small device-item" 
                        ${disabledAttr} onclick="FO_DASH.actions.selectDevice('${d.DeviceID}', this)">
                    <span class="badge ${statusCls} me-2">${statusTxt}</span>
                    <span class="fw-bold">${d.DeviceName}</span>
                </button>`;
            });
            $('#list-devices-online').html(html);
        });
    },

    // Hàm chọn thiết bị (để bật nút Gửi)
    selectDevice: function (deviceId, el) {
        $('.device-item').removeClass('active bg-primary text-white');
        $(el).addClass('active bg-primary text-white');

        // Lưu ID thiết bị đã chọn vào biến tạm
        this.selectedData.deviceId = deviceId;

        // Mở khóa nút "XÁC NHẬN GỬI KÝ"
        $('#btn-confirm-send').prop('disabled', false);
    },

    // 2. Hàm thực hiện gửi (Sửa lại payload cho khớp)
    sendToQueue: function () {
        const tplId = $('#sign-select-tpl').val();
        const deviceId = this.selectedData.deviceId;

        if (!deviceId) {
            Swal.fire("Lỗi", "Vui lòng chọn một thiết bị (iPad) để ký!", "warning");
            return;
        }

        const payload = {
            ModuleName: "FO",
            RefType: "BOOKING",
            // Lấy từ biến tạm đã gán ở bước 1
            RefID: this.selectedData.folio,
            FolioNum: this.selectedData.folio,
            GroupCode: this.selectedData.group === 'null' ? null : this.selectedData.group,
            IdAddition: parseInt(this.selectedData.idAdd),
            TemplateID: parseInt(tplId),
            DeviceID: deviceId
            // CreatedBy: Server tự lấy từ session như đã bàn
        };
        console.log(payload);
        $.ajax({
            url: '/api/v1/queue/send',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(payload),
            success: function (res) {
                Swal.fire("Thành công", "Hồ sơ đã gửi đến iPad!", "success");
                $('#modalSelectSign').modal('hide');
            },
            error: function (err) {
                Swal.fire("Lỗi", err.responseJSON?.detail || "Không thể gửi hồ sơ", "error");
            }
        });
    }
};
// 3. EVENT XỬ LÝ RIÊNG CHO ĐIỆN THOẠI (Chạm để hiện InfoBox)
$(document).on('click', '.btn-filter-stat', function () {
    // Chỉ xử lý trên màn hình nhỏ (Mobile)
    if (window.innerWidth <= 768) {
        const paxInfo = $(this).attr('data-pax');
        $('#paxInfoBox').removeClass('d-none');
        $('#lblPaxDetail').text(paxInfo);

        // Hiệu ứng highlight nhẹ để báo hiệu đã nhận lệnh
        $('#lblPaxDetail').css('color', '#dc3545').delay(200).queue(function (next) {
            $(this).css('color', '#007bff');
            next();
        });
    }
});
// 4. EVENTS
$(document).ready(() => {
    FO_DASH.actions.init();
    // SỰ KIỆN KHI NHẤN CHECKBOX show reservation
    $(document).on('change', '#chkShowResName', function () {
        const isChecked = $(this).is(':checked');

        // Gọi hàm đổi URL
        FO_DASH.actions.switchUrl(isChecked);
    });

    // KHỞI TẠO THỦ CÔNG DROPDOWN (Để chắc chắn nó hoạt động) rs. ih, rsih
    var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'))
    var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl)
    });

    // F5 XONG THÌ TỰ ĐỘNG CHẠY LẠI MODULE CUỐI CÙNG
    FO_DASH.actions.switchModule(FO_DASH.currentModule);

    // drop down ... ký
    $(document).on('shown.bs.dropdown', '.dropdown', function () {
        // Tìm cái menu vừa được mở
        const menu = $(this).find('.dropdown-menu');

        // Bốc nó ra khỏi table và gắn vào body
        $('body').append(menu.detach());

        // Tính toán vị trí dựa trên cái nút bấm
        const offset = $(this).offset();
        menu.css({
            'display': 'block',
            'top': offset.top + $(this).outerHeight(),
            'left': offset.left - menu.outerWidth() + $(this).outerWidth()
        });
    });

    $(document).on('hidden.bs.dropdown', '.dropdown', function () {
        // Khi đóng thì dọn dẹp hoặc để Bootstrap tự lo
        $('.dropdown-menu').css('display', '');
    });
});
