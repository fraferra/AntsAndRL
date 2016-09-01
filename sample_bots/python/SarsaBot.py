#!/usr/bin/env python

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
from random import shuffle, random
from ants import *
import numpy as np
import sys


class FerrariBot():
    def __init__(self):
        self.S = {}
        self.Q_sa = {}
        self.E = {}
        self.other_ants_positions = set([])
        self.loop = 1
        self.greedy = 0.9
        self.decay_coefficent = 0.1
        self.apha = 0.5
        self.lambd = 0.4

    def returnTmpValueState(self, a_row, a_col, direction):
        (d_row, d_col) = ants.destination(a_row, a_col, direction)
        hunted = []
        if (d_row, d_col) in self.other_ants_positions:
            return -1 
        elif not ants.unoccupied(d_row, d_col):
            return -1
        else:
            value = 0
            if (d_row, d_col) == ants.closest_food(a_row,a_col,hunted):
                value += 1
            if (d_row, d_col) == ants.closest_enemy_hill(a_row,a_col):
                value += 7.0
            if (d_row, d_col) == ants.closest_enemy_ant(a_row,a_col,hunted):
                value += 0.5    
            return value        



    def selectA(self, a_row, a_col):
        action_value_pairs = []
        directions = ["n","e","s","w"]
        shuffle(directions)
        for direction in directions:
            value = self.returnTmpValueState(a_row, a_col)
            action_value_pairs.append((direction, value))
        action_value_pairs = sorted(action_value_pairs, key = lambda k: -k[1])
        
        best_action = action_value_pairs[0][1]
        other_actions = [x[0] for x in action_value_pairs[1:]]
        
        random_prob = random()

        if random_prob <= self.greedy:
            return best_action
        else:
            shuffle(other_actions)
            return other_actions[0]

    def getNextState(self, S, action, ants):
        (d_row, d_col) = ants.destination(S[0], S[1], action)
        return (d_row, d_col)

    # def returnValueState(self, S, ants):
    #     a_row = S[0]
    #     a_col = S[1]
    #     hunted = []
    #     if (a_row, a_col) in self.other_ants_positions:
    #         return -1 
    #     elif not ants.unoccupied(a_row, a_col):
    #         return -1
    #     else:
    #         value = 0
    #         food_location = ants.closest_food(a_row,a_col,hunted)
    #         if food_location is not None:
    #             value += 1

    #         hill_location = ants.closest_enemy_hill(a_row,a_col)
    #         if hill_location is not None:
    #             value += 7.0

    #         enemy_location = ants.closest_enemy_ant(a_row,a_col,hunted)
    #         if enemy_location is not None:
    #             value += 0.5
   
    #         return value        


    def updateDelta(self, R, A, A_prime, S, S_prime):
        delta = R + self.decay_coefficent * self.Q_sa.get((A_prime, S_prime), 0.0) - self.Q_sa.get((A, S), 0.0)


    def selectAbasedonQ(self, S, ants):
        directions = ["n", "e","s","w"]
        shuffle(directions)
        action_Qsa = []
        for direction in directions:
            next_S = getNextState(S, direction, ants)
            value = self.Q_sa.get((direction, next_S), 0.0)
            action_Qsa.append(direction, value)

        action_value_pairs = sorted(action_Qsa, key = lambda k: -k[1])
        
        best_action = action_value_pairs[0][1]
        other_actions = [x[0] for x in action_value_pairs[1:]]
        
        random_prob = random()

        if random_prob <= self.greedy:
            return best_action
        else:
            shuffle(other_actions)
            return other_actions[0]        


    def do_turn(self, ants):
        self.other_ants_positions = set([])
        if self.loop % 50 == 0:
            self.E = {}

        directions = ["n", "e","s","w"]
        shuffle(directions)
        A = directions[0]
        S_prime = (0,0)
        for a_row, a_col in ants.my_ants():

            S = (a_row, a_col)

            ants.issue_order((S[0], S[1], A))

            S_prime = self.getNextState()

            R = self.returnValueState(S, ants)

            A_prime = self.selectAbasedonQ(S, ants)


            delta = self.updateDelta(R, A, A_prime, S, S_prime)

            self.E[(A, S)] = self.E.get((A,S) ,0.0) + 1.0

            self.Q_sa[(A, S)] = self.Q_sa.get((A,S), 0.0) + self.alpha*delta*self.E[(A,S)]
            self.E[(A,S)] = self.decay_coefficent*self.lambd*self.E[(A,S)]

            A = A_prime
            S = S_prime

            #self.updateState()
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
        Ants.run(FerrariBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
