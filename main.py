import loopsamyak as lpsmk

def crudeFOS(Len, Sp, FAng):
    return Len - Sp + FAng

def getParameter(MODELNUMBER):
    counter = 1
    for e in E:#1
        for Gam in GammaUnsat:#2
            for p in phi:
                if p<30:
                    dilatency = 0
                else:
                    dilatency = p-30
                for c in C:#3
                    for n in Neu:#5
                        for ExDep in ExcavationDepth:#6
                            Bfill = 0
                            for Plthk in PlateThickness:
                                for FAng in FaceAngle:#8
                                    for inc in NailInclination:#9
                                        for sp in NailSpacing:#10
                                            for Nl in NailLength:#11
                                                if counter < MODELNUMBER:
                                                    counter += 1
                                                    continue
                                                
                                                parameter = {'E': e,
                                                                'Gam' : Gam,
                                                                'phi' : p,
                                                                'C' : c,
                                                                'Neu' : n,
                                                                'dil' : dilatency,
                                                                'ExDep' : ExDep,
                                                                'Bfill' : Bfill,
                                                                'Plthk' : Plthk,
                                                                'FAng' : FAng,
                                                                'Inc' : inc,
                                                                'Sp' : sp,
                                                                'Len' : Nl
                                                                }
                                                yield parameter

E = [8000, 6500 ,5000]
GammaUnsat = [19.5, 21.0, 22.5]
phi = [26.0,30.0,34.0]
C = [25.0,15.0,5.0]
Neu = [0.35, 0.30]

#Geometry
ExcavationDepth = [6.0]#[2.0,4.0,6.0,8.0,10.0]
# BackfillAngle = [13.0]#[0.0, 13.0, 26.0] 
FaceAngle = [5.0, 10.0]#[10.0, 5.0, 0.0]
#Nail
NailInclination = [15]#[13.0,15.0,18.0]
NailSpacing = [0.5, 0.7, 0.9]
NailLength = [1.2, 1.0, 0.8]#[0.8, 0.7, 0.6]
NailDiameter = 32.0
#plate
PlateThickness = [100, 200]#[150]

if __name__ == "__main__":
    
    #global startIndex, stopIndex
    startIndex = int(input("model start index: "))
    stopIndex = int(input("model end index: "))
    # modelCounter = 0
    # maxNoOfModels = 2
    parameterKeys = ['S.N.','E','Gam','phi','C','Neu','dil','ExDep','Bfill','Plthk','FAng','Inc','Sp','Len']
    lpsmk.startPlaxis()
    for MODELNUMBER in range (startIndex, stopIndex+1):
        parameters = next(getParameter(MODELNUMBER))
        # if modelCounter == 0:
        #     lpsmk.startPlaxis()
        # if modelCounter < maxNoOfModels:
        #     modelCounter += 1
        # else:
        #     modelCounter = 0
        lpsmk.run_code(parameters)
        print(f"{MODELNUMBER} CrudeFos = {round(crudeFOS(parameters['Len'], parameters['Sp'], parameters['FAng']), 3)}")