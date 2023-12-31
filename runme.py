import datetime
import pandas as pd
import numpy as np
from algormeter import algorMeter, perfProf
from algormeter.libs import JB01, JB02, JB03, JB04, JB05, JB06, JB07, JB08, JB09, JB10
import algormeter.algorithms as alg
import DADC as da


problems = [ # number are X dimensions

            (JB01,[2]), 
            (JB02,[2]), 
            (JB03,[4]), 
            (JB04,[2,5,10,50,100,150,200,250,500,750
                   ]),
            (JB05,[ 2,5,10,50, 100,150, 200 ,250,300,350,400,500,1000,1500,3000,10000,15000,20000,50000
                   ]),
            (JB06,[2]),
            (JB07,[2]),
            (JB08,[3]),
            (JB09,[4]),
            (JB10,[2,4,5,10,20,50,100,150,200
                   ]),
        ]
iterations = 3000
algorithms = [da.DADC]

ts = datetime.datetime.now()
df, pv= algorMeter(algorithms = algorithms,  iterations = iterations, 
                     problems = problems,
                     # trace=True, 
                    #  dbprint = True, 
                     )

pvf1 = np.round(pd.pivot_table(df, values=['f1'],index=['Algorithm',],columns=['Status'],aggfunc=['sum'],margins=True),2) 
print('\n', df)
print('\n', pv)
print('\n', pvf1)

usedtime = datetime.datetime.now() - ts  
print('\nElapsed time:',usedtime,'\n')

df.to_pickle('exp.pickle')

if len(algorithms) > 1:
       import matplotlib.pyplot as plt
       
       perfProf(df, costs= ['f1','Seconds','qp.solv','qp.maxRow'] )
       plt.show(block=True)
