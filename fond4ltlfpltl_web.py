import signal
from pathlib import Path
from subprocess import TimeoutExpired, PIPE, Popen

from flask import Flask, render_template, request, jsonify, url_for, Response
from fond4ltlfpltlf.core import execute

import os
import json

from ltlf2dfa.parser.ltlf import LTLfParser
from ltlf2dfa.parser.pltlf import ParsingError, PLTLfParser

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = PACKAGE_DIR / Path("static") / Path("output")
PLANNERS_DIR = PACKAGE_DIR / Path("planners")
MYND_DIR = PACKAGE_DIR / PLANNERS_DIR / Path("MyND")
PRP_DIR = PACKAGE_DIR / PLANNERS_DIR / Path("PRP")
FONDSAT_DIR = PACKAGE_DIR / PLANNERS_DIR / Path("FOND-SAT")


app = Flask(__name__)

FUTURE_OPS = {"X", "F", "U", "G", "W", "R"}
PAST_OPS = {"Y", "O", "S", "H"}


def launch(cmd, debug=False):
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
        return str(error).strip() if debug else str(output).strip()
    except TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        return False


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

    return domain_prime, problem_prime, p_formula, mona_output


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/load', methods=['GET'])
def load():
    file_path = request.args.get('jsdata')
    try:
        with open(f"{PACKAGE_DIR}/{file_path}", "r") as f:
            return json.load(f)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/download/<string:file>')
def download(file):
    return Response(
        open(f"{OUTPUT_DIR}/{file}"),
        mimetype="text/plain",
        headers={"Content-disposition": "attachment; filename={}".format(file)})


@app.route('/compile', methods=['POST'])
def compilation():
    formula = request.form['form_goal']
    in_domain = request.form['form_pddl_domain_in']
    in_problem = request.form['form_pddl_problem_in']

    try:
        domain_prime, problem_prime, p_formula, mona_output = _compilation(in_domain, in_problem, formula)
        return jsonify({'form_pddl_domain_out': str(domain_prime),
                        'form_pddl_problem_out': str(problem_prime),
                        'formula': str(p_formula),
                        'dfa': str(mona_output)})
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
        domain_prime, problem_prime, p_formula, mona_output = _compilation(in_domain, in_problem, formula)

        # call to planner and handle output
        if planner == "mynd":
            cmd = f"python {MYND_DIR}/mynd_wrapper.py -d {domain_prime} -p {problem_prime} -s {policy_type}"
            err = launch(cmd)
            if err:
                return jsonify({'form_pddl_domain_out': str(domain_prime),
                                'form_pddl_problem_out': str(problem_prime),
                                'formula': str(p_formula),
                                'dfa': str(mona_output),
                                'error': str(err)})
        elif planner == "prp":
            cmd = f"python {PRP_DIR}/prp_wrapper.py -d {domain_prime} -p {problem_prime}"
            err = launch(cmd)
            if err:
                return jsonify({'form_pddl_domain_out': str(domain_prime),
                                'form_pddl_problem_out': str(problem_prime),
                                'formula': str(p_formula),
                                'dfa': str(mona_output),
                                'error': str(err)})
            else:
                p = Path(f"{OUTPUT_DIR}/plan/policy-translated.out").rename("policy")
                p.rename(p.with_suffix(".txt"))
        else:
            assert planner == "fondsat"
            cmd = f"python {FONDSAT_DIR}/fondsat_wrapper.py -d {domain_prime} -p {problem_prime} -s {policy_type}"
            err = launch(cmd)
            if err:
                return jsonify({'form_pddl_domain_out': str(domain_prime),
                                'form_pddl_problem_out': str(problem_prime),
                                'formula': str(p_formula),
                                'dfa': str(mona_output),
                                'error': str(err)})

        return jsonify({'form_pddl_domain_out': str(domain_prime),
                        'form_pddl_problem_out': str(problem_prime),
                        'formula': str(p_formula),
                        'dfa': str(mona_output),
                        'policy_txt': str(open(f"{OUTPUT_DIR}/plan/policy.txt", "r").read()),
                        'policy_dot': str(open(f"{OUTPUT_DIR}/plan/policy.dot", "r").read())})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == "__main__":
    app.run(debug=True)
