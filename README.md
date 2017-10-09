# Ant Colony Optimazation Lattice Folding


# Usage:

`<path/to/anaconda/python> swarmass.py [options]`  
  
to interactively view results:  
`<path/to/anaconda/python> view_sequence.py <path/to/ant/json>...`

for a summary of the options:  
`<path/to/anaconda/python> swarmass.py --help`

# Examples:
assuming you installed anaconda to ~/anaconda3

`~/anaconda3/bin/python3.5 swarmass.py --sequence "hpphpph" --target 2 --generations 5 --population 10 --output ./example`

to view a result  
`~/anaconda3/bin/python3.5 view_sequence.py ./example/Ant_0_*.json`


# Setup:
1. install anaconda 4.2.0  
    (as python 3.5 is required, get it from
   https://repo.continuum.io/archive/index.html)
2. Install PyQT4 (assuming you installed anaconda to ~/anaconda3):  
   `~/anaconda3/bin/conda install pyqt=4`
3. Finished, try  it with:  
   `~/anaconda3/bin/python3.5 swarmass.py `

# Tips & Tricks
assuming you have a gnu/linux distribution (this probably works on macOS and other unix-likes as well)
if you want to view the ant paths in chronological order you run the following  
`<path/to/anaconda/python> view_sequence.py $(ls -rt <folder/with/ant/paths>*.json)`  
for example:  
`~/anaconda3/bin/python3.5 view_sequence.py $(ls -rt ./example/*.json)`
