"""
In the first of two scripts, the input values are defined which are
used in the second script to create 3D myofibrils. They consist of
hexagonal unit cells forming sarcomeres in Abaqus. The second
script is automatically started at the end of the first script.
Both scripts need to be located in the same folder to ensure access
to the output data of the first code.
---
Install the following extending python-library to make sure, the code is
going to work properly. Required is: numpy (it can be freely downloaded
for the preferred python compiler).
"""

import numpy as np
import sys
import subprocess


#------------------------------------------------------------------------------------------------------------
#--- HIERARCHICAL LEVEL 2 - MYOFIBRIL -----------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------------
#------ START USER INPUT ------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------


#------ GENERAL INPUT ---------------------------------------------------------------------------------------

# (1) length of sarcomere
l_sarcomere = 2.5

# (2) number of aligned sarcomeres
number_sarcomeres = 10

# (3) radius of unit cell
r_unit_cell = 0.03

# (4) number of unit cells per sarcomere
number_unit_cells_per_sarcomere = 1000


#------ ADDITIONAL INPUT FOR MULTIPLE STRUCTURES ------------------------------------------------------------

"""
Multiple structures are generated by changing one input value. First, choose
the changing input value (enter 0 to change nothing, enter 1 to change the
sarcomere length, enter 2 to change the number of sarcomeres, enter 3 to
change the unit cell radius or enter 4 to change the number of unit cells
per sarcomere. After choosing the number of structures, a minimum and maximum
value for the changing input value needs to be defined. These values replace
the upper input value. By the desired number of structures, the values of the
varying parameter are automatically calculated for the structures and are
evenly distributed in the desired range.
"""

# choose the changing input value (enter 0 if none, otherwise enter 1, 2, 3 or 4)
vary = 0

# number of structures
number_structures = 1

# enter the minimum and maximum value for the changing input value
min_value = 2
max_value = 3


#------------------------------------------------------------------------------------------------------------
#------ END USER INPUT --------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------


#------ TEXT FILE -------------------------------------------------------------------------------------------

"""
Create a text file where the names of all text files for the input variables are
saved. This text file is used for the second script to create all structures.
"""

all_txt_input = "all_txt_input.txt"
open(all_txt_input, 'w').close()


#------ GENERATION OF THE STRUCTURES ------------------------------------------------------------------------

# sort input values and their labeling in lists
input_list = [0 , l_sarcomere, number_sarcomeres, r_unit_cell,
              number_unit_cells_per_sarcomere]
input_list_string = ['', '_length_sarcomere_', '_number_sarcomeres_', '_radius_unit_cell_',
             '_number_unit_cells_per_sarcomere_']

# check the type of the input values
if (type(vary) == str or type(number_structures) == str or type(min_value) == str or type(max_value) == str or
type(l_sarcomere) == str or type(number_sarcomeres) == str or type(r_unit_cell) == str or
type(number_unit_cells_per_sarcomere) == str):
    sys.exit('+ + + INPUT ERROR - NO STRINGS + + +')

# check the input for multiple structures and stop the programm if the input values are incorrect
if not 0<=vary<=4:
    sys.exit('+ + + INPUT ERROR - VARY + + +')
if number_structures <=0:
    sys.exit('+ + + INPUT ERROR - NUMBER OF STRUCTURES + + +')
if vary == 0:
    number_structures = 1
if number_structures == 1:
    vary = 0
if number_structures>1:
    input_list[vary] = min_value

# loop to create all structures
for var in np.linspace(input_list[vary], max_value, num=number_structures):

    if vary == 2 or vary == 4:
        input_list[vary] = round(var)
    else:
        input_list[vary] = round(var,4)

    # assign the input values for each structure
    l_sarcomere = input_list[1]
    number_sarcomeres = input_list[2]
    r_unit_cell = input_list[3]
    number_unit_cells_per_sarcomere = input_list[4]

    # check the input values and stop the programm if the input values are incorrect or do not fit together
    if l_sarcomere <= 0:
        sys.exit('+ + + INPUT ERROR - LENGTH OF SARCOMERE + + +')
    if number_sarcomeres <= 0:
        sys.exit('+ + + INPUT ERROR - NUMBER OF SARCOMERES + + +')
    if r_unit_cell <= 0:
        sys.exit('+ + + INPUT ERROR - RADIUS OF UNIT CELL + + +')
    if number_unit_cells_per_sarcomere <= 0:
        sys.exit('+ + + INPUT ERROR - NUMBER OF UNIT CELLS PER SARCOMERE + + +')

    # define name of txt-file for the input values for each structure
    filename = []
    if vary == 0:
        filename = "input_values_myofibril.txt"
    else:
        filename = "input_values_myofibril"+input_list_string[vary]+str(input_list[vary])+".txt"


    #------ WRITE TEXT FILES --------------------------------------------------------------------------------

    """
    Add the input values and text file names of the input values to the
    corresponding text files. These files are used in the second script.
    """

    with open(filename, "w") as i:
        i.write(str(l_sarcomere) + "\n")
        i.write(str(number_sarcomeres) + "\n")
        i.write(str(r_unit_cell) + "\n")
        i.write(str(number_unit_cells_per_sarcomere) + "\n")
    i.close()

    with open(all_txt_input, "a") as i:
        i.write(str(filename) + "\n")
    i.close


#------ START THE SECOND SCRIPT -----------------------------------------------------------------------------

"""
A batch-file is created which is used to start the second python script.
"""

bat = open('myofibril.bat','w+')
bat.write('''@echo off
          %start abaqus cae script=myofibril2.py
          ''')
bat.close()

subprocess.call(['myofibril.bat'])
