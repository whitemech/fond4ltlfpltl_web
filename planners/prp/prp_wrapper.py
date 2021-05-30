import os
import re
import argparse
import signal
import inspect

from pathlib import Path
from subprocess import Popen, PIPE, TimeoutExpired

import translator.translate_policy as translator
import validator

PRP_DIR = os.path.dirname(inspect.getfile(inspect.currentframe()))  # type: ignore
PLANNERS_DIR = str(Path(PRP_DIR, "..").resolve())  # type: ignore
OUTPUT_DIR = str(Path(PLANNERS_DIR, "../static/output/plan").resolve())  # type: ignore


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


def plan(domain_path, problem_path):
    """Planning for temporally extended goals (LTLf or PLTLf)."""
    rm_cmd = "rm {0}/*.dot {0}/*.out".format(OUTPUT_DIR)
    launch(rm_cmd)
    planner_command = f"{PRP_DIR}/prp {domain_path} {problem_path} --dump-policy 2"
    out, err = launch(planner_command)
    result = re.search(
        r"No solution .*",
        out,
    )
    if result:
        print(out)
    elif err:
        print(err)
    else:
        # Translate the policy from SAS+ to instantiated standard facts
        mapping, _ = translator.translate('output', 'policy.out', f'{OUTPUT_DIR}/policy-translated.out')
        # Validate the policy (from the initial state to the goal state) and generate the data structure
        g = validator.validate_and_generate_graph(domain_path,
                                                  problem_path,
                                                  mapping, f'{OUTPUT_DIR}/policy-translated.out', 'prp')
        validator.generate_dot_graph(g, OUTPUT_DIR)

    rm_cmd = "rm graph.dot *.out *.fsap plan_numbers_and_cost sas_plan elapsed.time output *.sas"
    launch(rm_cmd)


if __name__ == '__main__':
    """
    Usage: python prp_wrapper.py -d <DOMAIN-PATH> -p <PROBLEM-PATH>
    """
    parser = argparse.ArgumentParser(description="Wrapper for prp.")
    parser.add_argument('-d', dest='domain_path', type=Path, required=True)
    parser.add_argument('-p', dest='problem_path', type=Path, required=True)
    args = parser.parse_args()

    domain_path = args.domain_path
    problem_path = args.problem_path

    plan(domain_path, problem_path)
