(function ($) {
    function bindDependencies(form, dependencies) {
        $.each(dependencies, function (i, dep) {
            var master, slave, slaveCtrl;
            master = $('#id_' + dep.master);
            slave = $('#id_' + dep.slave);
            slaveCtrl = slave.parents('.control-group');
            if ($.isArray(dep.value)) {
                function condition(value) {
                    return dep.value.indexOf(value) !== -1;
                }
            } else {
                function condition(value) {
                    return dep.value === value;
                }
            }
            master.change(function () {
                if(condition(master.val())) {
                    slave.removeAttr('disabled');
                    slaveCtrl.show();
                } else {
                    slave.attr('disabled', 'disabled');
                    slaveCtrl.hide();
                }
            });
            master.change();
        });
    }

    $(function ($) {
        $('.bob-select-all').click(function () {
            var table = $(this).closest('table')
            table.find('input[name="select"]').prop('checked', true);
            table.find('input[name="items"]').prop('checked', true);
        });
        $('.bob-select-none').click(function () {
            var table = $(this).closest('table')
            table.find('input[name="select"]').prop('checked', false);
            table.find('input[name="items"]').prop('checked', false);
            table.find('input[name="selectall"]').prop('checked', false);
        });
        $('.bob-select-toggle').click(function() {
            var table = $(this).closest('table')
            table.find('input[name="select"]').each(function () {
                this.checked = !this.checked;
            });
            table.find('input[name="items"]').each(function () {
                this.checked = !this.checked;
            });
            table.find('input[name="selectall"]').prop('checked', false);
        });
        $('.datepicker').datepicker({autoclose: true}).click(function(){
            $('input.datepicker').not(this).datepicker('hide');
        });
        $.each($('form'), function (i, form) {
            if (form.dataset.bobDependencies !== undefined) {
                bindDependencies(
                    form, $.parseJSON(form.dataset.bobDependencies));
            }
        });
    });
}($));
