#builtin libraries
import typing
from collections import namedtuple
from functools import reduce
import math
import random
import json
import os

#external libraries
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

#own libraries
import check_score




#As in Backofen 2000
vector = { #these are column vectors
    'f':np.matrix('1;0;0'),
    'l':np.matrix('0;1;0'),
    'u':np.matrix('0;0;1'),
    'r':np.matrix('0;-1;0'),
    'd':np.matrix('0;0;-1'),    
}

block = {
    'f':np.matrix(np.eye(3)),
    'l':np.matrix(
            '0  -1  0;'
            '1   0  0;'
            '0   0  1'),
    'u':np.matrix(
            '0  0 -1;'
            '0  1  0;'
            '1  0  0'),
    'r':np.matrix(
            '0  1  0;'
            '-1 0  0;'
            '0  0  1'),
    'd':np.matrix(
            '0  0  1;'
            '0  1  0;'
            '-1 0  0'),    
    }
    
class Ant(namedtuple('Ant', 'start move_sequence')):
    #__slots__ = ('start','move_sequence','world','tail_block', 'head_block', 'coord_sequence')
    #head is the side with the highest index
    #tail is the start with the lowest index
    #start is the index of the tail
    def __init__(self, start, move_sequence) -> None:
        self.end = self.start + len(move_sequence) - 1
        
    def as_new(self, world : 'swarmass.World') -> 'Ant':
        '''to initialize a new ant '''
        self.inherit_world(world)
        self.tail_block = block[self.move_sequence[0]]
        self.score = 0 if len(self.move_sequence) < 2 else check_score.score_config(self.move_sequence, self.world.get_sequence(self.start, self.end+1))
        
        self.head_block = block[self.move_sequence[-1]] 
        self.coord_sequence = [np.matrix('0;0;0')]
        self.new_connections = 0
        return self
    
    
        
    def inherit_world(self, world: 'swarmass.World') -> 'Ant':
        self.temp_energy = world.temp_energy
        self.energy_bias = world.energy_bias
        self.world = world
        return self
    def completed_path(self) -> bool:
        return len(self.move_sequence) == len(self.world.sequence)
    
    def reached_end(self) -> bool:
        '''whether head has reached the terminal'''
        return self.end + 1 == len(self.world.sequence)
    
    def reached_start(self) -> bool:
        '''whether tail has reached terminal'''
        return self.start == 0
    
    
    def is_occupied(self, coord : np.matrix) ->  bool:
        '''already visited coord'''
        return any(map(lambda x:(x == coord).all(), self.coord_sequence))
    
    def can_move_fwd(self, direction : str) -> bool:
        new_head_coord = self.coord_sequence[-1] \
            + self.head_block*vector[direction]
        return not self.is_occupied(new_head_coord)
    
    def can_move_bck(self, direction : str) -> bool:
        new_tail_block = self.tail_block * block[direction].getI()
        next_tail_coord = self.coord_sequence[0] - (new_tail_block * vector[direction])
        return not self.is_occupied(next_tail_coord)
    
    def conf_desirability(self) -> float:
        '''in paper: exp(- gamma * new_connections)
        here we exp(-gamma * new_connections * beta) 
        as this method is only used in swarmass.world.move.get_path_prob_{fwd,bck}.get_heur_pher
        we can rewrite formula(2) in the paper:
        rewriting the exp(- gamma * new_connections)^beta 
        to exp(- gamma * new_connections * beta)
        '''
        return math.exp(self.temp_energy * self.new_connections * self.energy_bias)
    
    
    
    def move_fwd(self, direction : str) -> 'Ant':
        next = Ant(self.start, self.move_sequence + direction).inherit_world(self.world)
        next.tail_block = self.tail_block
        
        new_head_coord = self.coord_sequence[-1] \
            + self.head_block*vector[direction]
        if self.is_occupied(new_head_coord):
            raise AssertionError("Constructed invalid path!")
        next.coord_sequence = self.coord_sequence  + [new_head_coord]  #add the newest node to the sequence
        next.head_block = self.head_block * block[direction]
        
        next.new_connections = score_new_node(next.coord_sequence, next.world.sequence[next.start:next.end + 1], -1)
        next.score = self.score - next.new_connections
        return next
    
    def attrite_bck(self) -> 'Ant':
        '''refolds the lower-indexed half to a random configuration,
        to be called when no move_bck can be performed with the  current configuration'''
        cutlength = (self.end + 1 - self.start) // 2 
        cutpoint = self.start + cutlength #cut before number
        next = Ant(self.cutpoint, self.move_sequence[cutlength:]).inherit_world(self.world)
        
        #determine the tail block of 'next'
        next.tail_block = self.tail_block
        for direction in self.move_sequence[:cutlength]:
            next.tail_block *= block['direction'] 
        possible_next_move = [x for x in world.directions if next.can_move_bck(x) and x != self.move_sequence[cutlength - 1]]
        next.score = check_score.score_config(next.move_sequence, next.world.get_sequence(next.start, next.end + 1))
        
        random.shuffle(possible_next_move) #shuffles in place.
        
            
            
    
    def move_bck(self, direction : str) -> 'Ant':
        '''moves the tail (lowest-indexed side) one step towards 0 in direction'''
        next = Ant(self.start - 1, direction + self.move_sequence).inherit_world(self.world)
        next.head_block = self.head_block
        
        next.tail_block = self.tail_block * block[direction].getI()
        next_tail_coord = self.coord_sequence[0] - (next.tail_block * vector[direction])
        if self.is_occupied(next_tail_coord): #Two nodes at the same place, thus invalid
            raise AssertionError("Constructed invalid path!")
        
        next.coord_sequence = [next_tail_coord] \
                                + self.coord_sequence
                            
        next.new_connections = \
        score_new_node(next.coord_sequence, next.world.sequence[next.start:next.end + 1], 0)
        next.score = self.score - next.new_connections
        return next
    
    def save_to_json(self, filename : str) -> None:
        save_attributes = [ "move_sequence", ]
        outdic = {x : getattr(self, x) for x in save_attributes}
        outdic.update({x : getattr(self.world, x) for x in ["dimensionality", "target_score"]})
        outdic['polar_sequence'] = self.world.sequence
        outdic['coord_sequence'] = [x.tolist() for x in self.coord_sequence]
        with open("{}.json".format(filename), 'w') as outfile:
            json.dump(outdic, outfile)

def score_new_node(coord_sequence : typing.List[np.matrix],  polarity_sequence : str, node_index : int) -> int:
    if node_index == -1:
        node_index = len(coord_sequence) - 1
    node_coords = coord_sequence[node_index]
    if polarity_sequence[node_index] == 'p':
        return 0
    return  sum(\
            map(lambda x:x[1] == 'h' #is hydrophobic 
                and abs(x[2] - node_index) > 1  #is not directly next in the sequence (or itself)
                and abs(x[0] - node_coords).sum() == 1, #is adjacent
            zip(coord_sequence, polarity_sequence, range(len(polarity_sequence))))) #how do I LISP in python?
    



    
if __name__ == '__main__':
    w = type('World', (object, ), {'sequence': 'hphphphph', 'temp_energy':0.1,'energy_bias':0.1})
    a = Ant(3, 'f').as_new(w)
    b = a.move_fwd('u')
    c = b.move_bck('f')
    
