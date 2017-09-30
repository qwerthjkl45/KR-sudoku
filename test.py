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
    return secondsToStr(time.clock())


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
    return grid

def solve_sudoku_without_center():
    for idx, grid in enumerate(grids_from_data):
        #T = And(S, parse_grid(grid))
        global times_w0 
        global start
        if (idx == len(grids_from_data)-1):
            return times_w0
        start = time() 
        solve(grid)
        times_w0 = endlog()+ times_w0
        grids_from_data[idx] = convert_sol_to_array(solve(grid))
    return times_w0

def solve_sudoku_w1():#solve separately
    #T = And(S, parse_grid(grids_from_data[4]))
    global times_w1 
    global start
    start = time()
    solve(grids_from_data[4])
    times_w1 = endlog()+ times_w0
    return times_w1

def solve_sudoku_w2():#solve with value from first-fourth sudoku
    grids_from_data[4] = replace(0, 0, grids_from_data[4], grids_from_data[0])
    grids_from_data[4] = replace(0, 6, grids_from_data[4], grids_from_data[1])
    grids_from_data[4] = replace(6, 0, grids_from_data[4], grids_from_data[2])
    grids_from_data[4] = replace(6, 6, grids_from_data[4], grids_from_data[3])

    #T = And(S, parse_grid(grids_from_data[4]))
    global times_w2
    global start
    start = time()
    solve(grids_from_data[4])
    times_w2 = endlog()+ times_w0
    return times_w2

def solve_sudoku_w3(): #solve center sub-sukudo first, and then fill value in 1-4th sub sukodu
     #T = And(S, parse_grid(grids_from_data_used_in_w3[4]))
     global times_w3
     global start
     start = time()
     #T.satisfy_one()
     solve(grids_from_data_used_in_w3[4])
     times_w3 = endlog()
     grids_from_data_used_in_w3[4] = convert_sol_to_array(solve(grids_from_data_used_in_w3[4]))
     #replace value to 1-4th sudoku
     grids_from_data_used_in_w3[0] = replace(6, 6, grids_from_data_used_in_w3[0], grids_from_data_used_in_w3[4])
     grids_from_data_used_in_w3[1] = replace(6, 0, grids_from_data_used_in_w3[1], grids_from_data_used_in_w3[4])
     grids_from_data_used_in_w3[2] = replace(0, 6, grids_from_data_used_in_w3[2], grids_from_data_used_in_w3[4])
     grids_from_data_used_in_w3[3] = replace(0, 0, grids_from_data_used_in_w3[3], grids_from_data_used_in_w3[4])

     for idx, grid in enumerate(grids_from_data_used_in_w3):
        #T = And(S, parse_grid(grid))
        solve(grid)
        if (idx == len(grids_from_data)-1):
            return times_w3
        start = time()
        #T.satisfy_one()
        solve(grid)
        times_w3 = endlog()+ times_w3
     
     return times_w3

S = And(V, R, C, B)

file = open("data.txt","r")
grids_from_data = []
grids_from_data_used_in_w3 = []

times_w0 = 0.0 #time solve 1-4th sudoku
times_w1 = 0.0 #time solve 1-4th sudoku + solve 5th sudoku without value from 1 -4th sudoku
times_w2 = 0.0 #time solve 1-4th sudoku + solve 5th sudoku with value from 1-4th sudoku
times_w3 = 0.0 #time solve 5th sudoku, and then using new sub-sukodu of 1-4th to solve

times_w0_sum = 0.0
times_w1_sum = 0.0
times_w2_sum = 0.0
times_w3_sum = 0.0

way1_fastest_times = 0
way2_fastest_times = 0
way3_fastest_times = 0

w1_w2_w3 = 0
w1_w3_w2 = 0
w2_w1_w3 = 0
w2_w3_w1 = 0
w3_w1_w2 = 0
w3_w2_w1 = 0

for lines_index, lines in enumerate(file):
    grids_from_data.append(lines)
    grids_from_data_used_in_w3.append(lines)
    if((((lines_index-4) % 5 )==0) & (lines_index != 0)):
        
        times_w0 = solve_sudoku_without_center()
        times_w1 = solve_sudoku_w1()
        times_w2 = solve_sudoku_w2()
        times_w3 = solve_sudoku_w3()

        print('------')
        print('way1: '+str(times_w1)+' way2: '+str(times_w2)+' way3: '+str(times_w3)+' ')
        grids_from_data[:]=[]
        grids_from_data_used_in_w3[:]=[]        

        times_w0_sum += times_w0 
        times_w1_sum += times_w1
        times_w2_sum += times_w2 
        times_w3_sum += times_w3

        if((times_w1>=times_w2) & (times_w1>=times_w3)):
            if(times_w2>=times_w3):
                w1_w2_w3 = w1_w2_w3 +1
            else:
                w1_w3_w2 = w1_w3_w2 +1
        elif((times_w2>times_w1) & (times_w2>=times_w3)):
            if(times_w1>=times_w3):
                w2_w1_w3 = w2_w1_w3 +1
            else:
                w2_w3_w1 = w2_w3_w1 +1
        elif((times_w3>times_w1) & (times_w3>times_w2)):
            if(times_w1>=times_w2):
                w3_w1_w2 = w3_w1_w2 +1
            else:
                w3_w2_w1 = w3_w2_w1 +1

        times_w0 = 0.0
        times_w1 = 0.0
        times_w2 = 0.0
        times_w3 = 0.0
        
print('---------------result ------------------------')    
print('way 1: '+str(times_w1_sum/((lines_index+1)/5))+' solve each sudoku separately ' )    
print('way 2: '+str(times_w2_sum/((lines_index+1)/5))+' solve the surrounded sub-sudoku first, and then fill value you got from those sub-sudoku in the center sub-sudoku')
print('way 3: '+str(times_w3_sum/((lines_index+1)/5))+' solve the center sub-sudoku first, and then fill value you just got from center sub-sudoku in the surrounded sub-sudoku') 
print('---------------result ------------------------')  
print('way 1 is the fastest times: (w3>w2>w1) (w2>w3>w1)  '+str(w3_w2_w1)+'+ '+str(w2_w3_w1)+'= '+ str(w3_w2_w1+w2_w3_w1))
print('way 2 is the fastest times: (w1_w3_w2) (w3_w1_w2)  '+str(w1_w3_w2)+'+ '+str(w3_w1_w2)+'= '+ str(w1_w3_w2+w3_w1_w2))
print('way 3 is the fastest times: (w1>w2>w3) (w2>w1>w3)  '+str(w1_w2_w3)+'+ '+str(w2_w1_w3)+'= '+ str(w1_w2_w3+w2_w1_w3))



