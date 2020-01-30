# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 01:51:01 2020

@author: Ринат
"""

import pyodbc 
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=localhost;'
                      'Database=ERP245_2;'
                      'Trusted_Connection=yes;')

cursor = conn.cursor()

# CONVERT(VARCHAR(MAX), T2._Fld4865RRef, 2),
# master.dbo.fn_varbintohexstr (T2._Fld4865RRef),
cursor.execute('sp_executesql N' + '\''+ '''SELECT
master.dbo.fn_varbintohexstr (T2._Fld4865RRef),
T1._Fld35770
FROM dbo._AccumRg35757 T1
LEFT OUTER JOIN dbo._Reference179 T2
ON (T1._Fld35758RRef = T2._IDRRef) AND (T2._Fld1551 = @P1)
LEFT OUTER JOIN dbo._Reference71 T3
ON (T1._Fld35763RRef = T3._IDRRef) AND (T3._Fld1551 = @P2)
WHERE ((T1._Fld1551 = @P3)) AND ((T3._Fld2707RRef = @P4))
ORDER BY (T1._Period)\',N\'@P1 numeric(10),@P2 numeric(10),@P3 numeric(10),@P4 varbinary(16)\',0,0,0,0x950F701CE782F51F11EA3FA0CB15308C''')

prod = {}
quantity = {}
i=0
row = cursor.fetchone()
while row:
#   print (str(row[0]) + " " + str(row[1]) + " " + str(row[2]) + " " + str(row[3]))
#   print (str(row[0]) + " " + str(row[1]) + " " + str(row[2]))
    prod[i] = row[0]
    quantity[i] = float(row[1])
    i=i+1
    row = cursor.fetchone()
    
from sample3_3 import *

n_lag = 1
n_seq = 3
n_test = -36     # 10   -36
n_epochs = 1500   # 1500 300
n_batch = 1
n_neurons = 4   # 1 4
# prepare data
import pandas as pd 
import numpy

numpy.random.seed(27)
  
# create a series 
series = pd.Series(quantity)

#from matplotlib import pyplot
#pyplot.plot(series.values)

scaler, train, test = prepare_data(series, n_test, n_lag, n_seq)

model = fit_lstm(train, n_lag, n_seq, n_batch, n_epochs, n_neurons)
# make forecasts
model.reset_states()
#forecasts = make_forecasts(model, n_batch, test, n_lag, n_seq)
forecasts = make_forecasts_fin(model, n_batch, train, n_lag, n_seq)
# inverse transform forecasts and test
#forecasts = inverse_transform(series, forecasts, scaler, n_test+2)
forecasts_i = inverse_transform(series, forecasts, scaler, -n_test)

#actual = [row[n_lag:] for row in test]
#actual = inverse_transform(series, actual, scaler, n_test+2)
# evaluate forecasts
#evaluate_forecasts(actual, forecasts, n_lag, n_seq)

# plot forecasts
plot_forecasts(series, forecasts_i, 0)

for i in range(len(forecasts_i[0])):
    sql_str = '''update dbo._Document715_VT23518 
                 set _Fld23523 = ''' + str(forecasts_i[0][i]) + ', _Fld23524 =  ' + str(forecasts_i[0][i]) + '''
                 where _Document715_IDRRef = convert(binary(16),'0x950F701CE782F51F11EA3FAE072074C6',1)
                 and _Fld23520RRef = convert(binary(16),'0x950BD481D76EDCFE11EA37716E30A01F',1)
                 and _Fld23525 = cast(\'4020-''' + str(i+1) + '''-01 00:00:00\' as datetime)'''
    #print(sql_str)
    cursor.execute(sql_str).rowcount

cursor.commit()
cursor.close()