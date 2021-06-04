import os
import argparse
import re
import signal
import sys

from pathlib import Path
from subprocess import Popen, PIPE, TimeoutExpired

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PLANNERS_DIR = str(Path(PACKAGE_DIR, "planners").resolve())  # type: ignore
MYND_DIR = str(Path(PLANNERS_DIR, "mynd").resolve())  # type: ignore
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


def plan(domain_path, problem_path, strong):
    """Planning for temporally extended goals (LTLf or PLTLf)."""
    rm_cmd = ["rm", f"{OUTPUT_DIR}/*.dot", f"{OUTPUT_DIR}/*.txt"]
    launch(rm_cmd)
    search = "LAOSTAR"
    if strong:
        search = "AOSTAR"
    translate_command = [sys.executable, f"{MYND_DIR}/translator-fond/translate.py", f"{domain_path}",
                         f"{problem_path}"]
    launch(translate_command)
    planner_command = ["java", "-jar", f"{MYND_DIR}/MyND.jar", "-search", f"{search}", "output.sas", "-exportPlan",
                       f"{OUTPUT_DIR}/policy.txt", "-exportDot", f"{OUTPUT_DIR}/policy.dot", "-timeout", "300"]
    out, err = launch(planner_command)
    rm_cmd = ["rm", "output.sas"]
    launch(rm_cmd)
    result = re.search(
        r"Result: No .*",
        out,
    )
    if result:
        print(out)
    elif err:
        print(err)


if __name__ == '__main__':
    """
    Usage: python mynd_wrapper.py -d <DOMAIN-PATH> -p <PROBLEM-PATH> -s <STRONG>
    """
    parser = argparse.ArgumentParser(description="Wrapper for mynd.")
    parser.add_argument('-d', dest='domain_path', type=Path, required=True)
    parser.add_argument('-p', dest='problem_path', type=Path, required=True)
    parser.add_argument('-s', dest='strong', type=int, choices={0, 1}, required=True)
    args = parser.parse_args()

    domain_path = args.domain_path
    problem_path = args.problem_path
    strong = args.strong

    plan(domain_path, problem_path, strong)
