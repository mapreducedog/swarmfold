'''swarmass by mdp, zm
invocation
python3 swarmass.py [options]
'''

import sys
import swarmass
import itertools
import os

default_options = [10, 30, 'hhhhhhhhhhhhphphpphhpphhpphpphhpphhpphpphhpphhpphphphhhhhhhhhhhh', 42, 3, os.path.join(".", "paths")]
current_options = default_options[:]


def twod_path():
    '''fold in 2-dimensional space, rather than 3-dimensional''' 
    current_options[-1] = 2
    

def set_pop_size(x):
    '''the population size per generation, default:{}'''
    current_options[set_pop_size.pos] = int(x[0])
def set_number_generations(x):
    '''the number of generations, default:{}'''
    current_options[set_number_generations.pos] = int(x[0])
def set_polarity_string(x):
    '''the sequence to solve, default:{}'''
    current_options[set_polarity_string.pos] = int(x[0])
def set_parameters(x):
    "set pheremone_bias, energy_bias, temp_energy"
def set_target_score(x):
    '''the target score, default:{}'''
    current_options[set_target_score.pos] = int(x[0])
def set_dimensionality(x):
    '''set the dimensionality, choose 2 or 3, default is {}'''
    current_options[set_dimensionality.pos] = int(x[0])
    
def set_output_directory(x):
    '''save the the files to this directory, default "{}"
        will make the directory if it doesnt exist
    '''
    current_options[set_output_directory.pos] = " ".join(x)
def print_help():
    '''print help'''
    print(__doc__)
    exit()
    
    
def check_option(short_option, long_option, return_arguments = False):
    if not short_option:
        short_option = '_______________________________________'
    if not long_option:
        long_option = '_______________________________________'
    for option in ["-" + short_option,
                   "--" + long_option]:
        if option in sys.argv:
            pos = sys.argv.index(option)
            if return_arguments:
                return list(itertools.takewhile(lambda x: not x.startswith("-"), sys.argv[pos + 1:]))
            else:
                return True
    for pos, string in enumerate(sys.argv[1:], 1):
        if string.startswith("-") and not string.startswith('--'):
            if short_option in string:
                if return_arguments:
                    return list(itertools.takewhile(lambda x: not x.startswith("-"), sys.argv[pos + 1:]))
                return True
    return [] if return_arguments else False


def main():
    for item in flags:
        return_value = check_option(item[1][0], item[1][1], item[2])
        if return_value:
            if item[2]: #returns the arguments
                item[0](return_value) #apply the function to the arguments
            else:
                item[0]()    

flags = [(print_help, ('h', 'help'), False),
         (set_pop_size,('p', 'population'), True),
         (set_number_generations, ('g', 'generations'), True),
         (set_polarity_string, ('s', 'sequence'), True),
         (set_target_score, ('t', 'target'), True),
         (set_dimensionality, ('d', 'dimensionality'), True),
         (set_output_directory, ('o', 'output'), True),
        ]
for pos, item in enumerate(flags[1:],0):
    item[0].pos = pos
    item[0].__doc__ = item[0].__doc__.format(default_options[pos])
             
__doc__ += "\n".join(["-{1[0]}{3}, --{1[1]}{3}: {0.__doc__}".format(*(item + (" <args>" if item[-1] else "",))) for item in flags if any(item[1])]) 

if __name__ == '__main__':
    main()
