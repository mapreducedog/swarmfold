'''
Documentation, License etc.


@package swarmass
'''

#builtins
import itertools
import random
import typing
import sys
import math
import os

#non-builtin
import numpy as np

#own
import check_score
import move
import user_interface


class World(list):
    pheromone_bias = 1.0 #1 #alpha in paper
    energy_bias = 2.0 #2#0.2 #beta in paper
    temp_energy = 1.0 #27     #gamma in paper
    min_pheromone_level = 0.05 #theta in paper
    pheromone_decay_rate = 0.98    #0.95 #rho in paper
    directions = list(move.vector.keys()) # ['l','r','f']
    dimensionality = 3
    with_votes = True
    output_directory = ""
    __base_pheromone__ = 1/len(directions)
    
    
    def __init__(self, sequence, target_score):
        super().__init__(({direction:self.__base_pheromone__ for direction in self.directions} 
                    for _ in sequence))
        self.votes = [{direction:0 for direction in self.directions} for _ in sequence]
        self.sequence = sequence
        self.target_score = -abs(target_score)
    
    @classmethod
    def set_dimensionality(cls, dimensionality = 2):
        cls.dimensionality = dimensionality
        if dimensionality == 2:
            cls.directions = ['l','r','f']
        elif dimensionality == 3:
            cls.directions = list(move.vector.keys())
        else :
            raise NotImplementedError("dimensionality should be 2 or 3")
        cls.__base_pheromone__ = 1/ len(cls.directions) 
        
    @classmethod
    def set_output_directory(cls, instr):
        cls.output_directory = instr
    def get_sequence(self, start, end):
        return self.sequence[start:end]
    
    def get_pheromone(self,position : int, direction : str) -> float: 
        return self[position][direction] ** self.pheromone_bias
    
    
    def get_path_prob_fwd(self, ant : move.Ant) -> typing.Dict[move.Ant, float]:
        def get_heur_pher(ant : move.Ant, direction: str ) -> float:
            return self.get_pheromone(ant.end, direction) * ant.conf_desirability()
        
        perdir = {
            new_ant: get_heur_pher(new_ant, n_direction) 
                for new_ant, n_direction in 
                    map(lambda direction:(ant.move_fwd(direction), direction),
                filter(ant.can_move_fwd, self.directions))
            }
        totvalue = sum(perdir.values())
        return {new_ant:value/totvalue for new_ant,value in perdir.items()}
    
    def get_path_prob_bck(self, ant : move.Ant) -> typing.Dict[move.Ant, float]:
        def get_heur_pher(ant : move.Ant, direction: str ) -> float:
            return self.get_pheromone(ant.end, direction) * ant.conf_desirability()
        
        perdir = {
            new_ant: get_heur_pher(new_ant, n_direction) 
                for new_ant, n_direction in 
                    map(lambda direction:(ant.move_bck(direction), direction),
                filter(ant.can_move_bck, self.directions))
            }
        totvalue = sum(perdir.values())
        return {new_ant:value/totvalue for new_ant,value in perdir.items()}
    

    def choose_path(self, path_prob : typing.Dict[move.Ant, float]) -> move.Ant:
        roll = random.random();
        sum_prob = 0;
        for ant, prob in path_prob.items():
            sum_prob += prob
            if sum_prob > roll:
                return ant
        
    def lay_pheromone_with_votes(self, ants: typing.Sequence[move.Ant]) -> None:
                #todo decay pheromone
        for pheromones in self.votes:
            for direction in pheromones:
                pheromones[direction] *= self.pheromone_decay_rate
        
        totscore = self.target_score #sum((ant.score for ant in ants)) or 1
        for ant in ants:
            ant.rel_score = abs(ant.score/self.target_score)
            for direction, votes in zip(ant.move_sequence, self.votes):
                votes[direction] += ant.rel_score #mutability carries through
        
        
        #normalizing the pheromone levels
        for votes, pheromones in zip(self.votes, self):
            totvalue = sum(votes.values())
            if totvalue == 0:
                continue
            for direction in pheromones:
                pheromones[direction] = votes[direction] / totvalue
            while min(pheromones.values()) < self.min_pheromone_level:
                lowest = min(pheromones, key = lambda x:pheromones[x])
                highest = max(pheromones, key = lambda x:pheromones[x])
                diff = self.min_pheromone_level - pheromones[lowest]
                pheromones[lowest] = self.min_pheromone_level
                pheromones[highest] -= diff
    def lay_pheromone_without_votes(self, ants: typing.Sequence[move.Ant]) -> None:
        #decay pheromone
        for pheromones in self:
            for direction in pheromones:
                pheromones[direction] *= self.pheromone_decay_rate
        
        totscore = self.target_score #sum((ant.score for ant in ants)) or 1
        #update the pherome level 
        for ant in ants:
            ant.rel_score = ant.score / totscore
            for direction, pheromones in zip(ant.move_sequence, self):
                pheromones[direction] += ant.rel_score #mutability carries through
        
        
        #normalizing the pheromone levels
        for pheromones in self:
            totvalue = sum(pheromones.values())
            for direction in pheromones:
                pheromones[direction] /= totvalue
            while min(pheromones.values()) < self.min_pheromone_level:
                lowest = min(pheromones, key = lambda x:pheromones[x])
                highest = max(pheromones, key = lambda x:pheromones[x])
                diff = self.min_pheromone_level - pheromones[lowest]
                pheromones[lowest] = self.min_pheromone_level
                pheromones[highest] -= diff
    
    def lay_pheromone(self, ants: typing.Sequence[move.Ant]) -> None:
        if self.with_votes:
            self.lay_pheromone_with_votes(ants)
        else:
            self.lay_pheromone_without_votes(ants)
    def get_max_phero_path(self):
        return "".join([max(pher, key = pher.get) for pher in self])
    
    
    def move_ants(self, ants : typing.Sequence[move.Ant]) -> typing.List[move.Ant]:
        make_new_ant = lambda : move.Ant(random.randint(0, len(self) - 1), random.choice(self.directions)).as_new(self)
        
        select_fwd = lambda ant: ant if ant.reached_end() else \
                    self.choose_path(self.get_path_prob_fwd(ant)) #if no possible successor, return this ant 
        select_bck = lambda ant: ant if ant.reached_start() else \
                    self.choose_path(self.get_path_prob_bck(ant))
        finished_ants = []
        walking_ants = ants[:]
        tries = 0
        while walking_ants:
            queued_ants = []
            for ant in walking_ants:
                new_ant = select_bck(ant)
                if new_ant is None:
                    queued_ants.append(make_new_ant())
                    continue
                new_ant = select_fwd(new_ant)
                if new_ant is None:
                    queued_ants.append(make_new_ant())
                    continue
                if new_ant.completed_path():
                    finished_ants.append(new_ant)
                else:
                    queued_ants.append(new_ant)
            walking_ants = queued_ants
            #tries += 1
        return finished_ants
        #walking_ants, finished_ants =
        
        #[self.choose_path(self.get_path_prob(ant, ))]
        #return [select_fwd(select_bck(ant)) for ant in ants]
        
def plot_ant(ant, gen = 0):
    ant_name = os.path.join(World.output_directory, "Ant_Gen_{}_{}".format(gen, ant.score))
    ant.save_to_json(ant_name)
    check_score.make_plot(ant.coord_sequence, ant.world.sequence, name = ant_name, dimensionality=World.dimensionality)
    

def plot_pher_route(world, gen = 0):
    min_route = "".join([max(pher, key = pher.get) for pher in world])
    score = check_score.score_config(min_route, world.sequence)
    check_score.test_plot(min_route, world.sequence, name = "World Gen {} {} ".format(gen, score))

def test_single(pop_size, generations,polarity_string = 'hphhpphhhhphhhpphhpphphhhphphhpphhppphpppppppphh', 
                target_score = 32):
    world = World(polarity_string, target_score)
    #check_score.plot_world_phero(world)
    #w = World('hpphpphpphpphpph')
    best = type('Ant', (object, ), {'score': 0})
    means = []
    mins = []
    for i in range(generations):
        old_path = world.get_max_phero_path()
        a = [move.Ant(random.randint(0, len(world) - 1), random.choice(world.directions)).as_new(world) for _ in range(pop_size)]
        print("generation {}".format(i + 1))
        successful_ants = world.move_ants(a)
        if successful_ants:
            pop_best = min(successful_ants, key = lambda ant:ant.score)
            if pop_best.score < best.score:
                best = pop_best
            mean = sum((x.score for x in successful_ants))/len(successful_ants)
            mins.append(pop_best.score)
            means.append(mean)
            print("succesfull paths : {}".format(len(successful_ants)))
            print("min : {}".format(pop_best.score))
            print("mean : {}".format(mean))
            laying_ants = list(sorted(successful_ants, key = lambda x:x.score))[0:len(successful_ants)//5]
            print("{} ants will place their pheromones".format(len(laying_ants)))
            #b = list(filter(lambda x: x.score < (pop_best.score +  mean)/2, b))
            plot_ant(pop_best, i)
        world.lay_pheromone(laying_ants)
        #check_score.plot_world_phero(world, i + 1)
        new_path = world.get_max_phero_path()
        print("Fraction Changes: {}".format(sum(map(lambda x,y: x != y, new_path, old_path))/ len(new_path)))
        
    #plot_pher_route(w)
    check_score.plot_history(mins, os.path.join(World.output_directory, "history"))
    a = best
    print(a.score)
    #[print(coord.T, dire) for coord, dire in zip(a.coord_sequence, a.move_sequence)]
    plot_ant(a, "final")
    return world,successful_ants + [a]

if __name__ == '__main__':
    user_interface.main()
    World.set_dimensionality(user_interface.current_options[user_interface.set_dimensionality.pos])
    World.set_output_directory(user_interface.current_options[user_interface.set_output_directory.pos])
    if not os.path.exists(World.output_directory):
        os.makedirs(World.output_directory)
    my_world,my_ant = test_single(*user_interface.current_options[:user_interface.set_target_score.pos + 1])
