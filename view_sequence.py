#builtin
import sys
import json

#own
import check_score

def view_sequence(filename):
    with open(filename, 'r') as infile:
        seqdic = json.load(infile)
    check_score.test_plot(seqdic['move_sequence'],seqdic['polar_sequence'])
    
    


if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[-1] in {'-h', '--help'}:
        print("usage: python view_sequence <sequence_file(s)>")
    else:
        
        for filename in sys.argv[1:]:
            view_sequence(filename)
