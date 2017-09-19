#objective function as in shmygelska 2005 

import matplotlib
matplotlib.use('Qt4Agg') #
import matplotlib.pyplot as plt
import time
import math
from functools import reduce
import move
import numpy as np
import itertools

save_plots = False


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
		

def get_coords(move_sequence):
	coord = np.matrix('0;0;0')
	#yield coord
	coord = coord + move.vector['f'] #the first move is "relative-free"
	move_block = move.block['f']
	#yield coord 
	for direction in move_sequence:
		coord = coord + move_block * move.vector[direction]
		yield coord
		move_block = move_block * move.block[direction]
		




def score_config(coord_sequence, polar_sequence):
	tot = 0
	for left, right in itertools.combinations( 		#compare each node with another
		filter(lambda x:x[1] == 'h',				#compare only hydrophobic nodes
			zip(									#make a tuple that represents: 
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



def make_plot(coord_sequence, polar_sequence = None, name = None):
	if not save_plots:
		return
	fig = plt.figure()
	ax = fig.gca(projection = '3d')
	plt.hold(True)
	coord_sequence = list(coord_sequence)
	#xyzs = np.matrix(coord_sequence)
	xyzs = [[int(j[0,0]) for j in i] for i in zip(*coord_sequence)]
	x,y,z = xyzs
	mins = [min(x), min(y), min(z)]
	maxs = [max(x), max(y), max(z)]
	for pos, axis in enumerate('xyz'):
		getattr(ax, "set_{}bound".format(axis))(mins[pos], maxs[pos])
		getattr(ax, "set_{}ticks".format(axis))(list(range(mins[pos], maxs[pos] + 1)))
	#ax.plot(coord_sequence)
	ax.plot(*xyzs)
	ax.scatter(*xyzs, c = [x == 'h' for x in polar_sequence] if polar_sequence else None, vmin = -1, vmax = 2, alpha = 1)
	#ax.text(xyzs[0], xyzs[1],xyzs[2],[str(x) for x in range(len(xyzs[0]))]) #[,#[str(x) for x in range(len(xyz[0]))])	
	for pos, xyz in enumerate(coord_sequence):
		ax.text(xyz[0,0],xyz[1,0],xyz[2,0], s = str(pos))
		#ax.text(*xyz, s = str(pos))
	if save_plots:
		plt.savefig("paths/{}".format(name or int(time.time())))
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
	
	
def test_plot(move_sequence, polar_sequence, name = None):
	coords, blocks = zip(*get_coords_blocks(move_sequence))
	#for l, r in zip(coords, blocks):
	#	print(l)
	#	print(r)
	#print(score_config(coords, polar_sequence))
	make_plot(get_coords(move_sequence), polar_sequence, name = name)

def plot_history(mean_hist):
	x = list(range(len(mean_hist)))
	plt.plot(x, mean_hist)
	plt.savefig("paths/{}".format(int(time.time())))