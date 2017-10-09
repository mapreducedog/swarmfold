'''

'''

#builtin
import sys
import json
import os
import glob

#external
import numpy as np
#own
import check_score

def view_sequence(filename):
    print(filename)
    with open(filename, 'r') as infile:
        seqdic = json.load(infile)
    coord_sequence = [np.matrix(xyz) for xyz in seqdic['coord_sequence']]
    check_score.make_plot(coord_sequence, seqdic['polar_sequence'], show_plot = True,save_plot = False, dimensionality=seqdic['dimensionality'])
    
    
def view_sequence_from_folder(foldername):
    files = glob.glob(os.path.join(foldername, "*.json"))
    files.sort(key = os.path.getctime)
    print(files)
    for filename in files:
        view_sequence(filename)

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[-1] in {'-h', '--help'}:
        print(
        '''usage: python view_sequence.py <sequence_file>...
    python view_sequence.py <folder/with/sequence/files>...
    ''')
    else:
        for filename in sys.argv[1:]:
            if os.path.isdir(filename):
                view_sequence_from_folder(filename)
            else:
               view_sequence(filename)
