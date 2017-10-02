#Ant Colony Optimazation Lattice Folding


#usage:
`<path/to/anaconda/python> swarmass.py [options]`
to interactively view results:
`<path/to/anaconda/python> view_sequence.py <path/to/ant/json>...`

for a summary of the options:
`<path/to/anaconda/python> swarmass.py --help`

#example
assuming you installed anaconda to ~/anaconda3

`~/anaconda3/bin/python3.5 swarmass.py --sequence "hpphpph" --target 2 --generations 5 --population 10 --output ./example`

to view a result
`~/anaconda3/bin/python3.5 view_sequence.py ./example/Ant_0_*.json`


#setup
install anaconda 4.2.0 (as python 3.5 is required, get it from
https://repo.continuum.io/archive/index.html)
assuming you installed anaconda to ~/anaconda3:
install pyQT4:
`~/anaconda3/bin/conda install pyqt=4`
then you can run run the swarmass:
~/anaconda3/bin/python3.5 swarmass.py 

