import argparse
from pathlib import Path

from graphviz import Digraph


# TODO: Alberto --> clen and comment this a bit
def draw(file, outfile):
    G = Digraph()
    G.graph_attr['rankdir'] = 'LR'
    infile = open(file, 'r')

    mapping = {}

    for line in infile:
        if line == '----------\n':
            line = next(infile)
            while line != '===================\n':
                node = line.split(' ')[-1].strip().replace('(', '').replace(')', '')
                predicate = ''.join(line.split(' ')[:-1]).replace(' ', '').replace('NegatedAtom', '').replace('Atom',
                                                                                                              '').replace(
                    '()', '')
                if not node in mapping:
                    mapping[node] = [predicate]

                else:
                    mapping[node].append(predicate)
                line = next(infile)

                if line == '----------\n' or line == '===================\n':
                    mapping[node] = '\n'.join(mapping[node])
                    G.node(node, mapping[node])
                    line = next(infile)

        if line == '(CS, Action name, CS)\n':
            line = next(infile)
            line = next(infile)
            while line != '===================\n':
                ini = line.split(',')[0].replace('(', '')
                dest = line.split(',')[-1].replace(')\n', '')
                action = line.split(',')[1].replace('_DETDUP_1', '').replace('_DETDUP_0', '').replace('_DETDUP_3',
                                                                                                      '').replace(
                    '_DETDUP_4', '')
                # G.add_edge(ini,dest)
                G.edge(ini, dest, action)
                line = next(infile)

    # directory = file.replace(file, outfile)
    G.save(outfile)


if __name__ == '__main__':
    """
    Usage: python draw.py -i <POLICY-PATH> -o <GRAPH-PATH>
    """
    parser = argparse.ArgumentParser(description="Wrapper for FOND-SAT.")
    parser.add_argument('-i', dest='policy_path', type=Path, required=True)
    parser.add_argument('-o', dest='graph_path', type=Path, required=True)
    args = parser.parse_args()

    policy_path = args.policy_path
    graph_path = args.graph_path

    draw(policy_path, graph_path)
