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
        self.greedy = 0.05
        self.decay_coefficent = 1.0
        self.alpha = 0.05
        self.lambd = 0.1

    def getDirections(self, S, destination, ants):
        dist = ants.direction(S[0], S[1], destination[0], destination[1])
        return dist

    def returnValueState2(self,previous_S, S, direction, ants):
        a_row = S[0]
        a_col = S[1]
        hunted = []
        next_next_state = self.getNextState(S, direction, ants)
        value = 0.0
        if (a_row, a_col) in self.other_ants_positions:
            value -= 15.0
        elif not ants.passable(a_row, a_col):
            self.walls[S] = -1
            value -= 2.0

        else:
            value = 1.0 / self.S.get(S, 1.0) 

            if S not in self.S:
                value += 3.0

            #value += self.returnValueStateBasedOnObstaclesAround(S, ants)

            food_location = ants.closest_food(a_row,a_col,hunted)
            if food_location is not None:
                value += 5.0
                path = self.get_path(previous_S, food_location, ants)
                if len(path) > 0:
                    next_S_based_on_path_1 = self.getNextState(previous_S, path[0], ants)
                    if next_S_based_on_path_1 == S:
                        value += 2.0
                if len(path) >1:
                    next_S_based_on_path_2 = self.getNextState(previous_S, path[1], ants)
                    if next_S_based_on_path_2 == S:
                        value += 2.0
                if len(path) == 0:
                    value -= 7.0
                        
                if S == food_location:
                    value += 4.0
            hill_location = ants.closest_enemy_hill(a_row,a_col)
            if hill_location is not None:
                value += 10.0
                path = self.get_path(previous_S, hill_location, ants)
                if len(path) > 0:
                    next_S_based_on_path = self.getNextState(previous_S, path[0], ants)
                    if next_S_based_on_path == S:
                        value += 4.0
                        sys.stderr.write("CIAO\n")
                else:
                    value -= 11.0
                if S == hill_location:
                    value += 4.0

            enemy_location = ants.closest_enemy_ant(a_row,a_col,hunted)
            if enemy_location is not None:
                value += 0.5
        #self.S[S] = 1.0*self.S.get(S, 0.0) + value
        self.tmp_Q_sa[S] = (self.tmp_Q_sa.get(S,0.0) + value)/2.0
        return value   


    def returnValueState(self,previous_S, S, direction, ants):
        a_row = S[0]
        a_col = S[1]
        hunted = []
        next_next_state = self.getNextState(S, direction, ants)
        value = 0.0
        if (a_row, a_col) in self.other_ants_positions:
            value -= 50.0
        if not ants.passable(a_row, a_col):
            self.walls[S] = -1
            value -= 5.0
        if not ants.passable(next_next_state[0], next_next_state[1]):
           value -= 2.0
        if ants.passable(a_row, a_col):
            self.walls[S] = -1
            value += 2.0
        #value += 2.0 / self.S.get(S, 1.0) 
        value -= 0.001*self.S.get(S, 1.0)
        if S not in self.S:
            value += 3.0

        #value += self.returnValueStateBasedOnObstaclesAround(S, ants)

        food_location = ants.closest_food(a_row,a_col,hunted)
        if food_location is not None:
            value += 5.0
            path = self.get_path(previous_S, food_location, ants)
            if len(path) > 0:
                next_S_based_on_path_1 = self.getNextState(previous_S, path[0], ants)
                if next_S_based_on_path_1 == S:
                    value += 2.0
            if len(path) >1:
                next_S_based_on_path_2 = self.getNextState(previous_S, path[1], ants)
                if next_S_based_on_path_2 == S:
                    value += 2.0
            if len(path) == 0:
                value -= 7.0
                    
            if S == food_location:
                value += 4.0
        hill_location = ants.closest_enemy_hill(a_row,a_col)
        if hill_location is not None:
            value += 10.0
            path = self.get_path(previous_S, hill_location, ants)
            if len(path) > 0:
                next_S_based_on_path = self.getNextState(previous_S, path[0], ants)
                if next_S_based_on_path == S:
                    value += 4.0
                    sys.stderr.write("CIAO\n")
            else:
                value -= 11.0
            if S == hill_location:
                value += 4.0

        enemy_location = ants.closest_enemy_ant(a_row,a_col,hunted)
        if enemy_location is not None:
            value += 0.5
        #self.S[S] = 1.0*self.S.get(S, 0.0) + value
        self.tmp_Q_sa[S] = (self.tmp_Q_sa.get(S,0.0) + value)/2.0
        #sys.stderr.write(str(value) +"\n")
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


    def get_path(self, loc, destination, ants):
        is_blocked = False
        directions_to_destination = []
        while loc != destination:
            directions = self.getDirections(loc, destination, ants)
            for direction in directions:
                loc = self.getNextState(loc, direction, ants)
                if not ants.passable(loc[0],loc[1]):
                    is_blocked = True
                    break
                else:
                    directions_to_destination.append(direction)
            if is_blocked:
                break
        if len(directions_to_destination) > 5:
            directions_to_destination = []
        return directions_to_destination

    def selectA(self, S, ants):
        directions = ["n", "e","s","w"]
        #shuffle(directions)

        results  = []
        for direction in directions:
            S_next = self.getNextState(S, direction, ants)
            value = self.returnValueState(S, S_next, direction,  ants) #+ 0.2*self.tmp_Q_sa.get(S_next,0.0) 
            # enemy_directions = self.directionToClosestEnemyNest(S_next, ants)
            # if enemy_directions != False:
            #     if direction in enemy_directions:
            #         value += 0.1

            results.append((direction, value))
        sys.stderr.write(str(results)+"\n")
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
        if self.loop % 200 == 0:
            self.E = {}
            self.S = {}
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

            self.S[S] = self.S.get(S, 1.0) + 1.0
            #self.S[S] = (1.0+1.0/self.loop)*self.S.get(S, 0.0) + self.returnValueState(S, S_prime, A, ants) + 0.1
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
