"""
The output data from the first script is used in this code which is run
in Abaqus to create the fascicles.
Both scripts need to be located in the same folder. Use this folder as
the work directory in Abaqus.
"""

from abaqus import *
from abaqusConstants import *
import __main__

import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior


#------------------------------------------------------------------------------------------------------------
#--- HIERARCHICAL LEVEL 4 - FASCICLE ------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------


#------ OUTPUT OF FIRST SCRIPT ------------------------------------------------------------------------------

"""
From the first script, read the output data of the two text files where the names
of all text files for (1) the input variables and (2) the vertice coordinates
are saved.
"""

all_txt_input="all_txt_input.txt"
all_txt_coordinates="all_txt_coordinates.txt"

txt_input = open(all_txt_input,'r')
txt_coordinates = open(all_txt_coordinates,'r')

input_entries = txt_input.read().splitlines()
coordinates_entries = txt_coordinates.read().splitlines()

txt_input.close
txt_coordinates.close


#------ GENERATION OF THE STRUCTURES ------------------------------------------------------------------------

# loop to create all structures
for i_structure in range(len(input_entries)):

    # read the input values from each structure of the first script
    input_entry = open(input_entries[i_structure],'r')
    read_input_entry = input_entry.readlines()
    number_muscle_fibers = float(read_input_entry[0])
    r_fascicle = float(read_input_entry[1])
    r_fascicle_inner = float(read_input_entry[2])
    l_fascicle = float(read_input_entry[3])
    input_entry.close()

    # read the polygon vertice-coordinates created by the first script
    v_x = []
    v_y = []
    coordinates_entry = open(coordinates_entries[i_structure],'r')
    read_coordinates_entry = coordinates_entry.readlines()
    coordinates_entry.close()


    #------ GEOMETRY NAME -----------------------------------------------------------------------------------

    # prepare a newly named model and delete the default model
    model = mdb.Model(name='fascicle')
    assembly = model.rootAssembly
    if mdb.Model(name='Model-1'):
        del mdb.models['Model-1']


    #--------- MUSCLE FIBERS --------------------------------------------------------------------------------

    """
    Muscle fibers are generated by connecting the input coordinates polygon by
    polygon with lines. This is done by saving the x- and y-coordinates of the
    vertices of one polygon in separate lists and immediately creating this
    polygon. Afterwards, the same procedure is done with the next polygon etc.
    """

    sketch_muscle_fibers = model.ConstrainedSketch(name='sketch_muscle_fibers', sheetSize=r_fascicle*2)

    a = 0
    count = 0
    # iterate over all vertice-coordinates
    for line in read_coordinates_entry:
        # the x- and y-vertice-coordinates are saved in separate lists
        if line != '\n':
            v_string = line.split(' ')
            v_x.append(round(float(v_string[0]),7))
            v_y.append(round(float(v_string[1]),7))

        # the muscle fiber polygons are created by connecting the vertices with lines
        else:
            count -= 1
            for i in range(a,count+1,1):
                if i < count:
                    sketch_muscle_fibers.Spline(points=((v_x[i], v_y[i]), (v_x[i+1], v_y[i+1])))
                else:
                    sketch_muscle_fibers.Spline(points=((v_x[count], v_y[count]), (v_x[a], v_y[a])))
            a = count+1
        count += 1

    muscle_fibers = model.Part(dimensionality=THREE_D, name='muscle_fibers', type=DEFORMABLE_BODY)
    muscle_fibers.BaseSolidExtrude(depth=l_fascicle, sketch=sketch_muscle_fibers)
    assembly.Instance(name='muscle_fibers', part=muscle_fibers, dependent=ON)


    #--------- ENDOMYSIUM -----------------------------------------------------------------------------------

    """
    Endomysium is generated by using the muscle fiber sketch.
    """

    sketch_endomysium = model.ConstrainedSketch(name='sketch_endomysium', sheetSize=r_fascicle*1.5)
    sketch_endomysium.CircleByCenterPerimeter(center=(0, 0), point1=(r_fascicle*2, 0))
    sketch_endomysium.retrieveSketch(sketch=model.sketches['sketch_muscle_fibers'])

    endomysium = model.Part(dimensionality=THREE_D, name='endomysium', type=DEFORMABLE_BODY)
    endomysium.BaseSolidExtrude(depth=l_fascicle, sketch=sketch_endomysium)
    assembly.Instance(name='endomysium', part=endomysium, dependent=ON)


     #------ CUT BOTH COMPONENTS TO FASCICLE RADIUS ---------------------------------------------------------

    """
    Muscle fiber and endomysium are cut out to obtain the final circular shape and
    the outer endomysium edge is added to the fascicle. Here, an additional plane
    and an axis is needed to cut areas and add the outer endomysium edge.
    """

    for i in range(2):
        if i == 0:
            component = model.parts['muscle_fibers']
        else:
            component = model.parts['endomysium']

        # create one xy-plane (d1[2]) and one axis (d1[5]) through two points (d1[3] and d1[4])
        d1 = component.datums
        component.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=l_fascicle)
        component.DatumPointByCoordinate(coords=(0, 0, l_fascicle))
        component.DatumPointByCoordinate(coords=(1, 1, l_fascicle))
        component.DatumAxisByTwoPoint(point1=d1[3], point2=d1[4])

        # cut out muscle fiber and endomysium
        t = component.MakeSketchTransform(sketchPlane=d1[2], sketchUpEdge=d1[5],
            sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, l_fascicle))
        sketch_cut = model.ConstrainedSketch(name='__profile__',
            sheetSize=r_fascicle*2, gridSpacing=r_fascicle/50, transform=t)
        sketch_cut.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_fascicle_inner, 0.0))
        sketch_cut.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_fascicle*2, 0.0))
        component.CutExtrude(sketchPlane=d1[2], sketchUpEdge=d1[5], sketchPlaneSide=SIDE1,
            sketchOrientation=RIGHT, sketch=sketch_cut, flipExtrudeDirection=OFF)

        if i == 1:
            # generate outer endomysium edge
            sketch_outer_endomysium = model.ConstrainedSketch(name='__profile__',
                sheetSize=r_fascicle*2, gridSpacing=r_fascicle/50, transform=t)
            sketch_outer_endomysium.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_fascicle_inner, 0.0))
            sketch_outer_endomysium.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_fascicle, 0.0))
            component.SolidExtrude(sketchPlane=d1[2], sketchUpEdge=d1[5], sketchPlaneSide=SIDE1,
                sketchOrientation=RIGHT, sketch=sketch_outer_endomysium, depth=l_fascicle, flipExtrudeDirection=ON)


    #--------- MERGE TO ONE INSTANCE ------------------------------------------------------------------------

    # merge the different instances of the fascicle to one instance
    all_instances = assembly.instances.keys()
    assembly.InstanceFromBooleanMerge(name='fascicle', instances=([assembly.instances[all_instances[i]]
        for i in range(len(assembly.instances))] ), keepIntersections=ON, originalInstances=SUPPRESS, domain=GEOMETRY)
    assembly.features.changeKey(fromName='fascicle-1', toName='fascicle')


    #--------- SAVE MODEL AS CAE-FILE -----------------------------------------------------------------------

    file_ending=input_entries[i_structure].replace('input_values_fascicle','')
    file_ending=file_ending.replace('.txt','')

    file='fascicle'+str(file_ending)
    mdb.saveAs(str(file)+'.cae')
