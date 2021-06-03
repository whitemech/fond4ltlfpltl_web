import os
import argparse
import re
import signal
import inspect
import sys

from pathlib import Path
from subprocess import Popen, PIPE, TimeoutExpired

MYND_DIR = os.path.dirname(inspect.getfile(inspect.currentframe()))  # type: ignore
PLANNERS_DIR = str(Path(MYND_DIR, "..").resolve())  # type: ignore
OUTPUT_DIR = str(Path(PLANNERS_DIR, "../static/output/plan").resolve())  # type: ignore


def launch(cmd):
    """Launch a command."""
    process = Popen(
        executable=sys.executable,
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


def plan(domain_path, problem_path, strong):
    """Planning for temporally extended goals (LTLf or PLTLf)."""
    rm_cmd = "rm {0}/*.dot {0}/*.txt".format(OUTPUT_DIR)
    launch(rm_cmd)
    search = "LAOSTAR"
    if strong:
        search = "AOSTAR"
    translate_command = f"python {MYND_DIR}/translator-fond/translate.py {domain_path} {problem_path}"
    launch(translate_command)
    planner_command = f"java -jar {MYND_DIR}/MyND.jar -search {search} output.sas -exportPlan " \
                      f"{OUTPUT_DIR}/policy.txt -exportDot {OUTPUT_DIR}/policy.dot -timeout 300"
    out, err = launch(planner_command)
    rm_cmd = "rm output.sas"
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
