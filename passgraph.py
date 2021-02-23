"""

"""

import glob
import biseau
from collections import Counter, defaultdict


def normalized(line:str) -> str:
    return line.lower().strip()
def normalized_human(name:str) -> str:
    return normalized(name).replace('-', '_').replace('ë', 'e')


ALIASES = {'jy': 'Jean_Yves', 'gaetan': 'Gaetan'}
HUMANS = 'Jean_Yves', 'Lucas', 'Gaetan', 'Jordan', 'Florian', 'Benjamin', 'Clément'
HUMANS = tuple(map(normalized_human, HUMANS))

def human_chains_from_files():
    for dailyfile in glob.glob('/home/lucas/notes/daily-conv*'):
        with open(dailyfile) as fd:
            for line in map(normalized, fd):
                if '->' in line:
                    humans = tuple(h for h in map(normalized_human, line.split('->')) if h)
                    if not set(humans) & set(HUMANS):
                        continue
                    yield humans

def firsts_and_links_from_file() -> (dict, [(str, str)]):
    first = defaultdict(int)  # number of time a given human is first speaker
    def gen_():
        for humans in human_chains_from_files():
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
        return round(10 * counts[pred, succ] / total_links, 2)
    graph = ''.join(
        f'link("{pred}","{succ}").  label("{pred}","{succ}","{counts[pred, succ]}").  '
        f'dot_property("{pred}","{succ}",penwidth,"{width_of(pred, succ)}").\n'
        for pred, succ in links
    ) + ''.join(f'dot_property("{human}",width,"{nb*0.2+0.2}").\n' for human, nb in firsts.items())
    biseau.compile_to_single_image(graph + ASP_BISEAU_RULES, outfile=outfile)
    print(f'saved into {outfile}')


if __name__ == '__main__':
    draw_links(*firsts_and_links_from_file(), 'out.png')


