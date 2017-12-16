

#external libraries
import matplotlib
matplotlib.use('Qt4Agg') #
import matplotlib.pyplot as plt
import numpy as np
import os

#builtin libraries
import time
import math
from functools import reduce
import move
import itertools
import json

plot_with_legend = True

polarity_colors = { 'h' : 'red', 'p' : 'blue'}
polarity_full_name = {'h': 'hydrophobic', 'p':'polar'}


def get_coords_blocks(move_sequence):
    coord = np.matrix('0;0;0')
    move_block = move.block['f']
    #yield (coord, move_block)
    coord = coord + move.vector['f'] #the first move is "relative-free"
    move_block = move.block['f']
    #yield (coord, move_block)
    for direction in move_sequence:
        coord = coord + move_block * move.vector[direction]
        move_block = move_block * move.block[direction]
        yield (coord, move_block)
        

def get_coords(move_sequence, off_by_one = False):
    coord = np.matrix('0;0;0')
    #yield coord
    coord = coord + move.vector['f'] #the first move is "relative-free"
    move_block = move.block['f']
    if off_by_one:
        yield coord
    for direction in (move_sequence[:-1] if off_by_one else move_sequence):
        coord = coord + move_block * move.vector[direction]
        yield coord
        move_block = move_block * move.block[direction]
        




def score_config(coord_sequence, polar_sequence):
    tot = 0
    for left, right in itertools.combinations(         #compare each node with another
        filter(lambda x:x[1] == 'h',                #compare only hydrophobic nodes
            zip(                                    #make a tuple that represents: 
                #coordinate      #polarity      #index in sequence  
                coord_sequence, polar_sequence, range(len(polar_sequence))) 
            ), 2):
                
        if abs(left[-1] - right[-1]) <= 1: #these follow one-another in the sequence, thus should be ignored.
            continue 
        
        if abs(left[0] - right[0]).sum() == 1: #these are neighbours
            tot -= 1
    return tot

def is_non_intersecting(coord_sequence):
    for left, right in itertools.combinations(coord_sequence, 2):
        if (left == right).all():
            return False
    else:
        return True

def save_sequence(move_sequence, polar_sequence, filename):
    outdic = {'move_sequence' : move_sequence, 'polar_sequence': polar_sequence}
    with open("{}.json".format(filename)) as outfile:
        json.dump(outdic, outfile)

def add_legend(ax):
    '''add a legend below the figure, of the desired size'''
    legend_size = 0.05
    box = ax.get_position()
    
    #shrink axis to componsate legend below
    ax.set_position([box.x0, 
        box.y0 + box.height * legend_size,box.width, box.height * ( 1.0 - legend_size)])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.03))

def make_plot_2d(coord_sequence, polar_sequence, ax):
    xys = [[int(j[0,0]) for j in i] for i in zip(*coord_sequence)][:-1] 
    x, y = xys
    mins = [min(x), min(y)]
    maxs = [max(x), max(y)]
    for pos, axis in enumerate('xy'):
        getattr(ax, "set_{}bound".format(axis))(mins[pos], maxs[pos])
        getattr(ax, "set_{}ticks".format(axis))(list(range(mins[pos], maxs[pos] + 1)))
    
    coords_by_polarity = itertools.groupby(sorted(zip(x,y,polar_sequence), key = lambda x:x[-1]), key = lambda x:x[-1])
    
    ax.plot(x,y)
    for polarity, coords in coords_by_polarity:
        xs,ys,_ = zip(*coords) #turn the ((x1,y1), (x2,y2), ...) -> ((x1, x2, ...), (y1,y2, ...))
        ax.scatter(xs, ys, color = polarity_colors[polarity], label = polarity_full_name[polarity])
        
    #ax.scatter(*xys, c = [x == 'h' for x in polar_sequence] if polar_sequence else None, vmin = -1, vmax = 2, alpha = 1,label = ['hydrophobic' if x == 'h' else 'polar' for x in polar_sequence])
    for pos, xyz in enumerate(coord_sequence):
        ax.text(xyz[0,0],xyz[1,0], s = str(pos))
    if plot_with_legend:
        add_legend(ax)

def make_plot_3d(coord_sequence, polar_sequence, ax):
    xyzs = [[int(j[0,0]) for j in i] for i in zip(*coord_sequence)]
    x,y,z = xyzs
    mins = [min(x), min(y), min(z)]
    maxs = [max(x), max(y), max(z)]
    for pos, axis in enumerate('xyz'):
        getattr(ax, "set_{}bound".format(axis))(mins[pos], maxs[pos])
        getattr(ax, "set_{}ticks".format(axis))(list(range(mins[pos], maxs[pos] + 1)))
    ax.plot(*xyzs)
    coords_by_polarity = itertools.groupby(sorted(zip(x,y,z,polar_sequence), key = lambda x:x[-1]), key = lambda x:x[-1])
    for polarity, coords in coords_by_polarity:
        xs,ys,zs, _ = zip(*coords) #turn the ((x1,y1,z1), (x2,y2,z1), ...) -> ((x1, x2, ...), (y1,y2, ...), (z1, z2 ...))
        ax.scatter(xs, ys,zs, color = polarity_colors[polarity], label = polarity_full_name[polarity])
    #ax.scatter(*xyzs, c = [x == 'h' for x in polar_sequence] if polar_sequence else None, vmin = -1, vmax = 2, alpha = 1)
    for pos, xyz in enumerate(coord_sequence):
        ax.text(xyz[0,0],xyz[1,0],xyz[2,0], s = str(pos))
    if plot_with_legend:
        add_legend(ax)
def make_plot(coord_sequence, polar_sequence = None, name = None, show_plot = False, save_plot = True, dimensionality = 3):
    fig = plt.figure()
    plt.hold(True)
    coord_sequence = list(coord_sequence)
    if dimensionality == 3:
        ax = fig.gca(projection = '3d')
        make_plot_3d(coord_sequence,polar_sequence, ax)
    elif dimensionality == 2:
        ax = fig.gca()
        make_plot_2d(coord_sequence,polar_sequence, ax)
    else:
        raise NotImplementedError("dimensionality should be 3 or 4, supplied {}".format(dimensionality)) 
    
    if save_plot:
        plt.savefig(name)
    if show_plot:
        plt.show()
    fig.clf()
    ax.cla()
    plt.close(fig)
    #plt.show(block = False)



def plot_world_phero(world, gen = 0):
    product = lambda inlist: reduce(lambda x,y: x*y, inlist, 1)
    
    move_sequence = world.get_max_phero_path()
    likelihood = product(map(lambda pher: max(pher.values()),world))
    
    polar_sequence = world.sequence
    coords, blocks = zip(*get_coords_blocks(move_sequence))
    coords = list(coords)
    score = score_config(coords, polar_sequence)
    print("max pher seq: {}".format(move_sequence))
    print("log10 p(this_route): {}".format(math.log10(likelihood)))
    print("log10 p(this_route)/p(random_route):{}".format(math.log10(likelihood / (len(world.directions) ** (- len(coords))))))
    print("World Gen {} Score {} Valid {}".format(gen,score, is_non_intersecting(coords)))
    make_plot(coords, polar_sequence, name = "World Gen {} Score {} Valid {}".format(gen,score, is_non_intersecting(coords)))
    
    
def test_plot(move_sequence, polar_sequence, name = None, autocorrect = False, dimensionality = 3):
    #maybe replace this with instead saving the ants coords sequences, rather than guessing the correct one
    
    #coords, blocks = zip(*get_coords_blocks(move_sequence))
    #for l, r in zip(coords, blocks):
    #    print(l)
    #    print(r)
    #print(score_config(coords, polar_sequence))
    if autocorrect:
        coords_both = [list(get_coords(move_sequence, x)) for x in [False, True]]
        correct_coords = list(filter(is_non_intersecting, coords_both))
        if correct_coords:
            coords = correct_coords[0]
        else:
            coords = coords_both[0]
    else:
        coords = get_coords(move_sequence)
    make_plot(coords, polar_sequence, name = name, save_plot = False, show_plot = True, dimensionality = dimensionality)

def plot_history(mean_hist, name):
    x = list(range(len(mean_hist)))
    plt.plot(x, mean_hist)
    plt.savefig(name)
    plt.clf()
