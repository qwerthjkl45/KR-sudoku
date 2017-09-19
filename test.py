#https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution/12344609#12344609 Nicojo

import atexit
from time import time
from datetime import timedelta
from pyeda.inter import *
import pyeda

DIGITS = "123456789"


line = "="*40
def log(s, elapsed=None):
    print()
    print(str(timedelta(seconds=time()))+ '-'+ s)
    print(line)
    print()

def endlog():
    end = time()
    print('total time '+str(end-start) )
    print(line)
    print("End Program "+str(timedelta(seconds=time())))

def now():
    return secondsToStr(time())


X = exprvars('x', (1, 10), (1, 10), (1, 10))
#X = exprvars('x', 9, 9, 9)

V = And(*[
         And(*[
             OneHot(*[ X[r, c, v]
                 for v in range(1, 10) ])
             for c in range(1, 10) ])
         for r in range(1, 10) ])
R = And(*[
         And(*[
             OneHot(*[ X[r, c, v]
                 for c in range(1, 10) ])
             for v in range(1, 10) ])
         for r in range(1, 10) ])
C = And(*[
         And(*[
             OneHot(*[ X[r, c, v]
                 for r in range(1, 10) ])
             for v in range(1, 10) ])
         for c in range(1, 10) ])

B = And(*[
         And(*[
             OneHot(*[ X[3*br+r, 3*bc+c, v]
                 for r in range(1, 4) for c in range(1, 4) ])
             for v in range(1, 10) ])
         for br in range(3) for bc in range(3) ])

def parse_grid(grid):
    chars = [c for c in grid if c in DIGITS or c in "0."]
    assert len(chars) == 9 ** 2
    return And(*[ X[i // 9 + 1, i % 9 + 1, int(c)]
                  for i, c in enumerate(chars) if c in DIGITS ])

def get_val(point, r, c):
    for v in range(1, 10):
        if point[X[r, c, v]]:
            return DIGITS[v-1]
    return "X"



def display(point):
    print('\n')
    chars = list()
    for r in range(1, 10):
        for c in range(1, 10):
            if c in (4, 7):
                chars.append("|")
            chars.append(get_val(point, r, c))
        if r != 9:
            chars.append("\n")
            if r in (3, 6):
                chars.append("---+---+---\n")
    print("".join(chars))

def solve(grid):
    with parse_grid(grid):
        return S.satisfy_one()

S = And(V, R, C, B)
print(pyeda.boolalg.expr.expr2dimacscnf(S))
#grid = "004300209005009001070060043006002087190007400050083000600000105003508690042910300"
grid =  "073000800004130050085006310500090030008010500010060007051600280040052900002000640"
print(parse_grid(grid))
T = And(S, parse_grid(grid))
start = time()
atexit.register(endlog)
log("Start Program")
T.satisfy_one()
endlog()
display(T.satisfy_one())
