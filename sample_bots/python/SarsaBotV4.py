#!/usr/bin/env python

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
from random import shuffle
from random import random as rnd
from ants import *
import numpy as np
import sys


class SarsaBot():
    def __init__(self):
        self.S = {}
        self.Q_sa = {}
        self.tmp_Q_sa = {}
        self.walls = {}
        self.E = {}
        self.other_ants_positions = set([])
        self.loop = 1
        self.greedy = 0.001
        self.decay_coefficent = 1.0
        self.alpha = 0.05
        self.lambd = 0.1

    def returnValueState(self, S, ants):
        a_row = S[0]
        a_col = S[1]
        hunted = []
        if (a_row, a_col) in self.other_ants_positions:
            return -5.0
        elif not ants.passable(a_row, a_col):
            self.walls[S] = -1
            return -1.0
        else:
            value = 1.0 / self.S.get(S, 1.0) 

            #value += self.returnValueStateBasedOnObstaclesAround(S, ants)

            food_location = ants.closest_food(a_row,a_col,hunted)
            if food_location is not None:
                value += 5.0
                if S == food_location:
                    value += 4.0
            hill_location = ants.closest_enemy_hill(a_row,a_col)
            if hill_location is not None:
                value += 7.0

            enemy_location = ants.closest_enemy_ant(a_row,a_col,hunted)
            if enemy_location is not None:
                value += 0.5
            self.tmp_Q_sa[S] = (self.tmp_Q_sa.get(S,0.0) + value)/2.0
            return value        


    def getNextState(self, S, action, ants):
        new_S = ants.destination(S[0], S[1], action)
        return new_S


    def updateDelta(self, R, A, A_prime, S, S_prime):
        delta = R + self.decay_coefficent * self.Q_sa.get((A_prime, S_prime), 0.0) - self.Q_sa.get((A, S), 0.0)
        return delta

    def selectAbasedonQ(self, S, ants):
        directions = ["n", "e","s","w"]
        shuffle(directions)
        action_Qsa = []
        for direction in directions:
            next_S = self.getNextState(S, direction, ants)
            value = self.Q_sa.get((direction, next_S), 0.0) + self.returnValueState(next_S, ants) + 0.1*self.tmp_Q_sa.get(next_S, 0.0)
            action_Qsa.append((direction, value))

        action_value_pairs = sorted(action_Qsa, key = lambda k: -k[1])
        
        best_action = action_value_pairs[0][0]
        other_actions = [x[0] for x in action_value_pairs[1:]]
        
        random_prob = rnd()

        if random_prob <= 1.0 - self.greedy:
            return best_action
        else:
            shuffle(other_actions)
            return other_actions[0] 




    # def findClosestEnemyHill(self, S, ants):
    #     locations = ants.enemy_hills()
    #     min_distance = 99999.0
        
    #     if locations is not None:
    #         closest_hill = locations[0]
    #         for location in locations:
    #             if ants.distance(S[0],S[1], location[0], location[1]) < min_distance:
    #                 closest_hill = location
    #     return closest_hill


    # def findPathToEnemyHill(self, S, ants):


    def do_turn(self, ants):
        self.other_ants_positions = set([])
        if self.loop % 5 == 0:
            self.tmp_Q_sa = {}
        if self.loop % 200 == 0:
            self.E = {}
            self.S = {}
            #self.Q_sa = {}
        directions = ["n", "e","s","w"]
        shuffle(directions)

        for a_row, a_col in ants.my_ants():

            S = (a_row, a_col)

            A = self.selectAbasedonQ(S, ants)

            S_prime = self.getNextState(S, A, ants)

            ants.issue_order((S[0], S[1], A))

            R = self.returnValueState(S, ants)

            A_prime = self.selectAbasedonQ(S_prime, ants)


            delta = self.updateDelta(R, A, A_prime, S, S_prime)

            self.E[(A, S)] = self.E.get((A,S) ,0.0) + 1.0

            self.Q_sa[(A, S)] = 0.85*self.Q_sa.get((A,S), 0.0) + self.alpha*delta*self.E[(A,S)]
            self.E[(A,S)] = self.decay_coefficent*self.lambd*self.E[(A,S)]
            self.S[S] = 0.90*self.S.get(S, 0.0) + 1.0
            self.tmp_Q_sa[S] = 0.60*self.tmp_Q_sa.get(S, 0.0) + 0.1
            self.other_ants_positions.add(S_prime)
            self.other_ants_positions.discard(S)


        self.loop += 1


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
        Ants.run(SarsaBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
