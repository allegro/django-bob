/*jslint browser: true */
/*global define*/
/* Djid extensions for jqGrid */

define([
    'jquery',
    'mustache',
    'moment',
    'bootbox',
    'jqGrid'
], function ($, Mustache, moment, bootbox) {
    "use strict";
    $.fn.fmatter.djid_link = function (value) {
        return Mustache.render(
            '<a href={{url}}>{{label}}</a>',
            {
                'url': value[0],
                'label': value[1],
            }
        );
    };

    function Djid(id, params) {
        var new_params, that;
        that = this;
        new_params = $.extend(
            {},
            this.default_params,
            params
        );
        this.id = id;
        this.pager_id = '#' + id + '-pager';
        new_params.pager = this.pager_id;
        new_params.url = '/djid/' + id + '/';
        this.jqgrid = $('#' + id).jqGrid(new_params);
        this.jqgrid.navGrid(this.pager_id, {
            'edit': false,
            'add': false,
            'del': false,
            'search': false
        });
        this.jqgrid.filterToolbar();
        this.jqgrid.get(0).toggleToolbar();
        this.jqgrid.navButtonAdd(this.pager_id, {
            caption: '',
            buttonicon: 'ui-icon-search',
            onClickButton: function () {
                this.toggleToolbar();
            }
        });
        this.jqgrid.navButtonAdd(this.pager_id, {
            caption: '',
            buttonicon: 'ui-icon-carat-1-e',
            onClickButton: function () {
                that.get_report();
            },
            id: this.get_id('csv', true)

        });
    }

    Djid.prototype.default_params = {
        datatype: "json",
        mtype: "GET",
        multiSort: true,
        scroll: true,
    };

    Djid.prototype.get_report = function () {
        this.add_progress();
        this.initial_request();
    };

    Djid.prototype.initial_request = function () {
        var data, that;
        that = this;
        data = this.jqgrid.jqGrid('getGridParam', 'postData');
        $.ajax({
            url: this.get_url('start_report'),
            data: data,
            success: function (result) {
                that.handle_initial_request(result);
            },
            headers: {
                'Accept': 'text/csv'
            },
            dataType: 'json'
        });
    };

    Djid.prototype.handle_initial_request = function (result) {
        var data, that;
        that = this;
        this.job_id = result.job_id;
        data = {'job_id': this.job_id};
        this.long_interval_handle = window.setInterval(function () {
            $.ajax({
                url:that.get_url('update_status'),
                data: data,
                success: that.handle_update,
                context: that
            });
        }, 5000);
    };


    Djid.prototype.set_eta = function (value) {
        if (value === null) {
            this.eta = null;
        } else {
            this.eta = moment.Duration(value, 'seconds');
        }
    };

    Djid.prototype.update_eta_display = function () {
        if (!this.eta) {
            return;
        }
        $(this.eta_el).html(Mustache.render('ETA: {{hours}}:{{minutes}}:{{seconds}}', {
            hours: this.pad(this.eta.hours()),
            minutes: this.pad(this.eta.minutes()),
            seconds: this.pad(this.eta.seconds())
        }));
    };

    Djid.prototype.handle_update = function (result) {
        var that, data;
        that = this;
        if (result.failed) {
             clearInterval(this.long_interval_handle);
             clearInterval(this.short_interval_handle);
             this.set_eta(null);
             this.remove_progress();
             bootbox.alert('Failed to generate the report');
             return;
        }
        if (result.finished) {
            clearInterval(this.long_interval_handle);
            clearInterval(this.short_interval_handle);
            this.remove_progress();
            this.set_eta(null);
            data = {'job_id': this.job_id, 'finished': true};
            window.location = (Mustache.render('{{{url}}}?{{{params}}}', {
                url: this.get_url('get_report'),
                params: $.param(data)
            }))
        }
    };

    Djid.prototype.set_progress = function (value) {
        $(this.progress).removeClass('progress-striped active');
        $(this.progress).children('.bar').css(
            'width',
            value.toString() + '%'
        );
    };

    Djid.prototype.get_url = function (action) {
        return Mustache.render('/djid/{{action}}/{{id}}/', {
            id: this.id,
            action: action

        });
    };

    Djid.prototype.add_progress = function () {
        this.progress = $(
            '<div></div>'
        ).attr('id', this.get_id('progress', true));
        $(this.get_id('pager_right')).append(this.progress);
        this.progress.progressbar();
        this.progress.progressbar('option', 'value', false);
    };

    Djid.prototype.remove_progress = function () {
        this.progress.remove();
    };

    Djid.prototype.get_id = function (suffix, drop_hash) {
        var result;
        result = this.id + '-' + suffix;
        if (drop_hash) {
            return result;
        }
        return '#' + result;
    };

    return {
        Djid: Djid
    };
});
