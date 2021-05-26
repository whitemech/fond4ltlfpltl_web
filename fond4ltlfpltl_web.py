from flask import Flask, render_template, request, jsonify, url_for, Response
from fond4ltlfpltlf.core import execute
import os
import json

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/compilation', methods=['POST'])
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

        return jsonify({'form_pddl_domain_out': str(domain_prime), 'form_pddl_problem_out': str(problem_prime)})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/load-example', methods=['GET'])
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
