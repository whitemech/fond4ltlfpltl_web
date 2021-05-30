import argparse
import re
from pathlib import Path

from graphviz import Digraph


def _dump(rgx, content, dotall):
    """Dumps interested strings from content using re."""
    return re.search(rgx, content, re.DOTALL).group(1).strip() if dotall else re.search(rgx, content).group(1).strip()


def _dump_all(rgx, content, dotall):
    """Dumps interested strings from content using re."""
    return re.findall(rgx, content, re.DOTALL) if dotall else re.findall(rgx, content)


def draw(in_path, out_path):
    """Create .dot from a FOND-SAT policy in :in_path."""
    G = Digraph()
    G.graph_attr['rankdir'] = 'LR'

    with open(in_path, "r") as content:
        policy = content.read()

    t_predicates = _dump(r"Atom \(CS\)(.*)\(CS, Action with arguments\)", policy, True).replace("===================",
                                                                                                "").replace(
        "___________________", "").strip()
    t_actions = _dump(r"\(CS, Action name, CS\)(.*)\(CS, CS\)", policy, True).replace("===================",
                                                                                      "").replace(
        "___________________", "").strip()

    states = _dump_all(r"(?<=----------\n)(.*?)(?=----------\n)", t_predicates + "----------\n", True)
    for state in states:
        if "-NegatedAtom turndomain()" in state:
            continue
        temp = set()
        node = state.split("\n")[0].split(" ")[-1].strip("()")
        predicates = state.split("\n")
        for p in predicates:
            p = "".join(p.split(" ")[:-1]).replace("NegatedAtom", "").replace("Atom", "").strip()
            if p != '':
                temp.add(p)
        G.node(node, "\n".join(temp))

    actions = [x.strip("()").split(",") for x in t_actions.split("\n")]
    for s, a, d in actions:
        if "trans-" not in a:
            rgx = f"\({d},trans-.*,(.*)\)"
            new_dest = _dump(rgx, t_actions, False)
            G.edge(s, new_dest,
                   a.replace('_DETDUP_1', '').replace('_DETDUP_0', '').replace('_DETDUP_3', '').replace('_DETDUP_4',
                                                                                                        ''))

    G.save(out_path)


if __name__ == '__main__':
    """
    Usage: python draw.py -i <POLICY-PATH> -o <GRAPH-PATH>
    """
    parser = argparse.ArgumentParser(description="Wrapper for fondsat.")
    parser.add_argument('-i', dest='policy_path', type=Path, required=True)
    parser.add_argument('-o', dest='graph_path', type=Path, required=True)
    args = parser.parse_args()

    policy_path = args.policy_path
    graph_path = args.graph_path

    draw(policy_path, graph_path)
