/**
 * LaVie Project - UI Handler
 * Xử lý đóng/mở Sidebar và lưu trạng thái cho CoreUI 5
 */

// function toggleSidebar() {
//     const sidebarEl = document.querySelector('#sidebar');
//     if (!sidebarEl) return;

//     // Lấy Instance của CoreUI Sidebar
//     const sidebar = coreui.Sidebar.getInstance(sidebarEl);

//     if (window.innerWidth < 992) {
//         // 1. Trên Mobile: Dùng hàm toggle mặc định (hiện menu bay)
//         if (sidebar) sidebar.toggle();
//     } else {
//         // 2. Trên Desktop: Tự thêm/bớt class sidebar-hide để ép Wrapper dãn 100%
//         sidebarEl.classList.toggle('sidebar-hide');
        
//         // Lưu trạng thái vào localStorage
//         const isHidden = sidebarEl.classList.contains('sidebar-hide');
//         localStorage.setItem('sidebar_hidden', isHidden);
//     }
// }

// // Khi trang load xong, khôi phục lại trạng thái cũ
// $(document).ready(function() {
//     const sidebarEl = document.querySelector('#sidebar');
//     if (sidebarEl) {
//         const isHidden = localStorage.getItem('sidebar_hidden') === 'true';
        
//         // Chỉ áp dụng ẩn trên Desktop khi load trang để tránh lỗi giao diện mobile
//         if (isHidden && window.innerWidth >= 992) {
//             $(sidebarEl).addClass('sidebar-hide');
            
//             // Mẹo nhỏ: Tạm tắt transition lúc load để không bị cảm giác "trượt" khi mới mở web
//             $('.wrapper').css('transition', 'none');
//             setTimeout(() => {
//                 $('.wrapper').css('transition', '');
//             }, 200);
//         }
//     }
// });
