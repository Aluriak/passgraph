

import glob
import biseau
from collections import Counter


def normalized(line:str) -> str:
    return line.lower().strip()
def normalized_human(name:str) -> str:
    return normalized(name).replace('-', '_').replace('ë', 'e')


ALIASES = {'jy': 'Jean_Yves', 'gaetan': 'Gaetan'}
HUMANS = 'Jean_Yves', 'Lucas', 'Gaetan', 'Jordan', 'Florian', 'Benjamin', 'Clément'
HUMANS = tuple(map(normalized_human, HUMANS))

def links_from_files():
    for dailyfile in glob.glob('/home/lucas/notes/daily-conv*'):
        with open(dailyfile) as fd:
            for line in map(normalized, fd):
                if '->' in line:
                    humans = tuple(map(normalized_human, line.split('->')))
                    if not set(humans) & set(HUMANS):
                        continue
                    for idx, pred in enumerate(humans):
                        try:
                            succ = humans[idx+1].strip()
                        except IndexError:
                            break
                        pred = pred.strip()
                        yield ALIASES.get(pred, pred), ALIASES.get(succ, succ)


def draw_links(links:[(str, str)], outfile:str):
    ASP_BISEAU_RULES = """
    obj_property(edge,arrowhead,normal).
    """
    counts = Counter(pred for pred, _ in links)
    total_links = len(links)
    def width_of(human):
        return round(10 * counts[human] / total_links, 2)
    graph = ''.join(
        f'link("{pred}","{succ}").  dot_property("{pred}","{succ}",penwidth,"{width_of(pred)}").\n'
        for pred, succ in links
    )
    biseau.compile_to_single_image(graph + ASP_BISEAU_RULES, outfile=outfile)
    print(f'saved into {outfile}')


if __name__ == '__main__':
    draw_links(tuple(links_from_files()), 'out.png')


