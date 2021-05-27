$(document).ready(function () {
    require.config({
        paths: {
            ace: "static/js/ace/lib/ace"
        }
    })
    require([
        'ace/ace',
        'ace/ext/language_tools',
    ], function (ace, lang_tools) {
        ace.require("ace/ext/language_tools");

        var editor_d = ace.edit("editor-domain");
        editor_d.setTheme("ace/theme/textmate");
        editor_d.getSession().setMode("ace/mode/pddl");
        editor_d.setOption("fontSize", "12pt");
        editor_d.setOptions({
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: true
        });
        editor_d.setBehavioursEnabled(true);

        var editor_p = ace.edit("editor-problem");
        editor_p.setTheme("ace/theme/textmate");
        editor_p.getSession().setMode("ace/mode/pddl");
        editor_p.setOption("fontSize", "12pt");
        editor_p.setOptions({
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: true
        });
        editor_p.setBehavioursEnabled(true);
    })


    function resizeAce() {
        $('#editor-domain').height($(window).height() - 300);
        $('#editor-problem').height($(window).height() - 300);
    }

    //listen for changes
    $(window).resize(resizeAce);
    //set initially
    resizeAce();
});
