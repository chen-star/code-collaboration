$(document).ready(function () {
    $("input#fileSearch").autocomplete({
        source: "/codereviewer/search",
        minLength: 1,
    });
});