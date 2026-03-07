const UI = {
    // Vẽ nút Sửa/Xóa dựa trên quyền
    renderTableActions: (id, editPerm, delPerm, editFnName, delFnName) => {
        let buttons = '';
        if (Auth.has(editPerm)) {
            buttons += `<button class="btn btn-sm btn-info me-1" onclick="${editFnName}(${id})">${t('btn_edit')}</button>`;
        }
        if (Auth.has(delPerm)) {
            buttons += `<button class="btn btn-sm btn-danger" onclick="${delFnName}(${id})">${t('btn_delete')}</button>`;
        }
        return buttons || `<span class="text-muted">${t('view_only')}</span>`;
    }
};