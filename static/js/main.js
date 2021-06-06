$(document).ready(function () {
    const MYHEIGHT = 300;
    require.config({
        baseUrl: "static/js",
        paths: {
            ace: "ace/lib/ace"
        }
    })
    require([
        'ace/ace',
        'ace/ext/language_tools',
    ], function (ace) {
        ace.require("ace/ext/language_tools");

        ids = ["editor-domain", "editor-problem", "editor-domain-2", "editor-problem-2"]
        editors = []
        for (let i = 0; i < 4; i++) {
            var editor = ace.edit(ids[i]);
            editor.setTheme("ace/theme/textmate");
            editor.getSession().setMode("ace/mode/pddl");
            editor.setOptions({
                fontSize: "14pt",
                enableBasicAutocompletion: true,
                enableSnippets: true,
                enableLiveAutocompletion: true,
            });
            editor.setBehavioursEnabled(true);
            editors.push(editor)
        }
        var editor_d = editors[0];
        var editor_p = editors[1]
        var editor_d2 = editors[2]
        var editor_p2 = editors[3]

        function resizeAce() {
            $(".editor").height(window.innerHeight - MYHEIGHT);
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
            $("#download").attr("disabled", true);
            $("#tool_execute").attr("disabled", false);
            $("#tool_compile").prop("disabled", false);
            editor_d.setValue("");
            editor_p.setValue("");
            editor_d2.setValue("");
            editor_p2.setValue("");
            $("#input-tab").tab("show");
            $("#policy_text").html("");
            $("#form_goal_c").val("");
            $("#form_goal_p").val("");
            d3.select("#compile_graph").select("svg").session_destroy;
            d3.select("#policy_graph").select("svg").session_destroy;
            $.ajax({
                url: "/load",
                type: "GET",
                data: {jsdata: $("#example_select").val()},
                success: function (response) {
                    $("#form_goal").val(response.formula);
                    editor_d.setValue(response.domain);
                    editor_p.setValue(response.problem);
                    d3.select("#compile_graph").select("svg").session_destroy;
                    d3.select("#policy_graph").select("svg").session_destroy;
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
                $(this).html(
                    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...'
                );
                editor_d2.setValue("");
                editor_p2.setValue("");
                d3.select("#compile_graph").select("svg").session_destroy;
                d3.select("#policy_graph").select("svg").session_destroy;
                $.ajax({
                    url: "/api/compile",
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
                            width: window.innerWidth - MYHEIGHT,
                            height: window.innerHeight - MYHEIGHT,
                            fit: false
                        }).transition(function () {
                            return d3.transition("main")
                                .ease(d3.easeLinear)
                                .delay(500)
                                .duration(1500);
                        }).renderDot(response.dfa);
                        document.getElementById("tool_compile").innerHTML = 'Compile \n' +
                            '                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"\n' +
                            '                                 class="bi bi-gear-fill" viewBox="0 0 16 16">\n' +
                            '                                <path d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.858z"/>\n' +
                            '                            </svg>';
                        $("#tool_execute").attr("disabled", false);
                        $("#tool_compile").attr("disabled", false);
                        $("#download").attr("disabled", false);
                        $('#outputc-tab').tab('show');
                        $("#toast-body").html("Elapsed time: " + response.elapsed_time + " s");
                        var myAlert = document.getElementById('toast');
                        var bsAlert = new bootstrap.Toast(myAlert);
                        bsAlert.show();
                    },
                    error: function (xhr) {
                        alert(xhr.error)
                    }
                });
            } else {
                alert("Make sure you provide all the required input!");
            }
        });

        // API :plan
        $("#tool_execute").click(function () {
            if ($("#form_goal").val() !== '' && editor_d.getValue() !== '' && editor_p.getValue() !== '') {
                $(this).attr("disabled", true);
                $("#tool_compile").attr("disabled", true);
                $("#policy_graph").html("");
                $('#policy_text').css('height', window.innerHeight - MYHEIGHT);
                $(this).html(
                    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...'
                );
                editor_d2.setValue("");
                editor_p2.setValue("");
                var policy_type = 0;
                d3.select("#compile_graph").select("svg").session_destroy;
                d3.select("#policy_graph").select("svg").session_destroy;
                if ($("#btnstrong").is(":checked")) {
                    policy_type = 1;
                }
                const chosen_planner = $("#planner_select").val();
                if (chosen_planner === "prp" && policy_type === 1) {
                    alert("PRP does not support strong policies.");
                    $("#tool_compile").attr("disabled", false);
                    $("#tool_execute").attr("disabled", false);
                    document.getElementById("tool_execute").innerHTML = 'Compile + Plan\n' +
                        '                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"\n' +
                        '                                 class="bi bi-gear-fill" viewBox="0 0 16 16">\n' +
                        '                                <path d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.858z"/>\n' +
                        '                            </svg>';
                } else {
                    $.ajax({
                        url: "/api/plan",
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
                                width: window.innerWidth - MYHEIGHT,
                                height: window.innerHeight - MYHEIGHT,
                                fit: false
                            }).renderDot(response.dfa);
                            document.getElementById("tool_execute").innerHTML = 'Compile + Plan\n' +
                                '                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"\n' +
                                '                                 class="bi bi-gear-fill" viewBox="0 0 16 16">\n' +
                                '                                <path d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.858z"/>\n' +
                                '                            </svg>';
                            $("#tool_execute").attr("disabled", false);
                            $("#tool_compile").attr("disabled", false);

                            if (response.policy_found) {
                                // everything went good
                                $("#policy_text").html(response.policy_txt);
                                d3.select("#policy_graph").graphviz({
                                    width: window.innerWidth - MYHEIGHT,
                                    height: window.innerHeight - MYHEIGHT,
                                    fit: true
                                }).transition(function () {
                                    return d3.transition("main")
                                        .ease(d3.easeLinear)
                                        .delay(500)
                                        .duration(1500);
                                }).renderDot(response.policy_dot);
                            } else {
                                if (response.policy_txt !== "") {
                                    $("#policy_text").html(response.policy_txt);
                                    $("#policy_graph").html("No policy found. See text for more details.");
                                } else {
                                    alert(response.error)
                                }
                            }
                            $("#download").attr("disabled", false);
                            $('#outputp-tab').tab('show');
                            $("#toast-body").html("Elapsed time: " + response.elapsed_time + " s");
                            var myAlert = document.getElementById('toast');
                            var bsAlert = new bootstrap.Toast(myAlert);
                            bsAlert.show();
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