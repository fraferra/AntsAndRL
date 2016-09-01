#!/usr/bin/env python
from random import shuffle
import random
from ants import *
import numpy as np
import sys
import math

class FerrariBot():
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



    def directionToClosetEnemyHill(self, a_row, a_col, ants):
        locations = ants.enemy_hills()
        distances = sorted([(location, ants.distance(location[0], location[1], a_row, a_col)) for location in locations], key = lambda k:k[1])[0][0]
        directions = ants.directions(a_row, a_col, distances[0], distances[1])
        return directions


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
                    
                    
                    #directions_to_enemy_hill =  self.directionToClosetEnemyHill(a_row, a_col, ants)
                    f_location = ants.closest_food(a_row,a_col,hunted)
                    if f_location != None:
                        f_direction = ants.direction(a_row, a_col, f_location[0], f_location[1])

                    if direction in f_direction:
                        value += 2.0
                    if (d_row, d_col) == ants.closest_enemy_hill(a_row,a_col):
                        value += 7.0
                    if (d_row, d_col) == ants.closest_enemy_ant(a_row,a_col,hunted):
                        value += 1.0
                    #if direction in directions_to_enemy_hill:
                    #    value += 2.0

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
            self.ACTION_STATES[position] = self.ACTION_STATES[position]*0.995
        for position in self.VISITED_STATES:
            self.VISITED_STATES[position] = self.VISITED_STATES[position]*0.995

    def do_turn(self, ants):
        self.other_ants_positions = set([])
        for a_row, a_col in ants.my_ants():

            self.takeAction(a_row, a_col, ants)
            #self.updateState()


        self.loop += 1
        # if self.loop % 200 == 0:
        #     self.ACTION_STATES = {}
        #     self.VISITED_STATES = {}



class FerrariBot2():
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
        total = 0.0
        for direction in dd:
            (d_row, d_col) = ants.destination(a_row, a_col, direction)
            if (d_row, d_col) in self.other_ants_positions:
                value = 0.0
            else:
                if not ants.unoccupied(d_row, d_col):
                    value = 0.0
                else:
                    value = self.ACTION_STATES.get((direction, d_row, d_col), 2.0)/ self.VISITED_STATES.get((d_row, d_col),1.0)

                    if (d_row, d_col) == ants.closest_food(a_row,a_col,hunted):
                        value += 2.0
                    if (d_row, d_col) == ants.closest_enemy_hill(a_row,a_col):
                        value += 7.0
                    if (d_row, d_col) == ants.closest_enemy_ant(a_row,a_col,hunted):
                        value += 1.0
            total += value
            results.append((direction, (d_row, d_col), value))

        #prob_results = [(x[0], x[1], x[2]/total) for x in results]
        probs = [x[2]/total for x in results]
        random_prob =  random.random()
        #random_prob = 0.3
        if random_prob <= float(sum(probs[:1])):
        #if (random_prob <= probs[0]):
            best_dir = results[0][1]
            best_place = results[0][1]
        elif random_prob > float(sum(probs[:1])) and random_prob <= float(sum(probs[:2])):
            best_dir = results[1][0]
            best_place = results[1][1]         
        elif random_prob > float(sum(probs[:2])) and random_prob <= float(sum(probs[:3])):
            best_dir = results[2][0]
            best_place = results[2][1]
        else:
            best_dir = results[3][0]
            best_place = results[3][1]            

        results = sorted(results, key = lambda k: -k[2])
        best_dir = results[0][0]
        best_place = results[0][1]
        ants.issue_order((a_row, a_col, best_dir))
        
        self.VISITED_STATES[(d_row, d_col)] = self.VISITED_STATES.get(best_place,1.0) + 1.0
        self.ACTION_STATES[(best_dir, best_place[0], best_place[1])] = self.ACTION_STATES.get((best_dir, best_place[0], best_place[1]),1.0) + 1.0
        self.other_ants_positions.discard((a_row, a_col))
        self.other_ants_positions.add(best_place)

        
    def updateState(self):
        for position in self.ACTION_STATES:
            self.ACTION_STATES[position] = self.ACTION_STATES[position]*0.995
        for position in self.VISITED_STATES:
            self.VISITED_STATES[position] = self.VISITED_STATES[position]*0.995

    def do_turn(self, ants):
        self.other_ants_positions = set([])
        for a_row, a_col in ants.my_ants():

            self.takeAction(a_row, a_col, ants)
            self.updateState()


        self.loop += 1
        # if self.loop % 200 == 0:
        #     self.ACTION_STATES = {}
        #     self.VISITED_STATES = {}



if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    try:
        Ants.run(FerrariBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
