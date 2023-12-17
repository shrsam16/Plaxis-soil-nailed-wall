# parameterKeys = ['S.N.','E','Gam','phi','C','Neu','dil','ExDep','Bfill','Plthk','FAng','Inc','Sp','Len']
# print(parameterKeys)
MoreIsGood = [False,True,False,True,True,True,True, False, False, True, True, True, False, True]
BestofFailed = [10000*x for x in MoreIsGood]
# print (BestofFailed)


def WroseForSure(Model1, Model2):
    #print(Model1, Model2)
    Model1List = list(Model1.values())
    Model2List = list(Model2.values())
    print(Model1List)
    print(Model2List)
    for m1, m2, che in zip(Model1List, Model2List, MoreIsGood):
        if(m1 == m2):
            continue
        elif((m1>m2) == che):
            continue
        else:
            return True
        # if m1>=m2 == che:
        #     continue
    
# for i in range (100,201):
#     para = next(main.getParameter(100))
#     print(compareToBestofFailed(para))