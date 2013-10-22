(function ($) {

    function AsyncLoader(url) {
        this.url = url;
    }

    AsyncLoader.prototype.start = function() {
        $.ajax({
            url: this.url,
            success: this.handleInitialReq,
            context: this,
        });
    };

    AsyncLoader.prototype.handleInitialReq= function (result, success, response) {
        var that;
        that = this;
        this.jobid = result.jobid;
        $('#async-progress').show();
        this.intervalHandle = setInterval(function () {
            $.ajax({
                url: that.url,
                data: {_report_jobid: that.jobid},
                success: that.handleUpdate,
                context: that,
            });
        }, 4e3);
    };

    AsyncLoader.prototype.handleUpdate = function (result, success, response) {
        if (result.finished) {
            clearInterval(this.intervalHandle);
            window.location = this.url + '?' + $.param(
                    {_report_jobid: this.jobid, _report_finish: true});

        }
    };

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


    function prepareAsync() {
        $('#async-progress').hide();
        $('.async-csv').click(function (ev) {
            new AsyncLoader(window.location + '/csv').start();
            return false;
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
        prepareAsync()
    });
}($));
