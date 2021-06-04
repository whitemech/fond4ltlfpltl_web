import os
import re
import argparse
import signal
import sys

from pathlib import Path
from subprocess import Popen, PIPE, TimeoutExpired

from planners.prp.translator import translate_policy as translator
from planners.prp import validator


PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PLANNERS_DIR = str(Path(PACKAGE_DIR, "planners").resolve())  # type: ignore
PRP_DIR = str(Path(PLANNERS_DIR, "prp").resolve())  # type: ignore
OUTPUT_DIR = str(Path(PACKAGE_DIR, "static/output/plan").resolve())  # type: ignore


def launch(cmd):
    """Launch a command."""
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


def plan(domain_path, problem_path):
    """Planning for temporally extended goals (LTLf or PLTLf)."""
    rm_cmd = ["rm", f"{OUTPUT_DIR}/*.dot", f"{OUTPUT_DIR}/*.out"]
    launch(rm_cmd)
    planner_command = [f"{PRP_DIR}/prp", f"{domain_path}", f"{problem_path}", "--dump-policy", "2"]
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
        mapping, _, policy = translator.translate('output', 'policy.out', f'{OUTPUT_DIR}/policy.txt')
        # Validate the policy (from the initial state to the goal state) and generate the data structure
        g = validator.validate_and_generate_graph(domain_path,
                                                  problem_path,
                                                  mapping, policy, 'prp')
        validator.generate_dot_graph(g, OUTPUT_DIR)

    rm_cmd = ["rm", "graph.dot", "policy.out", "policy.fsap", "plan_numbers_and_cost", "sas_plan", "elapsed.time", "output",
              "output.sas"]
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
