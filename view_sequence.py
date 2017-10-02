#builtin
import sys
import json

#external
import numpy as np
#own
import check_score

def view_sequence(filename):
    with open(filename, 'r') as infile:
        seqdic = json.load(infile)
    coord_sequence = [np.matrix(xyz) for xyz in seqdic['coord_sequence']]
    check_score.make_plot(coord_sequence, seqdic['polar_sequence'], show_plot = True,save_plot = False, dimensionality=seqdic['dimensionality'])
    
    


if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[-1] in {'-h', '--help'}:
        print("usage: python view_sequence <sequence_file(s)>")
    else:
        for filename in sys.argv[1:]:
            view_sequence(filename)
