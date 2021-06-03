import os
import re
import argparse
import signal
import inspect
import sys

from pathlib import Path
from subprocess import Popen, PIPE, TimeoutExpired

FONDSAT_DIR = os.path.dirname(inspect.getfile(inspect.currentframe()))  # type: ignore
PLANNERS_DIR = str(Path(FONDSAT_DIR, "..").resolve())  # type: ignore
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

    planner_command = f"python {FONDSAT_DIR}/main.py {domain_path} {problem_path} -strong {strong} -policy 1 " \
                      f"-time_limit 300"
    out, err = launch(planner_command)
    result = re.search(
        r"-> OUT OF TIME|-> OUT OF TIME/MEM",
        out,
    )
    if result:
        print(out)
    elif err:
        print(err)
    else:
        with open(f"{OUTPUT_DIR}/policy.txt", "w+") as f:
            f.write(re.search(r"##SOLVED##(.*)", out, re.DOTALL).group(1).strip())
        draw_command = f"python {FONDSAT_DIR}/draw.py -i {OUTPUT_DIR}/policy.txt -o {OUTPUT_DIR}/policy.dot"
        launch(draw_command)

    rm_cmd = "rm *.sas *-temp.txt*"
    launch(rm_cmd)


if __name__ == '__main__':
    """
    Usage: python fondsat_wrapper.py -d <DOMAIN-PATH> -p <PROBLEM-PATH> -s <STRONG>
    """
    parser = argparse.ArgumentParser(description="Wrapper for fondsat.")
    parser.add_argument('-d', dest='domain_path', type=Path, required=True)
    parser.add_argument('-p', dest='problem_path', type=Path, required=True)
    parser.add_argument('-s', dest='strong', type=int, choices={0, 1}, required=True)
    args = parser.parse_args()

    domain_path = args.domain_path
    problem_path = args.problem_path
    strong = args.strong

    plan(domain_path, problem_path, strong)
