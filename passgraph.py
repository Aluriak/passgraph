"""

"""

import glob
import biseau
import argparse
import itertools
from collections import Counter, defaultdict


def parse_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=str, help='globs describing files to edit')
    return parser.parse_args()


def normalized(line:str) -> str:
    return line.lower().strip()
def normalized_human(name:str) -> str:
    return normalized(name).replace('-', '_').replace('ë', 'e').replace('é', 'e')


ALIASES = {'jean_yves': 'Jean_Yves', 'jy': 'Jean_Yves', 'gaetan': 'Gaetan'}
HUMANS = 'Jean_Yves', 'Lucas', 'Gaetan', 'Clément', 'Jordan', 'Florian', 'Benjamin', 'Glenn', 'Laura'
HUMANS = tuple(map(normalized_human, HUMANS))

def human_chains_from_files(filenames:[str]):
    for dailyfile in filenames:
        with open(dailyfile) as fd:
            for line in map(normalized, fd):
                if '->' in line:
                    humans = tuple(h for h in map(normalized_human, line.split('->')) if h)
                    if not set(humans) & set(HUMANS):
                        continue
                    yield humans

def firsts_and_links_from_file(filenames:[str]) -> (dict, [(str, str)]):
    first = defaultdict(int)  # number of time a given human is first speaker
    def gen_():
        for humans in human_chains_from_files(filenames):
            first[humans[0]] += 1
            for idx, pred in enumerate(humans):
                try:
                    succ = humans[idx+1].strip()
                except IndexError:
                    break
                pred = pred.strip()
                yield ALIASES.get(pred, pred), ALIASES.get(succ, succ)
    return first, tuple(gen_())


def draw_links(firsts:dict, links:[(str, str)], outfile:str):
    ASP_BISEAU_RULES = """
    obj_property(edge,arrowhead,normal).
    obj_property(node,shape,circle).
    """
    counts = Counter(links)
    total_links = len(links)
    def width_of(pred, succ):
        return round(50 * counts[pred, succ] / total_links, 2)
    def humanized(name:str) -> str:
        return name.title().replace('_', ' ').replace('Gaetan', 'Gaëtan')
    graph = ''.join(
        f'link("{pred}","{succ}").  label("{pred}","{succ}","{counts[pred, succ]}").  '
        f'dot_property("{pred}","{succ}",penwidth,"{width_of(pred, succ)}").\n'
        for pred, succ in links
    ) + ''.join(
        f'dot_property("{human}",width,"{nb*0.2+0.2}").\n'
        for human, nb in firsts.items()
    ) + ''.join(
        f'label("{human}","{humanized(human)}").\n'
        for human in HUMANS
    )
    print(graph)
    biseau.compile_to_single_image(graph + ASP_BISEAU_RULES, outfile=outfile, dotfile=outfile + '.dot')
    print(f'saved into {outfile}')


if __name__ == '__main__':
    args = parse_cli()
    fnames = tuple(itertools.chain.from_iterable(map(glob.glob, args.files)))
    draw_links(*firsts_and_links_from_file(fnames), 'out.png')

