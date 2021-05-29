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

        // input tab
        var editor_d = ace.edit("editor-domain");
        editor_d.setTheme("ace/theme/monokai");
        editor_d.getSession().setMode("ace/mode/pddl");
        editor_d.setOption("fontSize", "14pt");
        editor_d.setOptions({
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: true,
            // minLines: 50,
            // maxLines: Infinity
        });
        editor_d.setBehavioursEnabled(false);

        var editor_p = ace.edit("editor-problem");
        editor_p.setTheme("ace/theme/monokai");
        editor_p.getSession().setMode("ace/mode/pddl");
        editor_p.setOption("fontSize", "14pt");
        editor_p.setOptions({
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: true
        });
        editor_p.setBehavioursEnabled(true);

        // output tab
        var editor_d2 = ace.edit("editor-domain-2");
        editor_d2.setTheme("ace/theme/monokai");
        editor_d2.getSession().setMode("ace/mode/pddl");
        editor_d2.setOption("fontSize", "14pt");
        editor_d2.setOptions({
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: true
        });
        editor_d2.setBehavioursEnabled(true);

        var editor_p2 = ace.edit("editor-problem-2");
        editor_p2.setTheme("ace/theme/monokai");
        editor_p2.getSession().setMode("ace/mode/pddl");
        editor_p2.setOption("fontSize", "14pt");
        editor_p2.setOptions({
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: true
        });
        editor_p2.setBehavioursEnabled(true);

        function resizeAce() {
            $(".editor").height(window.innerHeight - 300);
            editor_d.resize();
            editor_p.resize();
            editor_d2.resize();
            editor_p2.resize();
        }

        //listen for changes
        $(window).resize(resizeAce);
        //set initially
        resizeAce();

        // API :load
        $("#example_select").change(function () {
            // $("#domain_download").addClass("disabled");
            // $("#problem_download").addClass("disabled");
            $("#tool_execute").attr("disabled", false);
            $("#tool_compile").prop("disabled", false);
            editor_d.setValue("");
            editor_p.setValue("");
            editor_d2.setValue("");
            editor_p2.setValue("");
            $('#input-tab').tab('show');
            $(".graph").html("");
            $("#form_goal_c").val("");
            $("#form_goal_p").val("");
            $.ajax({
                url: "/load",
                type: "GET",
                data: {jsdata: $("#example_select").val()},
                success: function (response) {
                    $("#form_goal").val(response.formula);
                    editor_d.setValue(response.domain);
                    editor_p.setValue(response.problem);
                    // $('.nav-tabs a[href="#inputtab"]').tab('show');
                },
                error: function (xhr) {
                    alert(xhr.error)
                }
            });
        });

        // API :compile
        $("#tool_compile").click(function () {
            if ($("#form_goal").val() !== '' && editor_d.getValue() !== '' && editor_p.getValue() !== '') {
                $(this).attr("disabled", true);
                $("#tool_execute").attr("disabled", true);
                // $("#domain_download").addClass("disabled");
                // $("#problem_download").addClass("disabled");
                // add spinner to button
                $(this).html(
                    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...'
                );
                editor_d2.setValue("");
                editor_p2.setValue("");
                $.ajax({
                    url: "/compile",
                    type: "POST",
                    data: {
                        form_goal: $('#form_goal').val(),
                        form_pddl_domain_in: editor_d.getValue(),
                        form_pddl_problem_in: editor_p.getValue()
                    },
                    success: function (response) {
                        $("#form_goal_c").val(response.formula);
                        $("#form_goal_p").val(response.formula);
                        editor_d2.setValue(response.form_pddl_domain_out);
                        editor_p2.setValue(response.form_pddl_problem_out);
                        d3.select("#compile_graph").graphviz({
                            width: window.innerWidth - 300,
                            height: window.innerHeight - 300,
                            fit: false
                        }).transition(function () {
                            return d3.transition("main")
                                .ease(d3.easeLinear)
                                .delay(500)
                                .duration(1500);
                        }).renderDot(response.dfa);
                        // $("#domain_download").removeClass("disabled");
                        // $("#problem_download").removeClass("disabled");
                        document.getElementById("tool_compile").innerHTML = 'Compilation only\n' +
                            '                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"\n' +
                            '                                 class="bi bi-gear-fill" viewBox="0 0 16 16">\n' +
                            '                                <path d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.858z"/>\n' +
                            '                            </svg>';
                        $("#tool_execute").attr("disabled", false);
                        $("#tool_compile").attr("disabled", false);
                        $('#outputc-tab').tab('show');
                    },
                    error: function (xhr) {
                        alert(xhr.error)
                    }
                });
            } else {
                alert("Make sure you provide all the required input!");
            }
        });

        // API :compile
        $("#tool_execute").click(function () {
            if ($("#form_goal").val() !== '' && editor_d.getValue() !== '' && editor_p.getValue() !== '') {
                $(this).attr("disabled", true);
                $("#tool_compile").attr("disabled", true);
                $('#policy_text').css('height', window.innerHeight - 300);
                // $("#domain_download").addClass("disabled");
                // $("#problem_download").addClass("disabled");
                // add spinner to button
                $(this).html(
                    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...'
                );
                editor_d2.setValue("");
                editor_p2.setValue("");
                // set strong-cyclic or strong
                var policy_type = 0;
                if ($("#btnstrong").is(":checked")) {
                    policy_type = 1;
                }
                const chosen_planner = $("#planner_select").val();
                if (chosen_planner === "prp" && policy_type === 1) {
                    alert("PRP does not support strong policies.")
                } else {
                    $.ajax({
                        url: "/plan",
                        type: "POST",
                        data: {
                            form_goal: $('#form_goal').val(),
                            form_pddl_domain_in: editor_d.getValue(),
                            form_pddl_problem_in: editor_p.getValue(),
                            planner: chosen_planner,
                            policy_type: policy_type
                        },
                        success: function (response) {
                            $("#form_goal_c").val(response.formula);
                            $("#form_goal_p").val(response.formula);
                            editor_d2.setValue(response.form_pddl_domain_out);
                            editor_p2.setValue(response.form_pddl_problem_out);
                            d3.select("#compile_graph").graphviz({
                                width: window.innerWidth - 300,
                                height: window.innerHeight - 300,
                                fit: false
                            }).transition(function () {
                                return d3.transition("main")
                                    .ease(d3.easeLinear)
                                    .delay(500)
                                    .duration(1500);
                            }).renderDot(response.dfa);
                            // $("#domain_download").removeClass("disabled");
                            // $("#problem_download").removeClass("disabled");
                            document.getElementById("tool_execute").innerHTML = 'Compilation and Policy\n' +
                                '                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"\n' +
                                '                                 class="bi bi-gear-fill" viewBox="0 0 16 16">\n' +
                                '                                <path d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.858z"/>\n' +
                                '                            </svg>';
                            $("#tool_execute").attr("disabled", false);
                            $("#tool_compile").attr("disabled", false);
                            if (response.error) {
                                $("#policy_text").html(response.error);
                                $("#policy_graph").html("No policy found. See text for more details.");
                                alert(chosen_planner + " didn't find the policy. Try with another planner from the list.")
                            } else {
                                $("#policy_text").html(response.policy_txt);
                                d3.select("#policy_graph").graphviz({
                                    width: window.innerWidth - 300,
                                    height: window.innerHeight - 300,
                                    fit: true
                                }).transition(function () {
                                    return d3.transition("main")
                                        .ease(d3.easeLinear)
                                        .delay(500)
                                        .duration(1500);
                                }).renderDot(response.policy_dot);
                            }
                            $('#outputp-tab').tab('show');
                        },
                        error: function (xhr) {
                            alert(xhr.error)
                        }
                    });
                }
            } else {
                alert("Make sure you provide all the required input!");
            }
        });

    })
});