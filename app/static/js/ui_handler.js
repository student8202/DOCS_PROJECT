// Đảm bảo CoreUI Navigation khởi tạo đúng
$(document).ready(function() {
    // tính năng Dropdown (đóng/mở menu con) hoạt động
    const nav = document.querySelectorAll('.sidebar-nav');
    nav.forEach(el => {
        const navigation = coreui.Navigation.getInstance(el);
    });
    // Tự động mở menu cha nếu có menu con đang active
    $('.nav-group-items .nav-link.active').closest('.nav-group').addClass('show');
});
