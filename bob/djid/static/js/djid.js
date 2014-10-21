/* Djid extensions for jqGrid */

define(['jquery', 'jqGrid', 'mustache'], function ($, jqGrid, Mustache) {
    $.fn.fmatter.djid_link = function (value) {
        var url, label;
        return Mustache.render(
            '<a href={{url}}>{{label}}</a>', {
                'url': value[0],
                'label': value[1],
            }
        )
    };
    function Djid(id, params) {
        var new_params, that;
        that = this;
        new_params = $.extend(
            {}, this.default_params, params
        )
        this.id = id;
        this.pager_id = '#' + id + '-pager';
        new_params['pager'] = this.pager_id;
        new_params['url'] = '/djid/' + id + '/',
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
                that.add_progress()
            },
            id: this.get_id('csv', true)
            
        });
    };
    Djid.prototype.default_params = {
        datatype: "json",
        mtype: "GET",
        multiSort: true,
        scroll: true,
    };
    Djid.prototype.add_progress = function () {
        progress = $('<div></div>').attr('id', this.get_id('progress', true));
        $(this.get_id('pager_right')).append(progress);
        progress.progressbar();
        progress.progressbar('option', 'value', false);
    };
    Djid.prototype.get_id = function(suffix, drop_hash) {
        var result;
        result = this.id + '-' + suffix;
        if (drop_hash) {
            return result;
        } else {
            return '#' + result;
        }
    }
    return {
        Djid: Djid
    };
});

