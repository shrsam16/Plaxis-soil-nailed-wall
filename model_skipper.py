import pandas as pd

def shouldSkip(varied_list):
    varied = pd.Series(varied_list.values(), index =varied_list.keys())
    varied.loc[len(varied)] = varied_list.values()  
    forbidden = pd.read_csv('too_weak.csv', header = None, names = ['E'  ,'Gam','phi' ,'C'   ,'Neu' ,'dil' ,'ExDep' ,'Bfill' ,'Plthk' ,'FAng' ,'Inc' ,'Sp' ,'Len'])
#    too_weak.csv cannot be empty. It needs at least one valid entry.   
    better_model = forbidden.loc[( forbidden['E'] >= varied['E'])&
                                 (forbidden['Gam'] <= varied['Gam'])&
                                 (forbidden['phi'] >= varied['phi'])&
                                 (forbidden['C'] >= varied['C'])&
                                 (forbidden['Neu'] == varied['Neu'])&
                                 (forbidden['dil'] >= varied['dil'])&
                                 (forbidden['ExDep'] <= varied['ExDep'])&
                                 (forbidden['Bfill'] <= varied['Bfill'] ) &
                                ( forbidden['Plthk'] >= varied['Plthk'])&
                                (forbidden['FAng'] >= varied['FAng'])&
                                (forbidden['Inc'] == varied['Inc'])&
                                (forbidden['Sp'] <= varied['Sp'])&
                                (forbidden['Len'] >= varied['Len']) ]  
    if len(better_model) > 0:
        # print('skip')
        return True
    else:
        # print('run')
        return False

       
        




