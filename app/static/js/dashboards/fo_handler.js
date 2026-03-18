/**
 * FO DASHBOARD MODULE
 * Cấu hình -> Phụ trợ -> Hành động -> Sự kiện
 */

// 1. CONFIG
const FO_DASH = {
    tableId: '#tblInHouseDash',
    apiUrl: '/fo/inhouse-list2',
    instance: null
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

        FO_DASH.instance = $(FO_DASH.tableId).DataTable({
            ajax: { url: FO_DASH.apiUrl, dataSrc: '' },
            scrollX: true,
            fixedColumns: { left: 2 },
            columns: [
                { data: 'FolioNum', render: d => `<button class="btn btn-xs btn-primary py-0 px-1" onclick="signFolio('${d}')">Ký</button>` }, // 0
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
                { data: 'FirstName', defaultContent: "" }, // 7 (Giá)
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

                // Fix lỗi neo cột
                setTimeout(() => { if (api.fixedColumns) api.fixedColumns().relayout(); }, 10);
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
    switchUrl: (isShowRes) => {
        // Logic chọn URL
        const newUrl = isShowRes ? '/fo/inhouse-list' : '/fo/inhouse-list2';

        // Cập nhật API và nạp lại dữ liệu (load mới hoàn toàn)
        FO_DASH.instance.ajax.url(newUrl).load();

        console.log("Đã đổi sang API:", newUrl);
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
    }
};
// 3. EVENT XỬ LÝ RIÊNG CHO ĐIỆN THOẠI (Chạm để hiện InfoBox)
$(document).on('click', '.btn-filter-stat', function() {
    // Chỉ xử lý trên màn hình nhỏ (Mobile)
    if (window.innerWidth <= 768) {
        const paxInfo = $(this).attr('data-pax');
        $('#paxInfoBox').removeClass('d-none');
        $('#lblPaxDetail').text(paxInfo);
        
        // Hiệu ứng highlight nhẹ để báo hiệu đã nhận lệnh
        $('#lblPaxDetail').css('color', '#dc3545').delay(200).queue(function(next){
            $(this).css('color', '#007bff');
            next();
        });
    }
});
// 4. EVENTS
$(document).ready(() => {
    FO_DASH.actions.init();
    // SỰ KIỆN KHI NHẤN CHECKBOX
    $(document).on('change', '#chkShowResName', function () {
        const isChecked = $(this).is(':checked');

        // Gọi hàm đổi URL
        FO_DASH.actions.switchUrl(isChecked);
    });
});
