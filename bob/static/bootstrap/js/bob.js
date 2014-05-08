/*jslint unparam: true */
/*global jQuery: false */
var djangoBobConditions = function ($) {
    var checkCondition;

    function leadZeros(value, len) {
        var s = String(value);
        while (s.length < len) {
            s = "0" + s;
        }
        return s;
    }

    function formatSingleValue(val) {
        if (val instanceof Date) {
            return [
                val.getFullYear(),
                leadZeros(val.getMonth() + 1, 2),
                leadZeros(val.getDate(), 2)  // getDate returns month day
            ].join('-');
        } else if (typeof val === "boolean" || val === null) {
            return val;
        } else {
            return String(val);
        }
    }

    function formatValue(val) {
        if ($.isArray(val)) {
            return $.map(val, formatSingleValue);
        } else {
            return formatSingleValue(val);
        }
    }

    var conditions = {
        // declare own condition functions here and
        // in bob.forms.dependency_conditions
        any: function(value, conditionArgs) {
            return true;
        },
        exact: function(value, conditionArgs) {
            // we can assert, that values are string serializable
            return JSON.stringify(formatValue(value)) == JSON.stringify(conditionArgs[0]);
        },
        memberOf: function(value, conditionArgs) {
            return conditionArgs[0].indexOf(formatValue(value)) !== -1;
        },
        notEmpty: function (value, conditionArgs) {
            return (typeof value !== "undefined" &&
                    value !== null &&
                    value !== "");
        }
    };

    met = function(value, condition) {
        var conditionFunc = conditions[condition[0]];
        if (typeof conditionFunc === "undefined") {
            console.error("Condition '" + condition[0] + "' is not defined.");
        } else {
            return conditionFunc(value, condition.slice(1));
        }
    };

    return {
        met: met
    };
}(jQuery);


var djangoBob = function ($) {
    'use strict';
    var bindAjaxUpdate,
        bindDependencies,
        setFieldValue;

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
        $field.trigger("change");
    };

    function pageLoadCondition(pageLoadUpdate, e) {
        // returns false if and only if this is page load event and code
        // should not be executed, it means pageLoadUpdate is false and
        // this is page load event
        return pageLoadUpdate || !e.pageLoad;
    }

    bindAjaxUpdate = function (master, slave, condition, options) {
        var slavesName = "dependencySlaves";
        var slaveDescription = {
            field: slave,
            condition: condition,
            pageLoadUpdate: !!(options.page_load_update)
        };
        var url = options.url;

        if (typeof master.data(slavesName) === "undefined") {
            master.data(slavesName, [slaveDescription]);
            master.change(function (ev) {
                var passedSlaves = [],
                    slavesNames = $(this).data(slavesName),
                    slavesNamesLength = slavesNames.length,
                    slaveObj;
                for (var i = 0; i < slavesNamesLength; i++) {
                    slaveObj = slavesNames[i];
                    if (djangoBobConditions.met(master.val(), slaveObj.condition)) {
                        if (pageLoadCondition(
                                slaveObj.pageLoadUpdate, ev)) {
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
            var masters = $('[id$="-' + dep.master + '"]').add('#id_' + dep.master);
            $.each(masters, function (j, master) {
                master = $(master);
                var slave, slaveCtrl, prefix;
                prefix = master.attr('id').slice(0, -dep.master.length);
                slave = $('#' + prefix + dep.slave);
                if (slave.length == 0) {
                    slave = $('[name="' + dep.slave + '"]');
                }
                slaveCtrl = slave.parents('.control-group');
                if (dep.action === "REQUIRE") {
                    master.change(function () {
                        if (djangoBobConditions.met(master.val(), dep.condition)) {
                            $(slaveCtrl).find('label').addClass('required');
                        } else {
                            $(slaveCtrl).find('label').removeClass('required');
                        }
                    });
                } else if (dep.action === "SHOW") {
                    master.change(function () {
                        if (djangoBobConditions.met(master.val(), dep.condition)) {
                            slave.removeAttr('disabled');
                            slaveCtrl.show();
                        } else {
                            slave.attr('disabled', 'disabled');
                            slaveCtrl.hide();
                        }
                    });
                } else if (dep.action === "CLONE") {
                    master.change(function (ev) {
                        if (pageLoadCondition(dep.options.page_load_update, ev)) {
                            if (djangoBobConditions.met(master.val(), dep.condition)) {
                                slave.val(master.val()).trigger({
                                    type: 'change',
                                    cloneSource: master
                                });
                            }
                        }
                    });
                } else if (dep.action === "AJAX_UPDATE") {
                    bindAjaxUpdate(master, slave, dep.condition, dep.options);
                }
                master.trigger({
                    type: "change",
                    pageLoad: true
                });
            });
        });
    };

    return {
        bindAjaxUpdate: bindAjaxUpdate,
        setFieldValue: setFieldValue,
        bindDependencies: bindDependencies
    };
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
