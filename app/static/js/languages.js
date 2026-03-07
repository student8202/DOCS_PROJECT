// 1. Chỉ lấy từ localStorage, không gán mặc định 'vi' ở đây để kiểm tra logic trình duyệt
let currentLang = localStorage.getItem('appLang');

if (!currentLang) {
    const browserLang = navigator.language.split('-')[0]; // Lấy 'vi' hoặc 'en'
    // Kiểm tra nếu trình duyệt là 'vi' hoặc 'en' thì lấy, không thì mặc định 'vi'
    currentLang = ['vi', 'en'].includes(browserLang) ? browserLang : 'vi';
    localStorage.setItem('appLang', currentLang);
}

let translations = {};

// Hàm tải file JSON ngôn ngữ
async function loadLanguage(lang) {
    try {
        const response = await fetch(`/static/lang/${lang}.json`);
        translations = await response.json();
        currentLang = lang;
        applyLanguage(); // Dịch Label HTML
        if (typeof reloadDataTableLanguage === 'function') {
            reloadDataTableLanguage();
        } else {
            console.warn("Hàm reloadDataTableLanguage chưa sẵn sàng.");
        }
    } catch (error) {
        console.error("Lỗi tải ngôn ngữ:", error);
    }
}
/*
Hàm applyLanguage của bạn chỉ là "người đi phát kẹo", còn hàm t(key) mới là "người lấy kẹo từ trong túi ra". 
Nếu trong túi (JSON) kẹo được chia vào các ngăn nhỏ (buttons, messages), hàm t cũ sẽ không biết đường tìm.
*/
// Hàm lấy text theo key (và cả Hỗ trợ key dạng 'buttons.save')
function t(key, params = {}) {
    // Tách key bằng dấu chấm và duyệt sâu vào object translations
    let text = key.split('.').reduce((obj, i) => (obj ? obj[i] : null), translations);

    // Nếu không tìm thấy key, trả về chính cái key đó
    if (!text) text = key;

    // Thay thế tham số {count}, {name}...
    Object.keys(params).forEach(p => {
        text = text.replace(new RegExp(`{${p}}`, 'g'), params[p]);
    });

    return text;
}

// Hàm quét và dịch các thẻ HTML
function applyLanguage() {
    $('[data-i18n]').each(function () {
        const key = $(this).data('i18n');
        $(this).html(t(key));
    });
    $('[data-i18n-placeholder]').each(function () {
        const key = $(this).data('i18n-placeholder');
        $(this).attr('placeholder', t(key));
    });
}

// Tự động load khi trang mở
$(document).ready(() => loadLanguage(currentLang));

