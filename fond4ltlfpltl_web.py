from flask import Flask, render_template, request, jsonify, send_from_directory
from fond4ltlfpltl.core import execute
import os

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

        # with open(os.path.join(PACKAGE_DIR, "assets", "output", "new-domain.pddl"), "w+") as d:
        #     d.write(str(domain_prime))
        # with open(os.path.join(PACKAGE_DIR, "assets", "output", "new-problem.pddl"), "w+") as p:
        #     p.write(str(problem_prime))

        return jsonify({'form_pddl_domain_out': str(domain_prime), 'form_pddl_problem_out': str(problem_prime)})
    except Exception as e:
        return jsonify({'error': str(e)})


# @app.route('/download-domain', methods=['GET'])
# def download_domain():
#     return send_from_directory("assets/output", "new-domain.pddl")
#
#
# @app.route('/download-problem', methods=['GET'])
# def download_problem():
#     return send_from_directory("assets/output", "new-problem.pddl")


if __name__ == "__main__":
    app.run(debug=True)
