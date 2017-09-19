#https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution/12344609#12344609 Nicojo

import atexit
from time import time
from datetime import timedelta
from pyeda.inter import *
import pyeda
import numpy as np
import sys

DIGITS = "123456789"


line = "="*40
def log(s, elapsed=None):
    #print()
    #print(str(timedelta(seconds=time()))+ '-'+ s)
    print(line)
    #print()

def endlog():
    end = time()
    #print('total time '+str(end-start) )
    #print(line)
    #print("End Program "+str(timedelta(seconds=time())))
    return (end-start)

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

def convert_sol_to_array(point):
    grid_tmp = list()
    for r in range(1,10):
        for c in range(1,10):
            grid_tmp.append(get_val(point, r, c))
    return ("".join(grid_tmp))

def solve(grid):
    with parse_grid(grid):
        return S.satisfy_one()

def replace(block_ind_row, block_ind_col, grid, grid_value):
    for i in np.arange(3):
        for j in np.arange(3):
            index = (i + block_ind_row)*9+j+block_ind_col
            grid = grid[:index] + grid_value[((6-block_ind_row)+i)*9+j+(6-block_ind_col)] + grid[index + 1:]
    print(grid)
    return grid

def solve_sudoku_without_center():
    for idx, grid in enumerate(grids_from_data):
        T = And(S, parse_grid(grid))
        global times_w0 
        global start
        if (idx == len(grids_from_data)-1):
            return times_w0
        start = time()
        T.satisfy_one()
        times_w0 = endlog()+ times_w0
        grids_from_data[idx] = convert_sol_to_array(T.satisfy_one())
    return times_w0

def solve_sudoku_w1():#solve separately
    T = And(S, parse_grid(grids_from_data[4]))
    global times_w1 
    global start
    start = time()
    T.satisfy_one()
    times_w1 = endlog()+ times_w0
    return times_w1

def solve_sudoku_w2():#solve with value from first-fourth sudoku
    grids_from_data[4] = replace(0, 0, grids_from_data[4], grids_from_data[0])
    grids_from_data[4] = replace(0, 6, grids_from_data[4], grids_from_data[1])
    grids_from_data[4] = replace(6, 0, grids_from_data[4], grids_from_data[2])
    grids_from_data[4] = replace(6, 6, grids_from_data[4], grids_from_data[3])

    T = And(S, parse_grid(grids_from_data[4]))
    global times_w2
    global start
    start = time()
    T.satisfy_one()
    times_w2 = endlog()+ times_w0
    return times_w2


S = And(V, R, C, B)

file = open("data.txt","r")
grids_from_data = []

times_w0 = 0.0
times_w1 = 0.0
times_w2 = 0.0

for lines_index, lines in enumerate(file):
    grids_from_data.append(lines)
    if((((lines_index) % 4 )==0) & (lines_index != 0)):
        times_w0 = solve_sudoku_without_center()
        times_w1 = solve_sudoku_w1()
        times_w2 = solve_sudoku_w2()
        #clean grid data
        print(str(times_w0)+' '+str(times_w1)+' '+str(times_w2))
        
    

