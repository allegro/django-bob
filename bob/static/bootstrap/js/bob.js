/*jslint unparam: true */
/*global jQuery: false */
var djangoBob = function ($) {
    'use strict';
    var isConditionMet,
        bindAjaxUpdate,
        bindDependencies,
        setFieldValue;

    isConditionMet = function (dependencyValue, value) {
        if ($.isArray(dependencyValue)) {
            return dependencyValue.indexOf(value) !== -1;
        } else if (dependencyValue === null) {
            return true;
        } else if (Object.prototype.toString.call(dependencyValue) &&
                   Object.prototype.toString.call(dependencyValue)) {
            return JSON.stringify(dependencyValue) === JSON.stringify(value);
        }
        return dependencyValue === value;
    };

    setFieldValue = function (field, value) {
        var $field = $(field);
        if (value == null) {
            return;
        }
        if ($field.attr('type') == "checkbox") {
            $field.prop("checked", value);
        } else if ($.isArray(value) && $field.is('select')) {
            $field.children().remove();
            $.each(value[1], function(i, el) {
                $field.append($('<option></option>').val(el[0]).html(el[1]))
            });
            $field.val(value[0]);
        } else {
            $field.val(value);
        }
    };

    bindAjaxUpdate = function (master, slave, value, options) {
        var slavesName = "dependencySlaves";
        var slaveDescription = {
            field: slave,
            value: value,
            pageLoadUpdate: !!(options.page_load_update)
        };
        var url = options.url;

        function pageLoadCondition(pageLoadUpdate, eventOptions) {
            // returns false if and only if this is page load event and code
            // should not be executed, it means pageLoadUpdate is false and
            // this is page load event
            return pageLoadUpdate || !(
                typeof eventOptions !== "undefined" && eventOptions.pageLoad
            );
        }

        if (typeof master.data(slavesName) === "undefined") {
            master.data(slavesName, [slaveDescription]);
            master.change(function (event, eventOptions) {
                if (this.value === '') {
                    return;
                }
                var passedSlaves = [],
                    slavesNames = $(this).data(slavesName),
                    slavesNamesLength = slavesNames.length,
                    slaveObj;
                for (var i = 0; i < slavesNamesLength; i++) {
                    slaveObj = slavesNames[i];
                    if (isConditionMet(value, slaveObj.value)) {
                        if (pageLoadCondition(
                                slaveObj.pageLoadUpdate, eventOptions)) {
                            passedSlaves.push(slaveObj);
                            slaveObj.field.addClass('value-loading');
                        }
                    }
                }

                if (passedSlaves.length > 0) {
                    $.ajax(url, {
                        data: {
                            value: this.value
                        },
                        dataType: "json",
                        complete: function(request, status) {
                            var slaveObj;
                            for (var i = 0; i < passedSlaves.length; i++) {
                                slaveObj = passedSlaves[i];
                                slaveObj.field.removeClass('value-loading');
                            }
                        },
                        success: function(data, status, request) {
                            var id,
                                slaveObj;
                            for (var i = 0; i < passedSlaves.length; i++) {
                                slaveObj = passedSlaves[i];
                                id = (slaveObj.field.attr('name') ||
                                    slaveObj.field.attr('id').substr(3));
                                if (typeof(data[id]) !== "undefined") {
                                    setFieldValue(slaveObj.field, data[id]);
                                    if (slaveObj.field.prop('type') === 'hidden') {
                                        slaveObj.field.
                                            next('.uneditable-input').html(
                                                slaveObj.field.val()
                                            );
                                    }
                                }
                            }
                        },
                        type: "POST"
                    });
                }
            });
        } else {
            master.data(slavesName).push(slaveDescription);
        }
    };

    bindDependencies = function (form, dependencies) {
        $.each(dependencies, function (i, dep) {
            var master, slave, slaveCtrl;
            master = $('#id_' + dep.master);
            slave = $('#id_' + dep.slave);
            if (slave.length == 0) {
                slave = $('[name="' + dep.slave + '"]');
            }
            slaveCtrl = slave.parents('.control-group');
            if (dep.action === "REQUIRE") {
                master.change(function () {
                    if (isConditionMet(master.val())) {
                        $(slaveCtrl).find('label').addClass('required');
                    } else {
                        $(slaveCtrl).find('label').removeClass('required');
                    }
                });
            } else if (dep.action === "SHOW") {
                master.change(function () {
                    if (isConditionMet(master.val())) {
                        slave.removeAttr('disabled');
                        slaveCtrl.show();
                    } else {
                        slave.attr('disabled', 'disabled');
                        slaveCtrl.hide();
                    }
                });
            } else if (dep.action === "AJAX_UPDATE") {
                bindAjaxUpdate(master, slave, dep.value, dep.options);
            }
            master.trigger("change", {
                pageLoad: true
            });
        });
    };

    return {
        isConditionMet: isConditionMet,
        bindAjaxUpdate: bindAjaxUpdate,
        setFieldValue: setFieldValue,
        bindDependencies: bindDependencies
    }
}(jQuery);

$(document).ready(function () {
    $('.bob-select-all').click(function () {
        var table = $(this).closest('table');
        table.find('input[name="select"]').prop('checked', true);
        table.find('input[name="items"]').prop('checked', true);
    });
    $('.bob-select-none').click(function () {
        var table = $(this).closest('table');
        table.find('input[name="select"]').prop('checked', false);
        table.find('input[name="items"]').prop('checked', false);
        table.find('input[name="selectall"]').prop('checked', false);
    });
    $('.bob-select-toggle').click(function () {
        var table = $(this).closest('table');
        table.find('input[name="select"]').each(function () {
            this.checked = !this.checked;
        });
        table.find('input[name="items"]').each(function () {
            this.checked = !this.checked;
        });
        table.find('input[name="selectall"]').prop('checked', false);
    });
    $('.datepicker').datepicker({autoclose: true}).click(function () {
        $('input.datepicker').not(this).datepicker('hide');
    });
    $.each($('form'), function (i, form) {
        if (form.dataset.bobDependencies !== undefined) {
            djangoBob.bindDependencies(
                form,
                $.parseJSON(form.dataset.bobDependencies)
            );
        }
    });
    $('.help-tooltip').tooltip();
});
