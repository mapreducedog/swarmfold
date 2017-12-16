import sys
import os

'''need to import user_interface here,
so that it can inspect the World properties of swarmass'''
import user_interface as __user_interface
import swarmass

def filename_without_ext(filename):
    return os.path.splitext(os.path.basename(filename))[0]

def test_file(filename, dimensionality = 2):
    experimental_pop_size = 100
    experimental_nr_generations = 100
    
    user_interface = swarmass.user_interface
    with open(filename) as infile:
        seq_score_tups = \
            map(lambda seq_score : (seq_score[0].strip(), abs(int(seq_score[1]))),
                map(lambda line: line.strip().split(","), 
                infile.readlines()))
    user_interface.current_options[user_interface.set_dimensionality.pos] = dimensionality
    user_interface.current_options[user_interface.set_pop_size.pos] = experimental_pop_size
    user_interface.current_options[user_interface.set_number_generations.pos] = experimental_nr_generations
    parent_path = os.path.join(".", "test_{}".format(filename_without_ext(filename)))
    cnt = 0;
    for seq,score in seq_score_tups:
        cnt += 1
        user_interface.current_options[user_interface.set_output_directory.pos] = os.path.join(parent_path, "seq_{}".format(cnt))
        user_interface.current_options[user_interface.set_polarity_string.pos] = seq
        user_interface.current_options[user_interface.set_target_score.pos] = score
        swarmass.apply_options()
        swarmass.test_single(*user_interface.current_options[user_interface.set_pop_size.pos:user_interface.set_target_score.pos + 1])
        



if __name__ == '__main__':
    for filename in sys.argv[1:]:
        test_file(filename, 3 if '3d' in filename.lower() else 2)
