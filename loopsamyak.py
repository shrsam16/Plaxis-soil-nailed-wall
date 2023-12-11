from tkinter import *
from plxscripting.easy import *
import subprocess,time
import math
#Creating excelfile
import os
from openpyxl.workbook import Workbook
from openpyxl import load_workbook
import re

import pandas as pd
import openpyxl

def startPlaxis():
    PLAXIS_PATH=r"C:\Program Files\Bentley\Geotechnical\PLAXIS 2D CONNECT Edition V21\Plaxis2DXInput.exe"
    Port_i=10000
    Port_o=10001
    PASSWORD='1234'

    subprocess.Popen([PLAXIS_PATH,f'--AppServerPassword={PASSWORD}',f'--AppServerPort={Port_i}'],shell=False)

    global g_i, g_o, s_i, s_o
    s_i,g_i=new_server('localhost',Port_i,password=PASSWORD)
    s_o,g_o=new_server('localhost',Port_o,password=PASSWORD)


def readtxt(Model_id):
    with open('model.txt', 'r') as file:
        for i, line in enumerate(file):
            if i == Model_id:
                parameters = line.strip().split('\t')
                break
        parameterKeys = ['S.N.','E','Gam','phi','C','Neu','dil','ExDep','Bfill','Plthk','FAng','Inc','Sp','Len']
        res = {parameterKeys[i]: float(parameters[i]) for i in range(len(parameterKeys))}

    return res

def run_code(start, end):
    for Model_id in range(start, end+1):
        s_i.new()


        # # Initail Data
        parameters = readtxt(Model_id)
        DepthOfExcavation = float(parameters['ExDep'])
        XExtent = 15*DepthOfExcavation
        YExtent = 4*DepthOfExcavation
        WidthOfExcavation = 6*DepthOfExcavation
        g_i.SoilContour.initializerectangular(0,0,XExtent, YExtent)



        # # creating boreholes and creating soillayers

        class soil_layers:
            def __init__(self,soillayer_depth):
                self.soillayer_depth=soillayer_depth
        class Borehole:
            def __init__(self,borehole_no,x_coordinate=None,soillayer=None):
                self.borehole_no=borehole_no
                self.x_coordinate=x_coordinate
                self.soillayer= [] if soillayer is None else soillayer

        no_of_boreholes = 1
        boreholes = []#Bore hole list is created to store borehole objects
        previous_soillayer_no = 0
        x=0
        a=[]
        for i in range(no_of_boreholes):
            borehole_no = i+1

            x_coordinate = 0
            borehole = Borehole(borehole_no,x_coordinate)#new obj named borehole is created
            boreholes.append(borehole)#the new borehole object is appended to the above defined list
            borehole_g = g_i.borehole(boreholes[i].x_coordinate) #Bore hole is created extracting x coordinate from obj list
            
            print(borehole_g)
            sum=0

            soillayer_no = 1
            for j in range(soillayer_no):
   
                soillayer_depth = YExtent
                soillayer=soil_layers(soillayer_depth)
                boreholes[i].soillayer.append(soillayer)
                sum+=boreholes[i].soillayer[j].soillayer_depth
                if i==0:
                    boreholepolygon_g = g_i.soillayer(boreholes[i].soillayer[j].soillayer_depth)
                    print(boreholepolygon_g)

                if i!=0 and j>previous_soillayer_no-1:
                    boreholepolygon_g = g_i.soillayer(boreholes[i].soillayer[j].soillayer_depth)
                    print(boreholepolygon_g)
                g_i.setsoillayerlevel(borehole_g, j+1, -sum)
                
                if i!=0 and j>previous_soillayer_no-1:
                 g_i.setsoillayerlevel(a[i-1], j+1, 0)
                
                x=sum
                
            if soillayer_no < previous_soillayer_no:
                g_i.setsoillayerlevel(borehole_g, soillayer_no+1, 0)
            g_i.set(borehole_g.Head,-YExtent)
            previous_soillayer_no=soillayer_no
            a.append(borehole_g)
            # For Backfill
        import math   
              
        slope = float(parameters['FAng']) # angle with vertical
        x2,y2 = WidthOfExcavation, -DepthOfExcavation
        y1 = 0

        def xVal(y1,y2, slope):
            x1 = x2 + (y1-y2)/math.tan((90-slope)*math.pi/180) #y1=tan30 * x1+c #20 = tan 30 *10 +c=> c = 20-10*tan30=>x1 = (y1-(10*tan30-20))/tan30 => x1 = 10-20/tan(30)
            return x1
        
        x1 = xVal(y1,y2, slope)

        lineload_X_start = x1+1*math.cos(math.radians(parameters['Bfill']))
        lineload_Y_start = y1+1*math.sin(math.radians(parameters['Bfill']))
        lineload_X_finish = x1+11*math.cos(math.radians(parameters['Bfill']))
        lineload_Y_finish = y1+11*math.sin(math.radians(parameters['Bfill']))
        borehole_g = g_i.borehole(x1)
        g_i.setsoillayerlevel(borehole_g, 0, 0)

        borehole_g = g_i.borehole(XExtent)
        import math
        x=math.tan(math.radians(float(parameters['Bfill'])))
        HeightOfBackFill=x*(XExtent-x1)
        g_i.setsoillayerlevel(borehole_g, 0, HeightOfBackFill)


        # # Creating and assigning soil_Materials
        # defining the polygon for meshing purpose
        a=12*DepthOfExcavation
        b=-2*DepthOfExcavation
        HeightOfBackFill1=x*(a-x1)

        g_i.polygon((0,0), (x1, 0), (a,HeightOfBackFill1), (a, b), (0,b))
        point1_g, point2_g = g_i.point((0, b), (a, b))
            
        g_i.cutpoly(point1_g, point2_g)

        no_of_soilmaterial = 1
        for i in range (no_of_soilmaterial) :
            MySoil = g_i.soilmat()
            #mat_name=input('Enter material Name: ')
            mat_name = 'Mat_1'
            MySoil.setproperties("MaterialName", mat_name,'cref',float(parameters['C']), "SoilModel", 2, "gammaUnsat", float(parameters['Gam']),"gammaSat", float(parameters['Gam']),"nu", float(parameters['Neu']),"phi", float(parameters['phi']),"Eref",float(parameters['E']))
            g_i.Soillayers[i].Soil.Material = MySoil

        # # Creating Plate and Embedded Beam materials

        #Plate material
        EPlate = 30_000_000 # to 50_000_000 kN/m^2#esko value kati hunxa?
        EA= (EPlate-parameters['E']) * parameters['Plthk'] / 1000
        EI= (EPlate-parameters['E']) * ((parameters['Plthk']/1000) ** 3) /12
        d = math.sqrt(12*EI/EA)
        nu= 0.25 #neu value for RCC plate material -> different for different grades of concrete? #esko value kati hunxa?
        Gref= (EA/d)/(2*(1+nu))
        plat_mat=g_i.platemat('MaterialName','Facing_1','nu',0.25,'w',6,'IsIsotropic',True,'EA',EA,'EA2',EA,'EI',EI,'d',d,'Gref',Gref)

        # # Defining plate and Nail

        line_g  = g_i.line((x1,y1), (x2,y2))[-1]

        plate_g = g_i.plate(line_g)
        plate_g.setmaterial(plat_mat)


        #Nails
        #finding coordinates of position of head of soil nails
        step1 = parameters['Sp'] #m
        FirstNailDepth = 0.5
        yn = [-1*FirstNailDepth]
        i = yn[0]  #placement of first embedded row y coordinate

        while i-step1 > y2 :
            i = i-step1
            yn.append(i)
                       
        xn = []
        for i in yn:
            xn.append(xVal(i, y2, slope))
            

        #Soil nail embedded beam row
        ENail = 200_000_000
        TensionPullOut = 15#esko value kati hunxa?
        emrow=g_i.embeddedbeammat('MaterialName','SoilNail1','Elasticity',0,'Lspacing',parameters['Sp'],'E',ENail-parameters['E'],'w',78.5 - parameters['Gam'],'Tstart',TensionPullOut,'Tend',TensionPullOut)
        emrow.setproperties('Diameter',0.032)

        #creating nail array
        nailLength = parameters['Len'] * DepthOfExcavation
        nailSlope = parameters['Inc'] * math.pi/180 # with horizontal
        lines_g = []
        EmbeddedBeamRows_g = []
        for i in range (int(abs(int(y2-yn[0]))/step1)+1):
            lines_g.append(g_i.line((xn[i],yn[i]),(xn[i]+nailLength*math.cos(nailSlope)),(yn[i]-nailLength*math.sin(nailSlope)))[-1])
            EmbeddedBeamRows_g.append(g_i.embeddedbeamrow(lines_g[i]))
            #not plates, nails
            #when nail material is made change this
            #for i in range(10):
            g_i.setmaterial(g_i.EmbeddedBeamRows[i],emrow) #model explorer shown list can be accessed this way

        ### create line for excavation
        #excavation line creation
 
        d = 1.5 #excavation depth at a time
        H = parameters['ExDep']

        step=math.ceil(H/d)
        #wb.active=wb['Facing and Soil nail']
        #ws=wb.active

        x1,y1 = WidthOfExcavation, -DepthOfExcavation

        m=math.tan(math.radians(90-slope))

        for i in range(step):
            if i+1<step:
                y2=-(i+1)*d  #d=depth of excavation at a time
                x2=x1+(y2-y1)/m
                g_i.line((0,y2),(x2,y2))
            else:
                y2= -DepthOfExcavation #bottom y coordinate
                x2=(x1+(y2-y1)/m)
                g_i.line((0,y2),(x2,y2))

           
        #lineload
        g_i.lineload((lineload_X_start,lineload_Y_start),(lineload_X_finish,lineload_Y_finish),'qy_start',-8)

        # Creating mesh

        #meshing

        g_i.gotomesh()
        #refining the mesh
        refineControl = 1
        for j in range (refineControl):
            for i in range(step+1):
            
                polygon_s = g_i.Polygons[i]
                g_i.refine(polygon_s)
        g_i.mesh(0.1)

        m=math.tan(math.radians(90-slope))
        y2=0
        x2=x1+(y2-y1)/m

        g_i.selectmeshpoints()
        g_o.acp("Node",(x2,y2))

        g_o.update()

        #### gotostructures

        g_i.gotostages()
        phase0=g_i.InitialPhase
        phase=[phase0]
        excav=[f'{i} th excavation' for i in range(100)]
        init_depth=-1*FirstNailDepth
        k=0 #for embedded beam selection
        l=0 #for plates selection
        plate_index=[]
        beam_index=[]
        y1_dat=[]
        y2_dat=[]
        counter=0 #counts elements in y1_dat and y2_dat

        for i in range(step):

           phase.append(g_i.phase(phase[i]))
           g_i.setcurrentphase(phase[i+1]) 
           g_i.activate(g_i.LineLoads,g_i.Phases[1])
           for polygon in g_i.SoilPolygons[:]:

               a=polygon.BoundingBox.value #string
               y2=float(a.split(';')[1].strip()) #bottom left coordinate of polygon
               y1=float(a.split(';')[3].strip(')')) #top right coordinate of polygon
               x=float(a.split(';')[0].strip('min: ('))

               if y1==-round(i*d,4) and y2==-round((i+1)*d,4) and x==0: #sometimes soil to be non excavated may have same y coordinate(min max)
                   g_i.deactivate(polygon,g_i.Phases[i+1])
                   g_i.Phases[i+1].Identification.set(excav[i]+" excavation")
                   y1_dat.append(y1)
                   y2_dat.append(y2)
                   counter=counter+1
                   break
               elif y1==-round(i*d,4)and y2==-1*YExtent and x==0:  #y2 bottom left y1 top right
                   g_i.deactivate(polygon,g_i.Phases[i+1])
                   g_i.Phases[i+1].Identification.set(excav[i]+" excavation")
                   y1_dat.append(y1)
                   y2_dat.append(y2)
                   counter+=1
                   for poly in g_i.SoilPolygons[:]:

                       a=poly.BoundingBox.value #string
                       y2=float(a.split(';')[1].strip()) #bottom left coordinate of polygon
                       y1=float(a.split(';')[3].strip(')')) #top right coordinate of polygon

                       if y1==-1*YExtent and y2==-round((i+1)*d,4):

                           g_i.deactivate(poly,g_i.Phases[i+1])
                           y1_dat.append(y1)
                           y2_dat.append(y2)
                           counter+=1
                           break
               elif y2==-H and y1==-round((i)*d,4) and x==0:  #H should be positive
                   g_i.deactivate(polygon,g_i.Phases[i+1])
                   g_i.Phases[i+1].Identification.set(excav[i]+" excavation")
                   y1_dat.append(y1)
                   y2_dat.append(y2)
                   counter+=1
                   break

               #embeddedbeamrow selection
           if i+1>step:
               break

           excav_beam=[]
           n=k #store previous value of k
           if i+1<step:
               while round(init_depth,6)>-round((i+1)*d,6) :  #d=depth of each excavation


                   if k==len(g_i.EmbeddedBeamRows):
                       break
                   else:
                       g_i.activate(g_i.EmbeddedBeamRows[k],phase[i+1])
                       excav_beam.append(k)
                       k+=1 
                       #for indexing of beam row
                       init_depth-=step1 #1=vertical spacing of embedded beam 


           elif i+1==step:
               while round(init_depth,6)>-H :  #d=depth of each excavation
                   if k==len(g_i.EmbeddedBeamRows):
                       break
                   else:
                       g_i.activate(g_i.EmbeddedBeamRows[k],phase[i+1])
                       excav_beam.append(k)
                       k+=1 #for indexing of beam row
                       init_depth-=step1 #1=vertical spacing of embedded beam

           beam_index.append(excav_beam)
           print(beam_index)

           u=k-n #no. of embedded beam in a phase
           print('u= '+str(u))

           excav_plate=[]
               #plate selection

           if round(init_depth+u*step1,4)==-round((i*d),4):
               print('...entered')
               if round(init_depth,4)<-1*YExtent and round(init_depth+step1,4)>-1*YExtent:  #-10 soil layer depth
                   if y2==-1*YExtent:
                       for plate_no in range(u):
                           print(phase[i+1].Name)
                           g_i.activate(g_i.Plates[l],phase[i+1])
                           excav_plate.append(l)
                           l+=1

                   else:
                       for plate_no in range(u+1):
                           print(phase[i+1].Name)
                           g_i.activate(g_i.Plates[l],phase[i+1])

                           excav_plate.append(l)
                           l+=1
               else:


                   for plate_no in range(u):
                       #print(phase[i+1].Name)
                       #print('aaa')
                       g_i.activate(g_i.Plates[l],phase[i+1])
                       excav_plate.append(l)
                       l+=1


           else:
               print(y2_dat[counter-1],y1_dat[counter-2])
               print('fakg')
               if y2_dat[counter-1]<-1*YExtent and y1_dat[counter-2]>-1*YExtent and y1_dat[counter-2]==-round(i*d,4):

                   if  init_depth+step1==-1*YExtent or init_depth+2*step1==-1*YExtent or init_depth+3*step1==-1*YExtent or init_depth+4*step1==-1*YExtent or init_depth+5*step1==-1*YExtent:
                       for plate_no in range(u+1):
                           g_i.activate(g_i.Plates[l],phase[i+1])
                           excav_plate.append(l)
                           l+=1
                   else:
                       for plate_no in range(u+2):

                           g_i.activate(g_i.Plates[l],phase[i+1])
                           excav_plate.append(l)
                           l+=1

               else:
                   for plate_no in range(u+1):
                       g_i.activate(g_i.Plates[l],phase[i+1])
                       excav_plate.append(l)
                       l+=1



           plate_index.append(excav_plate)
           


        # ### if depth of excavation and soil nail spacing doesn't match error may occur as program formulated that way

        # ### calculation



        safephase=[]
        for i in range(step):
            safephase.append(g_i.phase(g_i.Phases[i+1]))
            g_i.setcurrentphase(safephase[i])
            g_i.Phases[step+1+i].DeformCalcType.set('Safety')

        for i in range(step-1):
            g_i.set(safephase[i].ShouldCalculate,False)   #only last phase fos is found

        g_i.calculate()


        for i in range(len(phase)):
            if g_i.Phases[i].CalculationResult!=1:
                break

        error = g_i.echo(g_i.Phases[i].LogInfo)

        import os
        directory = 'Error'
        if not os.path.exists(directory):
            os.makedirs(directory)
        error_message = f'Plaxis_Model_no {Model_id} {error}\n'
        with open(directory + '\error1.txt', 'a') as f:
            current_time = time.localtime()
            formatted_time = f"{current_time.tm_year}/{current_time.tm_mon}/{current_time.tm_mday} [{current_time.tm_hour}:{current_time.tm_min}:{current_time.tm_sec}]"
            f.write(f'{error_message} -> {formatted_time}\n')


        # ### May need to change path to save file


        name = 'Plaxis_Model_no ' + str(Model_id)
        directory = os.getcwd() + "\\Models\\"
        if not os.path.exists(directory):
            os.makedirs(directory)
        g_i.save(directory + name)

        # viewing the first phase of excavation
        g_i.view(phase[1])
        # ### Output
        # ### Fos
        ### Output for factor of safety 
        #not needed though
        FOS=g_i.Phases[-1].Reached.SumMsf.value
        #displacementMax = g_i.Phases[-1]
        print(FOS)

        #getting summsf values for curve generation
        def gettable_summsf_vs_ux(filename=None, phaseorder=None):
            # init data for lists
            stepids = []
            uyAs = []
            summsfs = []
            phasenames = []
            # look into all phases, all steps:
            for phase in phaseorder:
                for step in phase.Steps.value:
                    phasenames.append(phase.Name.value)
                    stepids.append(int(step.Name.value.replace("Step_", "")))
                    uyAs.append(g_o.getcurveresults(g_o.Nodes[0],
                                                    step,
                                                    g_o.ResultTypes.Soil.Ux))
                    
                    # make sure step info on summsf is available, then add it:
                   
                    if hasattr(step, 'Reached'):
                        if hasattr(step.Reached, 'SumMsf'):
                            summsf = step.Reached.SumMsf.value
                            

                    summsfs.append(summsf)

            if filename:
                with open(filename, "w") as file:
                    file.writelines(["{}\t{}\t{}\t{}\n".format(ph, nr, stepp, uxA)                             for ph, nr, stepp, uxA in zip(phasenames,
                                                                    stepids,
                                                                    summsfs, 
                                                                    uyAs)])

        # ### Displacement

        #getting displacement values for curve generation in x direction

        def gettable_step_vs_ux(filename=None, phaseorder=None):
            # init data for lists
            uxAs = []

            # look into all phases, all steps:
            for phase in phaseorder:
                for step in phase.Steps.value:
                    uxAs.append(g_o.getcurveresults(g_o.Nodes[0],
                                                    step,
                                                    g_o.ResultTypes.Soil.Ux))
            return uxAs                    # make sure step info on summsf is available, then add it:

        displacementsInXdirection = gettable_step_vs_ux(filename=None, phaseorder=[g_o.Phases[-2]])

        with open('resultOfModels_FOSandDisplacement.txt','a') as f:
            for par in parameters.values():
                f.write(f'{par}\t')
            f.write(f'{round(FOS,3)}\t{round(displacementsInXdirection[-1],3)}')
            f.write('\n')

if __name__ == '__main__':
    startPlaxis()
    with open('resultOfModels_FOSandDisplacement.txt','a') as f:
        HEADINGS = ['S.N.','E','Gam','phi','C','Neu','dil','ExDep','Bfill','Plthk','FAng','Inc','Sp','Len','FOS','Dis']
        for Head in HEADINGS:
            f.write(f'{Head}\t')
        f.write('\n')
    root = Tk()

    start_label = Label(root, text="Enter starting Model_No:")
    start_label.pack()
    start_entry = Entry(root)
    start_entry.pack()

    end_label = Label(root, text="Enter ending Model_No:")
    end_label.pack()
    end_entry = Entry(root)
    end_entry.pack()

    submit_button = Button(root, text="Submit", command=lambda: run_code(int(start_entry.get()), int(end_entry.get())))
    submit_button.pack()

    root.mainloop()