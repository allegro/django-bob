$(function ($) {
    $('.bob_select-all').click(function () {
        var table = $(this).closest('table')
        table.find('input[name="select"]').prop('checked', true);
        table.find('input[name="items"]').prop('checked', true);
    });
    $('.bob_select-none').click(function () {
        var table = $(this).closest('table')
        table.find('input[name="select"]').prop('checked', false);
        table.find('input[name="items"]').prop('checked', false);
        table.find('input[name="selectall"]').prop('checked', false);
    });
    $('.bob_select-toggle').click(function() {
        var table = $(this).closest('table')
        table.find('input[name="select"]').each(function () {
            this.checked = !this.checked;
        });
        table.find('input[name="items"]').each(function () {
            this.checked = !this.checked;
        });
        table.find('input[name="selectall"]').prop('checked', false);
    });
});