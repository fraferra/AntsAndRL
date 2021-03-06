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
        self.e = 0.3
        self.old_state = None
        self.old_action = None
        self.Q = self.load_obj()
        self.N = {}
        self.other_ants_positions = set([])
        self.count = 0
        self.loop = 0
        self.old_actions = [None]
        self.old_states = [None]

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
        
        return S_1




    def getDirections(self, S, destination, ants):
        dist = ants.direction(S[0], S[1], destination[0], destination[1])
        return dist

    def initialize_q(self):
        d = {}
        possible_states = []
        states = ["Nothing","Wall","Food", "Ant"]
        actions = ["n", "e", "s", "w"]
        d[None] = {}
        d[None][None] = 0.0
        for s1 in states:
            for s2 in states:
                for s3 in states:
                    for s4 in states:
                        d[(s1,s2,s3,s4)]={}
                        for a in actions:
                            d[(s1,s2,s3,s4)][a] = 10.0
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
            return -100
        elif loc in self.other_ants_positions:
            return -200
        else:
            return self.is_food_enemy_hill(loc, ants)


    def getState(self, loc, ants):
        directions = ["n", "e", "s", "w"]
        S = []
        for direction in directions:
            next_loc = self.getNextState(loc, direction, ants)
            value = self.is_state(next_loc, ants)
            S.append(value)
        return tuple(S)

    def is_state(self, loc, ants):
        if loc in self.other_ants_positions:
            return "Ant"
        elif not ants.passable(loc[0], loc[1]):
            return "Wall"
        elif self.returnValue(loc, ants) >= 100:
            return "Food"
        else:
            return "Nothing"



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
            return self.initialize_q()

    def UpdateQ(self, state, action, state_, action_, reward, explore):
        q = self.Q[state][action]
        q_ = self.Q[state_][action_]
        q += self.alpha * (reward + self.gamma * q_ - q)

        self.Q[state][action] = q



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
          action = max(actions, key = lambda x: self.Q[state][x])
          explore = False

        action = self.takeOppositeAction(action)
        #state_ = self.getState(self.getNextState(loc, action, ants), ants)
        state_ = self.create_quadrant(self.getNextState(loc, action, ants), ants)
        if rnd() < self.e:
          action_ = actions[random.randint(0, len(actions)-1)]
          explore = True
        # Exploit
        else:
          action_ = max(actions, key = lambda x: self.Q[state_][x])
          explore = False

        self.UpdateQ(self.old_state, self.old_action, state, action, reward, explore)
        self.old_action = action
        self.old_state = state
        

        return action

    def takeOppositeAction(self, action):
        if action == "n":
            return "s"
        if action == "s":
            return "n"
        if action == "w":
            return "e"
        else:
            return "w"

    def do_turn(self, ants):
        if self.loop % 50 == 0:
            self.save_obj(self.Q)
        idx = 0 

        for a_row, a_col in ants.my_ants()[:1]:

            loc = (a_row, a_col)
            #ants.issue_order((loc[0], loc[1], "w"))
            sys.stderr.write(str(loc) +"\n")
            reward = self.returnValue(loc, ants)
            action = self.Act(loc, reward, ants)
            
            ants.issue_order((loc[0], loc[1], action))
            next_loc = self.getNextState(loc, action, ants)
            self.other_ants_positions.add(next_loc)
            self.other_ants_positions.discard(loc)

            idx += 1
        sys.stderr.write(str(self.Q)+"\n")   
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
