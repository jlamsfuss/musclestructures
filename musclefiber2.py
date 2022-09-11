"""
The output data from the first script is used in this code which is run
in Abaqus to create the muscle fibers.
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
#--- HIERARCHICAL LEVEL 3 - MUSCLE FIBER --------------------------------------------------------------------
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
    number_myofibrils = float(read_input_entry[0])
    r_muscle_fiber = float(read_input_entry[1])
    r_muscle_fiber_inner = float(read_input_entry[2])
    l_muscle_fiber = float(read_input_entry[3])
    thickness_sarcolemma = float(read_input_entry[4])
    input_entry.close()

    # read the polygon vertice-coordinates created by the first script
    v_x = []
    v_y = []
    coordinates_entry = open(coordinates_entries[i_structure],'r')
    read_coordinates_entry = coordinates_entry.readlines()
    coordinates_entry.close()


    #------ GEOMETRY NAME -----------------------------------------------------------------------------------

    # prepare a newly named model and delete the default model
    model = mdb.Model(name='musclefiber')
    assembly = model.rootAssembly
    if mdb.Model(name='Model-1'):
        del mdb.models['Model-1']


    #--------- MYOFIBRILS -----------------------------------------------------------------------------------

    """
    Myofibrils are generated by connecting the input coordinates polygon by
    polygon with lines. This is done by saving the x- and y-coordinates of the
    vertices of one polygon in separate lists and immediately creating this
    polygon. Afterwards, the same procedure is done with the next polygon etc.
    """

    sketch_myofibrils = model.ConstrainedSketch(name='sketch_myofibrils', sheetSize=r_muscle_fiber*2)

    a = 0
    count = 0
    # iterate over all vertice-coordinates
    for line in read_coordinates_entry:
        # the x- and y-vertice-coordinates are saved in separate lists
        if line != '\n':
            v_string = line.split(' ')
            v_x.append(round(float(v_string[0]),7))
            v_y.append(round(float(v_string[1]),7))

        # the myofibril polygons are created by connecting the vertices with lines
        else:
            count -= 1
            for i in range(a,count+1,1):
                if i < count:
                    sketch_myofibrils.Spline(points=((v_x[i], v_y[i]), (v_x[i+1], v_y[i+1])))
                else:
                    sketch_myofibrils.Spline(points=((v_x[count], v_y[count]), (v_x[a], v_y[a])))
            a = count+1
        count += 1

    myofibrils = model.Part(dimensionality=THREE_D, name='myofibrils', type=DEFORMABLE_BODY)
    myofibrils.BaseSolidExtrude(depth=l_muscle_fiber, sketch=sketch_myofibrils)
    assembly.Instance(name='myofibrils', part=myofibrils, dependent=ON)


    #--------- SARCOPLASMIC RETICULUM -----------------------------------------------------------------------

    """
    Sarcoplasmic reticulum is generated by using the myofibril sketch.
    """

    sketch_sarcoplasmic_reticulum = model.ConstrainedSketch(name='sketch_sarcoplasmic_reticulum', sheetSize=r_muscle_fiber*1.5)
    sketch_sarcoplasmic_reticulum.CircleByCenterPerimeter(center=(0, 0), point1=(r_muscle_fiber*2, 0))
    sketch_sarcoplasmic_reticulum.retrieveSketch(sketch=model.sketches['sketch_myofibrils'])

    sarcoplasmic_reticulum = model.Part(dimensionality=THREE_D, name='sarcoplasmic_reticulum', type=DEFORMABLE_BODY)
    sarcoplasmic_reticulum.BaseSolidExtrude(depth=l_muscle_fiber, sketch=sketch_sarcoplasmic_reticulum)
    assembly.Instance(name='sarcoplasmic_reticulum', part=sarcoplasmic_reticulum, dependent=ON)


    #------ CUT BOTH COMPONENTS TO MUSCLE FIBER RADIUS ------------------------------------------------------

    """
    Myofibril and sarcoplasmic reticulum are cut out to obtain the final circular
    shape and the outer sarcoplasmic reticulum edge is added to the muscle fiber.
    Here, an additional plane and an axis is needed to cut areas and add the outer
    sarcoplasmic reticulum edge.
    """

    for i in range(2):
        if i == 0:
            component = model.parts['myofibrils']
        else:
            component = model.parts['sarcoplasmic_reticulum']

        # create one xy-plane (d1[2]) and one axis (d1[5]) through two points (d1[3] and d1[4])
        d1 = component.datums
        component.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=l_muscle_fiber)
        component.DatumPointByCoordinate(coords=(0, 0, l_muscle_fiber))
        component.DatumPointByCoordinate(coords=(1, 1, l_muscle_fiber))
        component.DatumAxisByTwoPoint(point1=d1[3], point2=d1[4])

        # cut out myofibril and sarcoplasmic reticulum
        t = component.MakeSketchTransform(sketchPlane=d1[2], sketchUpEdge=d1[5],
            sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, l_muscle_fiber))
        sketch_cut = model.ConstrainedSketch(name='__profile__',
            sheetSize=r_muscle_fiber*2, gridSpacing=r_muscle_fiber/50, transform=t)
        sketch_cut.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_muscle_fiber_inner, 0.0))
        sketch_cut.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_muscle_fiber*2, 0.0))
        component.CutExtrude(sketchPlane=d1[2], sketchUpEdge=d1[5], sketchPlaneSide=SIDE1,
            sketchOrientation=RIGHT, sketch=sketch_cut, flipExtrudeDirection=OFF)

        if i == 1:
            # generate outer sarcoplasmic reticulum edge
            sketch_outer_sarcoplasmic_reticulum = model.ConstrainedSketch(name='__profile__',
                sheetSize=r_muscle_fiber*2, gridSpacing=r_muscle_fiber/50, transform=t)
            sketch_outer_sarcoplasmic_reticulum.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_muscle_fiber_inner, 0.0))
            sketch_outer_sarcoplasmic_reticulum.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_muscle_fiber, 0.0))
            component.SolidExtrude(sketchPlane=d1[2], sketchUpEdge=d1[5], sketchPlaneSide=SIDE1,
                sketchOrientation=RIGHT, sketch=sketch_outer_sarcoplasmic_reticulum, depth=l_muscle_fiber, flipExtrudeDirection=ON)


    #--------- SARCOLEMMA -----------------------------------------------------------------------------------

    """
    Sarcolemma is placed as a thin hollow cylinder on the outer sarcoplasmic reticulum edge.
    """

    sketch_sarcolemma = model.ConstrainedSketch(name='sketch_sarcolemma', sheetSize=r_muscle_fiber*2)
    sketch_sarcolemma.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_muscle_fiber, 0.0))
    sketch_sarcolemma.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_muscle_fiber+thickness_sarcolemma, 0.0))

    sarcolemma = model.Part(name='sarcolemma', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    sarcolemma.BaseSolidExtrude(sketch=sketch_sarcolemma, depth=l_muscle_fiber)
    assembly.Instance(name='sarcolemma', part=sarcolemma, dependent=ON)


    #--------- MERGE TO ONE INSTANCE ------------------------------------------------------------------------

    # merge the different instances of the muscle fiber to one instance
    all_instances = assembly.instances.keys()
    assembly.InstanceFromBooleanMerge(name='musclefiber', instances=([assembly.instances[all_instances[i]]
        for i in range(len(assembly.instances))] ), keepIntersections=ON, originalInstances=SUPPRESS, domain=GEOMETRY)
    assembly.features.changeKey(fromName='musclefiber-1', toName='musclefiber')


    #--------- SAVE MODEL AS CAE-FILE -----------------------------------------------------------------------

    file_ending=input_entries[i_structure].replace('input_values_musclefiber','')
    file_ending=file_ending.replace('.txt','')

    file='musclefiber'+str(file_ending)
    mdb.saveAs(str(file)+'.cae')
