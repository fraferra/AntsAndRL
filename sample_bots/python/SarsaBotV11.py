#!/usr/bin/env python

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
from random import shuffle
from random import random as rnd
from ants import *
import sys
import datetime
import pickle
import math

class SarsaBot():
    def __init__(self):
        self.gamma = 0.9
        self.alpha = 0.8
        self.map = {}
        self.e = 0.3
        self.old_state = None
        self.old_action = None
        self.Q = self.load_obj()
        self.N = {}
        self.other_ants_positions = set([])
        self.count = 0
        self.loop = 0

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
        return directions_to_destination

    def getDistance(self, loc, destination, ants):
        try:
            dist = ants.distance(loc[0], loc[1], destination[0], destination[1])
            return dist
        except IndexError:
            return 99

    def create_quadrant(self, loc, ants):
        S_1 = self.getState(loc, ants)
        actions = ["n", "e", "s", "w"]
        for a in actions:
            next_loc = self.getNextState(loc, a, ants)
            tmp_S = self.getState(next_loc, ants)
            S_1 += (tmp_S)
            for a_2 in actions:
                next_loc_2 = self.getNextState(next_loc, a_2, ants)
                tmp_S = self.getState(next_loc_2, ants)
                S_1 += (tmp_S)                
        return S_1




    def getDirections(self, S, destination, ants):
        dist = ants.direction(S[0], S[1], destination[0], destination[1])
        return dist

    def initialize_q(self):
        d = {}
        possible_states = []
        states = [0,1,-1, 2, -2]
        actions = ["n", "e", "s", "w"]

        for s1 in states:
            for s2 in states:
                for s3 in states:
                    for s4 in states:
                        d[(s1,s2,s3,s4)]={}
                        for a in actions:
                            d[(s1,s2,s3,s4)][a] = 0.0
        return d

    def is_food_enemy_hill(self, loc, ants):
        hunted = []
        food_location = ants.closest_food(loc[0],loc[1],hunted)
        hill_location = ants.closest_enemy_hill(loc[0],loc[1])
        if food_location is not None:
            #sys.stderr.write(str(self.get_path(loc, food_location, ants))+"\n")
            if loc == food_location:
                return 2
        if hill_location is not None:
            if loc == hill_location:
                return 1
        return 0

    def bestMove(self, loc, ants):
        hunted = []
        
        directions = ["n", "e", "s", "w"]

        best_a = directions[0]

        food_location = ants.closest_food(loc[0],loc[1],hunted)
        hill_location = ants.closest_enemy_hill(loc[0],loc[1])

        if food_location is not None:
            food_path = self.get_path(loc, food_location, ants)
            if len(food_path) > 0:
                food_path = food_path[:2]
                shuffle(food_path)
                best_a = food_path[0]

        if hill_location is not None:
            enemy_path = self.get_path(loc, hill_location, ants)
            if len(enemy_path) > 0:
                enemy_path = enemy_path[:2]
                shuffle(enemy_path)
                best_a = enemy_path[0]
        next_loc = self.getNextState(loc, best_a, ants)
        if next_loc in self.other_ants_positions:
            shuffle(directions)
            best_a = directions[0]
        return best_a

    def returnValue(self, loc, ants):
        if not ants.passable(loc[0], loc[1]):
            return -1
        elif loc in self.other_ants_positions:
            return -2
        else:
            return self.is_food_enemy_hill(loc, ants)


    def getState(self, loc, ants):
        directions = ["n", "e", "s", "w"]
        S = []
        for direction in directions:
            next_loc = self.getNextState(loc, direction, ants)
            value = self.returnValue(next_loc, ants)
            S.append(value)
        return tuple(S)





    def getNextState(self, loc, action, ants):
        next_loc = ants.destination(loc[0], loc[1], action)
        return next_loc


    def save_obj(self,obj):
        with open('learningV10.pkl', 'wb') as f:
             pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        sys.stderr.write("SAVED!!!!! \n\n\n")

    def load_obj(self):
        try:
            with open('learningV10.pkl', 'rb') as f:
                return pickle.load(f)
        except (OSError, IOError) as e:
            return {}#self.initialize_q()

    def UpdateQ(self, state, action, state_, action_, reward, explore):

        q = self.Q.get((state, action), 10.0)
        q_ = self.Q.get((state_, action_), 10.0)
        q += self.alpha * (reward + self.gamma * q_ - q)

        self.Q[(state, action)] = q



    def Act(self, loc, reward, ants):

        #state = self.getState(loc, ants)
        state = self.create_quadrant(loc, ants)

        self.count += 1
        if self.count == 10000:
          self.e -= self.e/20
          self.count = 1000

        
        actions = ["n","e","s","w"]
        # Explore
        if rnd() < self.e:
          action = actions[random.randint(0, len(actions)-1)]
          explore = True
        # Exploit
        else:
          action = max(actions, key = lambda x: self.Q.get((state,x), 10.0))
          explore = False

        #state_ = self.getState(self.getNextState(loc, action, ants), ants)
        state_ = self.create_quadrant(self.getNextState(loc, action, ants), ants)
        if rnd() < self.e:
          action_ = actions[random.randint(0, len(actions)-1)]
          explore = True
        # Exploit
        else:
          action_ = max(actions, key = lambda x: self.Q.get((state_,x), 10.0))
          explore = False

        self.UpdateQ(state, action, state_, action_, reward, explore)

        return action


    def do_turn(self, ants):
        if self.loop % 50 == 0:
            self.save_obj(self.Q)
        for a_row, a_col in ants.my_ants():

            loc = (a_row, a_col)
            reward = self.returnValue(loc, ants)
            action = self.Act(loc, reward, ants)
            #sys.stderr.write(str(self.Q)+"\n")
            ants.issue_order((loc[0], loc[1], action))
            next_loc = self.getNextState(loc, action, ants)
            self.other_ants_positions.add(next_loc)
            self.other_ants_positions.discard(loc)
            
        self.loop +=1



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
