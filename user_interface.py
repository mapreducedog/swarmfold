'''swarmass by mdp, zm
invocation
python3 swarmass.py [options]
'''
#builtin libraries
import sys
import itertools
import os
import json
import copy

#own libraries
import swarmass


default_options = [ 10, 5, 
'hhhhhhhhhhhhphphpphhpphhpphpphhpphhpphpphhpphhpphphphhhhhhhhhhhh', 
42, [getattr(swarmass.World, x) for x in [
            "pheromone_bias", "energy_bias", 
            "temp_energy", "min_pheromone_level", "pheromone_decay_rate"]], 3, 
os.path.join(".", "paths")]
current_options = copy.deepcopy(default_options)
    

def set_pop_size(x):
    '''the population size per generation, default:{}'''
    current_options[set_pop_size.pos] = int(x[0])
def set_number_generations(x):
    '''the number of generations, default:{}'''
    current_options[set_number_generations.pos] = int(x[0])
def set_polarity_string(x):
    '''the sequence to solve, default:{}'''
    current_options[set_polarity_string.pos] = "".join(x)
def set_parameters(x):
    '''set pheromone_bias (alpha), energy_bias (beta), temp_energy (gamma), min_pheromone_level (theta), pheremone_decay_rate (rho), you may enter "x" keep a value unchanged.
    default: {}'''
    
    '''if input was quoted, rather than multiple items (e.g),
    as a result of "swarmass -P "1.0, 3.0, 27"
    instead of "swarmass -P 1.0 3.0 27
    '''
    if len(x) == 1:
        #reformat it to x = ["1.0", "3.0", "27"]
        x = list(filter(None, x[0].replace(',',' ').split(' ')))
    
    for pos, entry in enumerate(x):
        if entry != 'x':
            current_options[set_parameters.pos][pos] = float(entry)
    
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

def print_settings():
    for flag in flags[start_offset:]:
        print("{0[1][1]} : {1}".format(flag, current_options[flag[0].pos]))

def save_settings_to_json():
    settings_dic = {x[1][1] : current_options[x[0].pos] for x in flags[start_offset:]}
    with open(os.path.join(current_options[set_output_directory.pos], "settings.txt"), 'w') as outfile:
        json.dump(settings_dic, outfile, indent = 1)

def load_settings_file(x):
    '''load settings from file,additional flags override the applicable file setting  '''
    filename = x[0]
    with open(filename) as infile:
        settings_dict = json.load(infile)
    name_pos_dict = {x[1][1] : x[0].pos for x in flags[start_offset:]}
    for name, value in settings_dict.items():
        current_options[name_pos_dict[name]] = value
    
    
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
                return list(itertools.takewhile(lambda x: not x.startswith("-"), 
                                                sys.argv[pos + 1:]))
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

'''
here we define the flags for the command_line interface
'''
flags = [(print_help, ('h', 'help'), False),
         (load_settings_file, ('f', 'file'), True),
         (set_pop_size,('p', 'population'), True),
         (set_number_generations, ('g', 'generations'), True),
         (set_polarity_string, ('s', 'sequence'), True),
         (set_target_score, ('t', 'target'), True),
         (set_parameters, ('P', 'parameters'), True),
         (set_dimensionality, ('d', 'dimensionality'), True),
         (set_output_directory, ('o', 'output'), True),
        ]

'''everything before start_offset 
(each argument listed before set_pop_size in flags),
is a 'preprocessing' flag that does not get 
entered into the current_options list'''
start_offset = (list(zip(*flags))[0].index(set_pop_size))

for pos, item in enumerate(flags[start_offset:],0):
    #set at which position in array this function puts its result
    item[0].pos = pos
    #show the default value in the docstring
    item[0].__doc__ = item[0].__doc__.format(default_options[pos])

#create the automatic doc
__doc__ += "\n".join(["-{1[0]}{3}, --{1[1]}{3}: {0.__doc__}".format(*(item + (" <args>" if item[-1] else "",))) for item in flags if any(item[1])]) 
__doc__ += '''
examples :
    swarmass --genarations 30 --population 20 --sequence hpphpphpphpph --target 5
    solve the sequence "hpphpphpphpph" in 30 generations with 20 ants in one generation with target score 5
    swarmass --file ./example/settings.txt --output ./example_2/ --generations 30
    perform the same test as ./example/settings.txt, execpt with 30 generations, and put the output in the example_2 folder
'''

if __name__ == '__main__':
    pass
    #main()
