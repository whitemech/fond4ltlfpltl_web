from flask import Flask, render_template, request, jsonify, url_for, Response
from fond4ltlfpltlf.core import execute

import os
import json

from ltlf2dfa.parser.ltlf import LTLfParser
from ltlf2dfa.parser.pltlf import ParsingError, PLTLfParser

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

FUTURE_OPS = {"X", "F", "U", "G", "W", "R"}
PAST_OPS = {"Y", "O", "S", "H"}

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/compile', methods=['POST'])
def compilation():
    formula = request.form['form_goal']
    in_domain = request.form['form_pddl_domain_in']
    in_problem = request.form['form_pddl_problem_in']

    try:
        domain_prime, problem_prime = execute(in_domain, in_problem, formula)

        with open(os.path.join(PACKAGE_DIR, "static", "output", "new-domain.pddl"), "w+") as d:
            d.write(str(domain_prime))
        with open(os.path.join(PACKAGE_DIR, "static", "output", "new-problem.pddl"), "w+") as p:
            p.write(str(problem_prime))

        # dfa computed again. We need to change fond4ltlfpltlf APIs
        if all(c in FUTURE_OPS for c in formula if c.isupper()):
            f_parser = LTLfParser()
            try:
                p_formula = f_parser(formula)
            except Exception:
                raise ParsingError()

        else:
            assert all(c in PAST_OPS for c in formula if c.isupper())
            p_parser = PLTLfParser()
            try:
                p_formula = p_parser(formula)
            except Exception:
                raise ParsingError()

        mona_output = p_formula.to_dfa(mona_dfa_out=False)
        mona_output = mona_output.replace("LR", "TB")

        return jsonify({'form_pddl_domain_out': str(domain_prime),
                        'form_pddl_problem_out': str(problem_prime),
                        'dfa': str(mona_output),
                        'formula': str(p_formula)})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/load', methods=['GET'])
def load_example():
    file_path = request.args.get('jsdata')
    try:
        with open(os.path.join(PACKAGE_DIR, file_path)) as f:
            return json.load(f)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/download/<string:file>')
def download(file):
    return Response(
        open(os.path.join(PACKAGE_DIR, 'static', 'output', file)),
        mimetype="text/plain",
        headers={"Content-disposition": "attachment; filename={}".format(file)})


if __name__ == "__main__":
    app.run(debug=True)
