from pathlib import Path
from subprocess import TimeoutExpired, PIPE, Popen

from flask import Flask, render_template, request, jsonify, url_for, send_file
from fond4ltlfpltlf.core import execute

import os
import json
import shutil
import time
import signal

from ltlf2dfa.parser.ltlf import LTLfParser
from ltlf2dfa.parser.pltlf import ParsingError, PLTLfParser

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = PACKAGE_DIR / Path("static") / Path("output")
PLANNERS_DIR = PACKAGE_DIR / Path("planners")
PLANNER_DIR = PACKAGE_DIR / PLANNERS_DIR
DOWNLOAD = Path("fond4ltlfpltlf-output")

app = Flask(__name__)

FUTURE_OPS = {"X", "F", "U", "G", "W", "R"}
PAST_OPS = {"Y", "O", "S", "H"}


def launch(cmd):
    """Launch a command."""
    process = Popen(
        args=cmd,
        stdout=PIPE,
        stderr=PIPE,
        preexec_fn=os.setsid,
        shell=True,
        encoding="utf-8",
    )
    try:
        output, error = process.communicate(timeout=30)
        return str(output).strip(), str(error).strip()
    except TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        return None, None


def _call_wrapper(planner, d, p, s="0"):
    """Call the planner wrapper."""
    cmd = f"python {PLANNER_DIR}/{Path(planner)}/{planner}_wrapper.py -d {d} -p {p}"
    if planner != "prp":
        cmd = cmd + f" -s {s}"
    return launch(cmd)


def _compilation(d, p, f):
    """Compile a FOND for temporal extended goals to standard FOND."""
    domain_prime, problem_prime = execute(d, p, f)

    with open(f"{OUTPUT_DIR}/new-domain.pddl", "w+") as d:
        d.write(str(domain_prime))
    with open(f"{OUTPUT_DIR}/new-problem.pddl", "w+") as p:
        p.write(str(problem_prime))

    # dfa computed again. We need to change fond4ltlfpltlf APIs
    if all(c in FUTURE_OPS for c in f if c.isupper()):
        f_parser = LTLfParser()
        try:
            p_formula = f_parser(f)
        except Exception:
            raise ParsingError()

    else:
        assert all(c in PAST_OPS for c in f if c.isupper())
        p_parser = PLTLfParser()
        try:
            p_formula = p_parser(f)
        except Exception:
            raise ParsingError()

    mona_output = p_formula.to_dfa(mona_dfa_out=False)
    mona_output = mona_output.replace("LR", "TB")

    with open(f"{OUTPUT_DIR}/dfa.dot", "w+") as p:
        p.write(mona_output)

    return domain_prime, problem_prime, p_formula, mona_output


@app.route('/')
def index():
    launch(f"rm {OUTPUT_DIR}/* {OUTPUT_DIR}/plan/* {PACKAGE_DIR}/{DOWNLOAD}.zip")
    return render_template("index.html")


@app.route('/load', methods=['GET'])
def load():
    file_path = request.args.get('jsdata')
    try:
        with open(f"{PACKAGE_DIR}/{file_path}", "r") as f:
            return json.load(f)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/download')
def download():
    shutil.make_archive(DOWNLOAD, 'zip', OUTPUT_DIR)
    return send_file(f"{DOWNLOAD}.zip", mimetype='application/zip', as_attachment=True)


@app.route('/compile', methods=['POST'])
def compilation():
    formula = request.form['form_goal']
    in_domain = request.form['form_pddl_domain_in']
    in_problem = request.form['form_pddl_problem_in']

    try:
        c_start = time.perf_counter()
        domain_prime, problem_prime, p_formula, mona_output = _compilation(in_domain, in_problem, formula)
        c_end = time.perf_counter()
        return jsonify({'form_pddl_domain_out': str(domain_prime),
                        'form_pddl_problem_out': str(problem_prime),
                        'formula': str(p_formula),
                        'dfa': str(mona_output),
                        'elapsed_time': str(c_end - c_start)})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/plan', methods=['POST'])
def plan():
    formula = request.form['form_goal']
    in_domain = request.form['form_pddl_domain_in']
    in_problem = request.form['form_pddl_problem_in']
    planner = request.form['planner']
    policy_type = request.form['policy_type']

    try:
        p_start = time.perf_counter()
        domain_prime, problem_prime, p_formula, mona_output = _compilation(in_domain, in_problem, formula)
        dom_path = OUTPUT_DIR / "new-domain.pddl"
        prob_path = OUTPUT_DIR / "new-problem.pddl"

        result = {"form_pddl_domain_out": str(domain_prime),
                  "form_pddl_problem_out": str(problem_prime),
                  "formula": str(p_formula),
                  "dfa": str(mona_output),
                  "policy_found": False,
                  "error": "Policy not found.",
                  "policy_txt": "",
                  "policy_dot": "",
                  "elapsed_time": "-1",}

        ok = False
        if planner == "mynd":
            out, err = _call_wrapper(planner, dom_path, prob_path, policy_type)
            p_end = time.perf_counter()
            if out:
                result["policy_txt"] = out
            elif err:
                result["error"] = err
            else:
                ok = True
        elif planner == "prp":
            out, err = _call_wrapper(planner, dom_path, prob_path)
            p_end = time.perf_counter()
            if out:
                result["policy_txt"] = out
            elif err:
                result["error"] = err
            else:
                ok = True
                # Path(f"{OUTPUT_DIR}/plan/policy-translated.out").rename(f"{OUTPUT_DIR}/plan/policy.txt")
        else:
            assert planner == "fondsat"
            out, err = _call_wrapper(planner, dom_path, prob_path, policy_type)
            p_end = time.perf_counter()
            if out:
                result["policy_txt"] = out
            elif err:
                result["error"] = err
            else:
                ok = True

        result["elapsed_time"] = str(p_end - p_start)
        if ok:
            result["policy_found"] = True
            result["error"] = ""
            result["policy_txt"] = str(open(f"{OUTPUT_DIR}/plan/policy.txt", "r").read())
            result["policy_dot"] = str(open(f"{OUTPUT_DIR}/plan/policy.dot", "r").read())

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == "__main__":
    app.run(debug=True)
