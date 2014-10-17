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
        var new_params;
        new_params = $.extend(
            {}, this.default_params, params
        )
        this.id = '#' + id;
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
    }
    Djid.prototype.default_params = {
        datatype: "json",
        mtype: "GET",
        multiSort: true,
        scroll: true,
    }
    return {
        Djid: Djid
    }
});

