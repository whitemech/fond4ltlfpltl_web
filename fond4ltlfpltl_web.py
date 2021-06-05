import sys
from dataclasses import dataclass
from pathlib import Path
from platform import python_version
from subprocess import TimeoutExpired, PIPE, Popen
from functools import wraps

from flask import Flask, render_template, request, jsonify, url_for, send_file
from flask import __version__ as flask_version
from fond4ltlfpltlf import __version__ as fond_version
from ltlf2dfa import __version__ as dfa_version
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


@dataclass(frozen=True)
class Configuration:
    """
    An helper class that lets the app to seamlessly
    read configuration from code and from OS environment.
    """

    # FLASK_STATIC_FOLDER: str = "static"
    FLASK_RUN_HOST: str = "0.0.0.0"
    FLASK_RUN_PORT: int = 5000
    MONA_BIN_PATH: str = shutil.which("mona")
    DOT_BIN_PATH: str = shutil.which("dot")

    def __getattribute__(self, varname):
        """Get varname from os.environ, else None"""
        value = os.environ.get(varname, None)
        try:
            default = super(Configuration, self).__getattribute__(varname)
        except AttributeError:
            default = None
        return value if value else default


configuration = Configuration()

app = Flask(__name__)

FUTURE_OPS = {"X", "F", "U", "G", "W", "R"}
PAST_OPS = {"Y", "O", "S", "H"}


def assert_(condition, message: str = ""):
    """Custom assert function to replace Python's built-in."""
    if not condition:
        raise AssertionError(message)


def launch(cmd):
    """Launch a command."""
    app.logger.info(f"Launching command: {' '.join(cmd)}")
    process = Popen(
        args=cmd,
        stdout=PIPE,
        stderr=PIPE,
        preexec_fn=os.setsid,
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
    cmd = [sys.executable, f"{PACKAGE_DIR}/{planner}_wrapper.py", "-d", f"{d}", "-p", f"{p}"]
    if planner != "prp":
        cmd.extend(["-s", f"{s}"])
    return launch(cmd)


def _compilation(d, p, f):
    """Compile a FOND for temporal extended goals to standard FOND."""
    domain_prime, problem_prime = execute(d, p, f)

    app.logger.info(f"Writing domain and problem to path {OUTPUT_DIR}")
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

    app.logger.info(f"Writing dfa to path {OUTPUT_DIR}")
    with open(f"{OUTPUT_DIR}/dfa.dot", "w+") as p:
        p.write(mona_output)

    return domain_prime, problem_prime, p_formula, mona_output


# TODO increase when ready
def cachecontrol(max_age=1):
    def decorate_f(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            response = f(*args, **kwargs)
            if (type(response) is Flask.response_class) and (
                response.status_code == 200
            ):
                response.cache_control.max_age = max_age
            return response

        return wrapped_f

    return decorate_f


@app.route('/load', methods=['GET'])
def load():
    file_path = request.args.get('jsdata')
    try:
        with open(f"{PACKAGE_DIR}/{file_path}", "r") as f:
            return json.load(f)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route("/api/")
def healthcheck():
    return {}, 200


# Return a Json list of triplets [[tool,version,url],...].
@app.route("/api/versions")
@cachecontrol()
def versions():
    app.logger.info("Request /api/versions")
    try:
        out, err = launch([configuration.DOT_BIN_PATH, "-V"])
        app.logger.info(err)
        assert_(err)
        dot_version = err.split(" ")[4]
    except Exception as e:
        app.logger.error(f"Dot version failed: {e}")
        dot_version = "missing"

    try:
        out, err = launch([configuration.MONA_BIN_PATH])
        assert_(out)
        mona_version = out.split("\n")[0].split(" ")[1][1:].strip()
    except Exception as e:
        app.logger.error(f"Mona version failed: {e}")
        mona_version = "missing"

    return jsonify(
        [
            ("Mona", mona_version, "https://www.brics.dk/mona/"),
            ("Graphviz", dot_version, "https://graphviz.org/"),
            ("Python", python_version(), "https://www.python.org/"),
            ("Flask", flask_version, "https://flask.palletsprojects.com/en/2.0.x/"),
            ("FOND4LTLfPLTLf", fond_version, "https://github.com/whitemech/fond4ltlfpltlf"),
            ("LTLf2DFA", dfa_version, "https://github.com/whitemech/ltlf2dfa"),
        ]
    )


@app.route('/api/compile', methods=['POST'])
@cachecontrol()
def compilation():
    formula = request.form['form_goal']
    in_domain = request.form['form_pddl_domain_in']
    in_problem = request.form['form_pddl_problem_in']
    app.logger.info(f"Request /api/compile: {formula} {in_domain} {in_problem}")

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


@app.route('/api/plan', methods=['POST'])
@cachecontrol()
def plan():
    formula = request.form['form_goal']
    in_domain = request.form['form_pddl_domain_in']
    in_problem = request.form['form_pddl_problem_in']
    planner = request.form['planner']
    policy_type = request.form['policy_type']
    app.logger.info(f"Request /api/plan: {formula} {in_domain} {in_problem} {planner} {policy_type}")

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
        app.logger.info(f"Calling {planner}...")
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

        app.logger.info(f"Calling {planner}... Done! Result: {ok}")
        result["elapsed_time"] = str(p_end - p_start)
        if ok:
            result["policy_found"] = True
            result["error"] = ""
            result["policy_txt"] = str(open(f"{OUTPUT_DIR}/plan/policy.txt", "r").read())
            result["policy_dot"] = str(open(f"{OUTPUT_DIR}/plan/policy.dot", "r").read())

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/download')
def download():
    app.logger.info(f"Request /api/download here {DOWNLOAD}")
    shutil.make_archive(DOWNLOAD, 'zip', OUTPUT_DIR)
    return send_file(f"{DOWNLOAD}.zip", mimetype='application/zip', as_attachment=True)


@app.route('/')
def index():
    launch(["rm", f"{OUTPUT_DIR}/*", f"{OUTPUT_DIR}/plan/*", f"{PACKAGE_DIR}/{DOWNLOAD}.zip"])
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
