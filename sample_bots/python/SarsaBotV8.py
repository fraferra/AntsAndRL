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
        self.States = ["ENEMY_ANT", "MY_ANT","FOOD","ENEMY_HILL", "WALL", "FREE"]
        self.States_toggle = ["SEEN", "UNSEEN"]
        self.proximity = [0,1,2,4,5]
        self.seen_states = {}
        self.S = {}
        self.Q_sa = self.load_obj()
        self.tmp_Q_sa = {}
        self.walls = {}
        self.E = {}
        self.other_ants_positions = set([])
        self.loop = 1
        self.greedy = 0.05
        self.decay_coefficent = 0.9
        self.alpha = 0.8
        self.lambd = 1.0
        self.my_ants = 1
        self.enemy_ants = 2


    # def returnReward(self,S, ants):
    #     # previous_my_ants = self.my_ants()
    #     # self.my_ants = len(ants.my_ants())
    #     # value = 0
    #     # # if self.my_ants >= previous_my_ants:
    #     # #     value += 1
    #     # # else:
    #     # #     value -= 1
    #     # # previous_enemy_ants = self.enemy_ants
    #     # # self.enemy_ants = len(ants.enemy_ants())
    #     # # if previous_enemy_ants > self.enemy_ants:
    #     # #     value +=1
    #     V
    #     if S in self.other_ants_positions:
    #         value -= 5
    #     if  not ants.passable(S[0], S[1]):
    #         value -=2

    def getDistance(self, S, destination, ants):
        try:
            dist = ants.distance(S[0], S[1], destination[0], destination[1])
            if dist > 6:
                dist = 99
            return dist
        except IndexError:
            return 99

    def getDirections(self, S, destination, ants):
        dist = ants.direction(S[0], S[1], destination[0], destination[1])
        return dist

    def sameDirection(self, possible_direction, directions_toward_objective):
        if possible_direction in directions_toward_objective:
            return True
        else:
            return False

    def returnState(self,S, S_next, current_direction, ants):
        a_row = S_next[0]
        a_col = S_next[1]
        hunted = []
        value = 0.0
        food_location = ants.closest_food(a_row,a_col,hunted)
        hill_location = ants.closest_enemy_hill(a_row,a_col)
        enemy_location = ants.closest_enemy_ant(a_row,a_col,hunted)

        IS_BLOCKED = False

        PROXIMITY = 0.0

        POSITION_RELATIVE_TO_ANT = True

        if S_next in self.seen_states:
            STATE_TOGGLE = "SEEN"
        else:
            STATE_TOGGLE = "UNSEEN"  

        if S_next in self.other_ants_positions:
            STATE = "MY_ANT"
            PROXIMITY = 0.1
            IS_BLOCKED = True
            POSITION_RELATIVE_TO_ANT = self.getDirections(S, S_next, ants)[0]
            #POSITION_RELATIVE_TO_ANT != self.sameDirection(current_direction, self.getDirections(S, S_next, ants))
            return (STATE, STATE_TOGGLE, PROXIMITY, POSITION_RELATIVE_TO_ANT, IS_BLOCKED)
        elif not ants.unoccupied(a_row, a_col):# or not ants.unoccupied(S[0], S[1]):
            self.walls[S] = -1
            STATE = "WALL"
            PROXIMITY = 0.1
            IS_BLOCKED = True
            POSITION_RELATIVE_TO_ANT = self.getDirections(S, S_next, ants)[0]
            #POSITION_RELATIVE_TO_ANT != self.sameDirection(current_direction, self.getDirections(S, S_next, ants))
            return (STATE, STATE_TOGGLE, PROXIMITY, POSITION_RELATIVE_TO_ANT, IS_BLOCKED)
        elif hill_location is not None and self.getDistance(S, hill_location, ants) <= 4:
            PROXIMITY = self.getDistance(S, hill_location, ants)

            if S_next == hill_location:
                STATE = "FOOD"
                PROXIMITY = 0.1
                POSITION_RELATIVE_TO_ANT = self.getDirections(S, hill_location, ants)[0]
                #POSITION_RELATIVE_TO_ANT = self.sameDirection(current_direction, self.getDirections(S, hill_location, ants))
                return (STATE, STATE_TOGGLE, PROXIMITY, POSITION_RELATIVE_TO_ANT, IS_BLOCKED)
            else:
                STATE = "FOOD"
                IS_BLOCKED = self.isBlocked(S, hill_location, ants)
                POSITION_RELATIVE_TO_ANT = self.getDirections(S, hill_location, ants)[0]
                #POSITION_RELATIVE_TO_ANT = self.sameDirection(current_direction, self.getDirections(S, hill_location, ants))
                return (STATE, STATE_TOGGLE, PROXIMITY, POSITION_RELATIVE_TO_ANT, IS_BLOCKED)
        elif food_location is not None and self.getDistance(S, food_location, ants) <=4:
            if S_next == food_location:
                STATE = "FOOD"
                PROXIMITY = 0.1
                POSITION_RELATIVE_TO_ANT = self.getDirections(S, food_location, ants)[0]
                #POSITION_RELATIVE_TO_ANT = self.sameDirection(current_direction, self.getDirections(S, food_location, ants))
                return (STATE, STATE_TOGGLE, PROXIMITY, POSITION_RELATIVE_TO_ANT, IS_BLOCKED)
            else:
                STATE = "FOOD"
                PROXIMITY = self.getDistance(S, food_location, ants)
                IS_BLOCKED = self.isBlocked(S, food_location, ants)
                POSITION_RELATIVE_TO_ANT = self.getDirections(S, food_location, ants)[0]
                sys.stderr.write(str(POSITION_RELATIVE_TO_ANT)+"\n")
                #POSITION_RELATIVE_TO_ANT = self.sameDirection(current_direction, self.getDirections(S, food_location, ants))
                return (STATE, STATE_TOGGLE, PROXIMITY, POSITION_RELATIVE_TO_ANT, IS_BLOCKED)
        elif enemy_location is not None and self.getDistance(S, enemy_location, ants) <= 4:
            if S_next == enemy_location:
                STATE = "ENEMY_ANT"
                PROXIMITY = 0.1
                POSITION_RELATIVE_TO_ANT = self.getDirections(S, enemy_location, ants)[0]
                #POSITION_RELATIVE_TO_ANT = self.sameDirection(current_direction, self.getDirections(S, enemy_location, ants))
                return (STATE, STATE_TOGGLE, PROXIMITY, POSITION_RELATIVE_TO_ANT, IS_BLOCKED)
            else:
                STATE = "ENEMY_ANT"
                PROXIMITY = self.getDistance(S, enemy_location, ants)  
                IS_BLOCKED = self.isBlocked(S, enemy_location, ants)
                POSITION_RELATIVE_TO_ANT = self.getDirections(S, enemy_location, ants)[0]
                #POSITION_RELATIVE_TO_ANT =  self.sameDirection(current_direction, self.getDirections(S, enemy_location, ants))
                return (STATE, STATE_TOGGLE, PROXIMITY, POSITION_RELATIVE_TO_ANT, IS_BLOCKED)        
        else:
            STATE = "NOTHING"
            PROXIMITY = 1.0
            POSITION_RELATIVE_TO_ANT = self.getDirections(S, S_next, ants)[0]
            return (STATE, STATE_TOGGLE, PROXIMITY, POSITION_RELATIVE_TO_ANT, IS_BLOCKED)
        return (STATE, STATE_TOGGLE, PROXIMITY, POSITION_RELATIVE_TO_ANT, IS_BLOCKED)     

    def isBlocked(self, S, destination, ants):
        is_blocked = False
        while S != destination:
            directions = self.getDirections(S, destination, ants)
            for direction in directions:
                S = self.getNextState(S, direction, ants)
                if not ants.passable(S[0],S[1]):
                    is_blocked = True
                    break
            if is_blocked:
                break
        return is_blocked




    def returnValueState(self, S, S_next, A, ants):
        proximity_coefficient = 0.1

        STATE,STATE_TOGGLE,PROXIMITY,POSITION_RELATIVE_TO_ANT,IS_BLOCKED = self.returnState(S, S_next,A, ants)

        
        MY = ants.my_ants()
        sys.stderr.write(str(MY)+"\n")


        value = 0.0
        if S_next in self.other_ants_positions:
            value -= 100.0
        if IS_BLOCKED:
            value -= 100.0
        # if POSITION_RELATIVE_TO_ANT:
        #     value += 1.0
        # if POSITION_RELATIVE_TO_ANT is False:
        #     value -=1.0
        # if STATE_TOGGLE == "UNSEEN":
        #     #value += 0.0
        #     value += (2.0 + 1.0/self.loop)
        # if STATE_TOGGLE == "SEEN":
        #     value -= 0.2
            #value -= (0.1 + self.seen_states.get(S, 1.0))
        if STATE == "MY_ANT":
            value -= (200.0 + proximity_coefficient*PROXIMITY)
        if STATE == "WALL":
            value -= (100.0 + proximity_coefficient*PROXIMITY) 
        if STATE == "FOOD":
            if PROXIMITY == 0.1:
                value += 100.0
            if PROXIMITY == 1:
                value += 50.0
            if PROXIMITY > 6:
                value -= 100.0
            value += (5.0 - 1.5*proximity_coefficient*PROXIMITY) 
        if STATE == "ENEMY_HILL":
            value += (7.0 - proximity_coefficient*PROXIMITY) 
        if STATE == "ENEMY_ANT":
            value += (20.0 - proximity_coefficient*PROXIMITY) 
        if STATE == "NOTHING":
            value += 10.0
        return value
  


    def getNextState(self, S, action, ants):
        new_S = ants.destination(S[0], S[1], action)
        return new_S


    def selectA(self, S, ants):
        directions = ["n", "e","s","w"]
        shuffle(directions)

        results  = []
        for direction in directions:
            S_prime = self.getNextState(S, direction, ants)
            STATE_STATE_TOGGLE = self.returnState(S, S_prime, direction, ants)
            value = self.Q_sa.get((direction,STATE_STATE_TOGGLE), 10.0)#self.returnValueState(S_next, ants) + (1.0 + 1/self.loop)/self.S.get(S_next, 0.1)
            #self.Q_sa[STATE_STATE_TOGGLE] = 0.5*(self.Q_sa.get(STATE_STATE_TOGGLE, 0.0) +  self.returnValueState(S, S_prime, ants))
            #value = self.Q_sa.get(STATE_STATE_TOGGLE, 0.0)#self.returnValueState(S_next, ants) + (1.0 + 1/self.loop)/self.S.get(S_next, 0.1)

            #self.Q_sa[(direction,STATE_STATE_TOGGLE)] = 0.5*(self.Q_sa.get((direction,STATE_STATE_TOGGLE), 0.0) +  self.returnValueState(S, S_prime, ants))

            #value = self.Q_sa.get((direction,STATE_STATE_TOGGLE), 0.0)#self.returnValueState(S_next, ants) + (1.0 + 1/self.loop)/self.S.get(S_next, 0.1)
    
    
            # if enemy_directions != False:
            #     if direction in enemy_directions:
            #         value += 0.1

            results.append((direction, value))

        results = sorted(results, key = lambda k: -k[1])
        random_prob = rnd()
        if random_prob <= 1.0 - self.greedy:
            best_action = results[0][0]
        else:
            results = results[:]
            shuffle(results)
            best_action = results[0][0]

        return best_action


    def updateDelta(self, R, A, A_prime, S, S_prime, ants):
        STATE_STATE_TOGGLE = self.returnState(S, S_prime, A, ants)
        STATE_STATE_TOGGLE_prime = self.returnState(S, S_prime, A_prime, ants)
        delta = R + self.decay_coefficent * self.Q_sa.get((A_prime, STATE_STATE_TOGGLE_prime), 0.0) - self.Q_sa.get((A, STATE_STATE_TOGGLE), 0.0)
        #delta = R + self.decay_coefficent * self.Q_sa.get(STATE_STATE_TOGGLE_prime, 0.0) - self.Q_sa.get(STATE_STATE_TOGGLE, 0.0)
        return delta

    def save_obj(self,obj):
        with open('learningV8_2.pkl', 'wb') as f:
             pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        sys.stderr.write("SAVED!!!!! \n\n\n")

    def load_obj(self):
        try:
            with open('learningV8_2.pkl', 'rb') as f:
                return pickle.load(f)
        except (OSError, IOError) as e:
            return {}

    def do_turn(self, ants):
        self.other_ants_positions = set([])
        if self.loop % 20 == 0:
            self.tmp_Q_sa = {}
        if self.loop % 50 == 0.0:
            #self.E = {}
            self.save_obj(self.Q_sa)
            sys.stderr.write("100 LOOP \n\n")
            #self.S = {}
            #self.Q_sa = {}
        directions = ["n", "e","s","w"]
        shuffle(directions)

        start_time = datetime.datetime.now()

        A = "n"
        S = None

        for a_row, a_col in ants.my_ants():
            now = datetime.datetime.now()
            elapsed_time = now  - start_time
            #sys.stderr.write(str(int(elapsed_time.total_seconds() * 1000)) + "\n")
            if int(elapsed_time.total_seconds() * 1000) >= ants.turntime:
                sys.stderr.write(str(int(elapsed_time.total_seconds() * 1000)) + "\n")
                break
            S = (a_row, a_col)
            

            A = self.selectA(S, ants)

            previous_ants = len(ants.my_ants())

            ants.issue_order((S[0], S[1], A))

            
            next_ants = len(ants.my_ants())

            

            S_prime = self.getNextState(S, A, ants)
            STATE_STATE_TOGGLE = self.returnState(S, S_prime, A, ants)



            R = self.returnValueState(S, S_prime, A, ants)
            if  next_ants > previous_ants:
                 R += 50.0


            A_prime = self.selectA(S_prime, ants)

            delta = self.updateDelta(R, A, A_prime, S, S_prime, ants)

            #self.E[STATE_STATE_TOGGLE] = self.E.get(STATE_STATE_TOGGLE, 0.0) + 1.0
            self.E[(A, STATE_STATE_TOGGLE)] = self.E.get((A,STATE_STATE_TOGGLE), 0.0) + 1.0
            #self.Q_sa[(A,STATE_STATE_TOGGLE)] = 0.5*(self.Q_sa.get((A,STATE_STATE_TOGGLE), 0.0) +  self.alpha*delta)
            #self.Q_sa[STATE_STATE_TOGGLE] = 0.5*(self.Q_sa.get(STATE_STATE_TOGGLE, 0.0) +  self.alpha*delta)

            # self.E[(A, S)] = self.E.get((A,S) ,0.0) + 1.0

 

            maxQsa = max([self.returnValueState(S, S_prime, d, ants) for d in ["n","e","s","w"]])

            self.Q_sa[(A, STATE_STATE_TOGGLE)] = self.Q_sa.get((A, STATE_STATE_TOGGLE), 10.0) + self.alpha*(R + self.decay_coefficent*maxQsa - self.Q_sa.get((A, STATE_STATE_TOGGLE), 10.0))
            # for key in self.E:
            #     self.Q_sa[key] = 1.0*(self.Q_sa.get(key, 0.0) + self.alpha*delta*self.E[key])
            #     self.E[key] = self.decay_coefficent*self.lambd*self.E[key]

            self.seen_states[S] = self.seen_states.get(S, 0.0) + 1.0
            self.other_ants_positions.add(S_prime)
            self.other_ants_positions.discard(S)

            # S = S_prime
            # A = A_prime
        sys.stderr.write(str(self.Q_sa)+"\n")

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
