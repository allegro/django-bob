/* Djid extensions for jqGrid */

(function ($) {
    $.fn.fmatter.djid_link = function (value) {
        var url, label;
        return Mustache.render(
            '<a href={{url}}>{{label}}</a>', {
                'url': value[0],
                'label': value[1],
            }
        )
    };
})(jQuery);
