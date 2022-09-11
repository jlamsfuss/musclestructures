"""
In the first of two scripts, the input values are defined which are
used in the second script to create 3D sarcomeres consisting of one
unit cell in Abaqus. Sarcomeres with a circular or hexagonal
cross-section can be generated. A sarcomere with a circular cross-section
represents a unit cell with whole actin filaments and is useful if only
level 1 is modeled. For multiscale modeling purposes, a hexagonal
cross-section should be used. The second script is automatically started
at the end of the first script.
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
#--- HIERARCHICAL LEVEL 1 - SARCOMERE -----------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------------
#------ START USER INPUT ------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------


#------ INPUT -----------------------------------------------------------------------------------------------

# choose a hexagonal or circular cross-section for the entire unit cell:
# enter 'hex' for hexagonal or 'cir' for circular
cross_section='cir'

# (1) radius of myosin
r_myosin = 0.006

# (2) length of myosin
l_myosin = 1.6

# (3) radius of actin
r_actin = 0.003

# (4) length of actin
l_actin = 1.0

# (5) thickness of z-disc
thickness_z_disc = 0.05

# (6) length of sarcomere (thickness of z-disc is included)
l_sarcomere = 2.5

# (7) length of crossbridge
l_crossbridge = 0.02

# (8) number of crossbridges
number_crossbridges = 600


#------ ADDITIONAL INPUT FOR MULTIPLE STRUCTURES ------------------------------------------------------------

"""
Multiple structures are generated by changing one input value. First, choose
the changing input value (enter 0 to change nothing, enter 1 to change
the myosin radius, enter 2 to change the myosin length, enter 3 to change the
actin radius, enter 4 to change the actin length, enter 5 to change the
thickness of z-disc, enter 6 to change the sarcomere length, enter 7 to
change the crossbridge length or enter 8 to change the number of crossbridges.
After choosing the number of structures, a minimum and maximum value for the
changing input value needs to be defined. These values replace the upper input
value. By the desired number of structures, the values of the varying parameter
are automatically calculated for the structures and are evenly distributed in
the desired range.
"""

# choose the changing input value (enter 0 if none, otherwise enter 1, 2, 3, 4, 5, 6, 7 or 8)
vary = 0

# number of structures
number_structures = 1

# enter the minimum and maximum value for the changing input value
min_value = 0.005
max_value = 0.007


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
input_list = [0 , r_myosin, l_myosin, r_actin, l_actin, thickness_z_disc, l_sarcomere, l_crossbridge,
              number_crossbridges]
input_list_string = ['', '_radius_myosin_', '_length_myosin_', '_radius_actin_', '_length_actin_',
                     '_thickness_z_disc_', '_length_sarcomere_', '_length_crossbridge_',
                     '_number_crossbridges_']

# check the type of the input values
if (type(vary) == str or type(number_structures) == str or type(min_value) == str or type(max_value) == str or
type(r_myosin) == str or type(l_myosin) == str or type(r_actin) == str or type(l_actin) == str or
type(thickness_z_disc) == str or type(l_sarcomere) == str or type(l_crossbridge) == str or
type(number_crossbridges) == str):
    sys.exit('+ + + INPUT ERROR - INTEGER OR FLOAT REQUIRED EXCEPT FOR CROSS-SECTION + + +')

if type(cross_section) != str:
    sys.exit('+ + + INPUT ERROR - STRING REQUIRED FOR CROSS-SECTION + + +')

# check the input for multiple structures and stop the programm if the input values are incorrect
if not 0<=vary<=8:
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

    if vary == 8:
        input_list[vary] = int(var)
    else:
        input_list[vary] = round(var,4)

    # assign the input values for each structure
    r_myosin = input_list[1]
    l_myosin = input_list[2]
    r_actin = input_list[3]
    l_actin = input_list[4]
    thickness_z_disc = input_list[5]
    l_sarcomere = input_list[6]
    l_crossbridge = input_list[7]
    number_crossbridges = input_list[8]

    # check the input values and stop the programm if the input values are incorrect or do not fit together
    if r_myosin <= 0:
        sys.exit('+ + + INPUT ERROR - RADIUS OF MYOSIN + + +')
    if l_myosin <= 0:
        sys.exit('+ + + INPUT ERROR - LENGTH OF MYOSIN + + +')
    if r_actin <= 0:
        sys.exit('+ + + INPUT ERROR - RADIUS OF ACTIN + + +')
    if l_actin <= 0:
        sys.exit('+ + + INPUT ERROR - LENGTH OF ACTIN + + +')
    if thickness_z_disc <= 0:
        sys.exit('+ + + INPUT ERROR - THICKNESS OF Z-DISC + + +')
    if l_sarcomere <= 0:
        sys.exit('+ + + INPUT ERROR - LENGTH OF SARCOMERE + + +')
    if l_crossbridge <= 0:
        sys.exit('+ + + INPUT ERROR - LENGTH OF CROSSBRIDGE + + +')
    if number_crossbridges <= 3:
        sys.exit('+ + + INPUT ERROR - NUMBER OF CROSSBRIDGES + + +')

    if cross_section != 'hex' and cross_section != 'cir':
        sys.exit('+ + + INPUT ERROR - CROSS-SECTION + + +')
    if cross_section == 'hex':
        if l_actin*2+thickness_z_disc >= l_sarcomere:
            sys.exit('+ + + INPUT ERROR - LENGTH OF ACTIN IS TOO LONG + + +')
        if l_myosin+thickness_z_disc >= l_sarcomere:
            sys.exit('+ + + INPUT ERROR - LENGTH OF MYOSIN IS TOO LONG + + +')
        if l_myosin+l_actin*2+thickness_z_disc <= l_sarcomere:
            sys.exit('+ + + INPUT ERROR - LENGTH OF MYOSIN AND ACTIN IS TOO SHORT + + +')
    else:
        if l_actin*2+thickness_z_disc*2 >= l_sarcomere:
            sys.exit('+ + + INPUT ERROR - LENGTH OF ACTIN IS TOO LONG + + +')
        if l_myosin+thickness_z_disc*2 >= l_sarcomere:
            sys.exit('+ + + INPUT ERROR - LENGTH OF MYOSIN IS TOO LONG + + +')
        if l_myosin+l_actin*2+thickness_z_disc*2 <= l_sarcomere:
            sys.exit('+ + + INPUT ERROR - LENGTH OF MYOSIN AND ACTIN IS TOO SHORT + + +')


    # define name of txt-file for the input values for each structure
    filename = []
    if vary == 0:
        filename = "input_values_sarcomere.txt"
    else:
        filename = "input_values_sarcomere"+input_list_string[vary]+str(input_list[vary])+".txt"


    #------ WRITE TEXT FILES --------------------------------------------------------------------------------

    """
    Add the input values and text file names of the input values to the
    corresponding text files. These files are used in the second script.
    """

    with open(filename, "w") as i:
        i.write(str(cross_section) + "\n")
        i.write(str(r_myosin) + "\n")
        i.write(str(l_myosin) + "\n")
        i.write(str(r_actin) + "\n")
        i.write(str(l_actin) + "\n")
        i.write(str(thickness_z_disc) + "\n")
        i.write(str(l_sarcomere) + "\n")
        i.write(str(l_crossbridge) + "\n")
        i.write(str(number_crossbridges) + "\n")
    i.close()

    with open(all_txt_input, "a") as i:
        i.write(str(filename) + "\n")
    i.close


#------ START THE SECOND SCRIPT -----------------------------------------------------------------------------

"""
A batch-file is created which is used to start the second python script.
"""

bat = open('sarcomere.bat','w+')
bat.write('''@echo off
          %start abaqus cae script=sarcomere2.py
          ''')
bat.close()

subprocess.call(['sarcomere.bat'])
