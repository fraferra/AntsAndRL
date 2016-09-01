#!/usr/bin/env python

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
from random import shuffle, random
from ants import *

import sys


class MyBot():
    def __init__(self):
        self.OBSTACLES_MAP = set([])
        self.NOT_OBSTACLES_MAP = set([])
        self.VISITED_STATES = {}
        self.VALUE_STATES = {}
        self.ACTION_STATES = {}
        self.TMP_STATE = {}
        self.other_ants_positions = set([])
        self.directions = ["n","e","s","w"]
        self.loop = 1



    def takeAction(self, a_row, a_col, ants):
        results = []
        dd = ["n","e","s","w"]
        hunted = []
        shuffle(dd)
        self.VISITED_STATES[(a_row, a_col)] = self.VISITED_STATES.get((a_row, a_col),1.0) + 0.1

        for direction in dd:
            (d_row, d_col) = ants.destination(a_row, a_col, direction)
            if (d_row, d_col) in self.other_ants_positions:
                value = -10.0
            else:
                if not ants.unoccupied(d_row, d_col):
                    value = -1.0
                else:
                    value = self.ACTION_STATES.get((direction, d_row, d_col), 2.0)/ self.VISITED_STATES.get((d_row, d_col),1.0)

                    if (d_row, d_col) == ants.closest_food(a_row,a_col,hunted):
                        value += 2.0
                    if (d_row, d_col) == ants.closest_enemy_hill(a_row,a_col):
                        value += 7.0
                    if (d_row, d_col) == ants.closest_enemy_ant(a_row,a_col,hunted):
                        value += 1.0

            results.append((direction, (d_row, d_col), value))


        results = sorted(results, key = lambda k: -k[2])
        best_dir = results[0][0]
        best_place = results[0][1]
        ants.issue_order((a_row, a_col, best_dir))
        
        self.VISITED_STATES[(d_row, d_col)] = self.VISITED_STATES.get(best_place,1.0) + 0.1
        self.ACTION_STATES[(best_dir, best_place[0], best_place[1])] = self.ACTION_STATES.get((best_dir, best_place[0], best_place[1]),1.0) + 0.1
        self.other_ants_positions.discard((a_row, a_col))
        self.other_ants_positions.add(best_place)

        
    def updateState(self):
        for position in self.ACTION_STATES:
            self.ACTION_STATES[position] = self.ACTION_STATES[position]*0.8
        for position in self.VISITED_STATES:
            self.VISITED_STATES[position] = self.VISITED_STATES[position]*0.8

    def do_turn(self, ants):
        self.other_ants_positions = set([])
        for a_row, a_col in ants.my_ants():

            self.takeAction(a_row, a_col, ants)
            #self.updateState()


        self.loop += 1
        # if self.loop % 100 == 0:
        #     self.ACTION_STATES = {}
        #     self.VISITED_STATES = {}

            
if __name__ == '__main__':
    # psyco will speed up python a little, but is not needed
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        Ants.run(MyBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
