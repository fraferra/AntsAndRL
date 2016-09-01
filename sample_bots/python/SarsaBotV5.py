#!/usr/bin/env python

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
from random import shuffle
from random import random as rnd
from ants import *
import sys
import datetime

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
            value = -5.0
        elif not ants.passable(a_row, a_col):
            self.walls[S] = -1
            value = -1.0
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
                value += 10.0
                if S == hill_location:
                    value += 4.0

            enemy_location = ants.closest_enemy_ant(a_row,a_col,hunted)
            if enemy_location is not None:
                value += 0.5
        #self.S[S] = 1.0*self.S.get(S, 0.0) + value
        self.tmp_Q_sa[S] = (self.tmp_Q_sa.get(S,0.0) + value)/2.0
        return value        


    def getNextState(self, S, action, ants):
        new_S = ants.destination(S[0], S[1], action)
        return new_S

    def findClosestEnemyHill(self, S, ants):
        #locations = ants.enemy_hills()
        locations = ants.closest_enemy_hill(S[0], S[1])
        sys.stderr.write(str(locations) + "\n")
        locations = [x[0] for x in locations]

        min_distance = 99999.0
        
        if locations is not None:
            closest_hill = locations[0]
            for location in locations:
                sys.stderr(location)
                if ants.distance(S[0],S[1], location[0], location[1]) < min_distance:
                    closest_hill = location
                    min_distance = ants.distance(S[0],S[1], location[0], location[1])
        else:
            return False
        #self.S[closest_hill] = 10.0
        return closest_hill

    def directionToClosestEnemyNest(self, S, ants):
        closest_hill = self.findClosestEnemyHill(S, ants)
        #closest_hill = ants.closest_enemy_hill(S[0], S[1])
        directions = ants.direction(S[0],S[1], closest_hill[0], closest_hill[1])
        return directions


    def selectA2(self, S, ants):
        directions = ["n", "e","s","w"]
        shuffle(directions)

        results  = []
        for direction in directions:
            S_next = self.getNextState(S, direction, ants)
            value = self.returnValueState(S_next, ants) #+ 0.2*self.tmp_Q_sa.get(S_next,0.0)

            try:
                enemy_directions = self.directionToClosestEnemyNest(S_next, ants)
                if enemy_directions != False:
                    if direction in enemy_directions:
                        value += 0.2
            except Exception as e:
                sys.stderr.write(str(e))
                sys.stderr.write("ciao \n")
            results.append((direction, value))

        results = sorted(results, key = lambda k: -k[1])
        if results[0][1] == results[1][1]:
            results = results[:2]
            shuffle(results)

        best_action = results[0][0]
        return best_action


    def selectA(self, S, ants):
        directions = ["n", "e","s","w"]
        shuffle(directions)

        results  = []
        for direction in directions:
            S_next = self.getNextState(S, direction, ants)
            value = self.returnValueState(S_next, ants) #+ 0.2*self.tmp_Q_sa.get(S_next,0.0) 
            # enemy_directions = self.directionToClosestEnemyNest(S_next, ants)
            # if enemy_directions != False:
            #     if direction in enemy_directions:
            #         value += 0.1

            results.append((direction, value))

        results = sorted(results, key = lambda k: -k[1])
        random_prob = rnd()
        if random_prob <= 1.0 - self.greedy:
            best_action = results[0][0]
        else:
            results = results[1:]
            shuffle(results)
            best_action = results[0][0]

        return best_action

    def do_turn(self, ants):
        self.other_ants_positions = set([])
        if self.loop % 20 == 0:
            self.tmp_Q_sa = {}
        if self.loop % 300 == 0:
            self.E = {}
            #self.S = {}
            #self.Q_sa = {}
        directions = ["n", "e","s","w"]
        shuffle(directions)

        start_time = datetime.datetime.now()

        for a_row, a_col in ants.my_ants():
            now = datetime.datetime.now()
            elapsed_time = now  - start_time
            #sys.stderr.write(str(int(elapsed_time.total_seconds() * 1000)) + "\n")
            if int(elapsed_time.total_seconds() * 1000) >= ants.turntime:
                sys.stderr.write(str(int(elapsed_time.total_seconds() * 1000)) + "\n")
                break

            S = (a_row, a_col)

            A = self.selectA(S, ants)

            ants.issue_order((S[0], S[1], A))

            S_prime = self.getNextState(S, A, ants)

            self.S[S] = (1.0+1.0/self.loop)*self.S.get(S, 0.0) + self.returnValueState(S, ants)
            self.Q_sa[(A, S)] = self.Q_sa.get((A,S), 0.0)
            self.other_ants_positions.add(S_prime)
            self.other_ants_positions.discard(S)


        self.loop += 1.0


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
