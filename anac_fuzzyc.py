# -*- coding: utf-8 -*-
"""
Created on Fri May 14 11:06:59 2021

@author: thiag
"""

import skfuzzy as fuzz
import numpy as np
import os
import pandas as pd
import seaborn as sns
import unidecode

folder = r'C:\Users\thiag\data\ANAC-transport'

dffiles = ['resumo_anual_2019.csv',
         'resumo_anual_2020.csv',
         'resumo_anual_2021.csv']

df = pd.concat([pd.read_csv(os.path.join(folder, x),
                            sep=';', encoding=('ISO-8859-1'))
                for x in dffiles])

df.columns = [unidecode.unidecode(z.lower())
              .replace(' ','_')
              .replace('(','')
              .replace(')','') 
              for z in df.columns]

df.to_csv('3years.csv', sep=';', index=False)
df['data'] = [str(x['ano']) + '-' + "{:02}".format(x['mes'])
              for index, x in df.iterrows()]

df['rota'] = [str(x['aeroporto_de_origem_sigla']) + '->' +
              str(x['aeroporto_de_destino_sigla'])
              for index, x in df.iterrows()]

df['rota_nome'] = [str(x['aeroporto_de_origem_nome']) + '->' +
              str(x['aeroporto_de_destino_nome'])
              for index, x in df.iterrows()]

def quarter(x):
    year = x['ano']
    mes = x['mes']
    if mes in [1, 2, 3]:
        quarter = str(year) + '-Q1' 
    elif mes in [4, 5, 6]:
        quarter = str(year) + '-Q2' 
    elif mes in [7, 8, 9]:
        quarter = str(year) + '-Q3' 
    elif mes in [10, 11, 12]:
        quarter = str(year) + '-Q4' 
    return quarter

df['quarter'] = df.apply(quarter, axis=1)

print('{:.2f} % of the rpk values is NaN.'
      .format(100*sum(df['rpk'].isna())/df.shape[0]))
print('{:.2f} % of the ask values is NaN.'
      .format(100*sum(df['ask'].isna())/df.shape[0]))
print('{:.2f} % of the rtk values is NaN.'
      .format(100*sum(df['rtk'].isna())/df.shape[0]))
print('{:.2f} % of the atk values is NaN.'
      .format(100*sum(df['atk'].isna())/df.shape[0]))
print('{:.2f} % of the baggage values is NaN.'
      .format(100*sum(df['bagagem_kg'].isna())/df.shape[0]))

# df['rpk'] = df['rpk'].fillna(0)
# df['ask'] = df['ask'].fillna(0)
# df['rtk'] = df['rtk'].fillna(0)
# df['atk'] = df['atk'].fillna(0)
# df['bagagem_kg'] = df['bagagem_kg'].fillna(0)

dummy = []
for index, x in df.iterrows():
    if x['decolagens'] == 0:
        dummy.append(abs(x['rpk']) < 1000)
    else:
        dummy.append(abs(x['rpk'] - x['passageiros_pagos']*x['distancia_voada_km']/x['decolagens']) < 1000)
print('The number of rpk values that correspond to rpk calculation is: {:.2f}%'.format(100*sum(dummy)/len(dummy)))
df['rpk_calc']= df['passageiros_pagos']*df['distancia_voada_km']/df['decolagens']
del dummy


dummy = []
for index, x in df.iterrows():
    if x['decolagens'] == 0:
        dummy.append(abs(x['ask']) < 1000)
    else:
        dummy.append(abs(x['ask'] - x['assentos']*x['distancia_voada_km']/x['decolagens']) < 1000)
print('The number of ask values that correspond to ask calculation is: {:.2f}%'.format(100*sum(dummy)/len(dummy)))
df['ask_calc']=df['assentos']*df['distancia_voada_km']/df['decolagens']

del dummy

dummy = []
for index, x in df.iterrows():
    if x['decolagens'] == 0:
        dummy.append(abs(x['atk']) < 1000)
    else:
        dummy.append(abs(x['atk'] - x['payload']*x['distancia_voada_km']/(1000*x['decolagens'])) < 1000)
print('The number of atk values that correspond to atk calculation is: {:.2f}%'.format(100*sum(dummy)/len(dummy)))
df['atk_calc']=df['payload']*df['distancia_voada_km']/(1000*df['decolagens'])

del dummy

dummy = []
rtk_calc = []
for index, x in df.iterrows():
    if x['empresa_nacionalidade'] == 'BRASILEIRA':
        avgw = 75
    elif x['empresa_nacionalidade'] == 'ESTRANGEIRA':
        avgw = 90
        
    if x['decolagens'] == 0:
        rtk = float('NaN')
        dummy.append(abs(x['rtk']) < 1000)
    else:
        rtk = (avgw*x['passageiros_pagos']+x['carga_paga_kg']+x['correio_kg']+x['bagagem_kg']
           )*x['distancia_voada_km']/(1000*x['decolagens'])
        dummy.append(abs(x['rtk'] - rtk) < 1000)
    rtk_calc.append(rtk)

print('The number of rtk values that correspond to rtk calculation is: {:.2f}%'.format(100*sum(dummy)/len(dummy)))
df['rtk_calc'] = rtk_calc
del dummy, rtk, avgw, rtk_calc

def data_transform(df):
    x = df.copy()
    x = x.drop([
        'empresa_sigla', 'empresa_nome', 'ano', 'mes',
        'aeroporto_de_origem_sigla', 'aeroporto_de_origem_nome',
        'aeroporto_de_origem_uf', 'aeroporto_de_origem_regiao',
        'aeroporto_de_origem_pais', 'aeroporto_de_origem_continente',
        'aeroporto_de_destino_sigla', 'aeroporto_de_destino_nome',
        'aeroporto_de_destino_uf', 'aeroporto_de_destino_regiao',
        'aeroporto_de_destino_pais', 'aeroporto_de_destino_continente',
        'combustivel_litros', 'grupo_de_voo',
        'data', 'rota', 'rota_nome', 'quarter', 'ask', 'rpk', 'atk',  
        'ask_calc', 'rpk_calc', 'atk_calc', 'carga_paga_km', 'carga_gratis_km',
        'correio_km'], axis=1)
    
    dlist = []
    x['horas_voadas']=[y.replace(',','.') for y in x['horas_voadas'].astype(str)]
    x['horas_voadas']= [float(y) for y in x['horas_voadas']]

    dlist.append(numerize(x, 'empresa_nacionalidade'))
    dlist.append(numerize(x, 'natureza'))

    x.dropna(axis=0, subset=['bagagem_kg'], inplace=True)
    x.dropna(axis=0, subset=['rtk'], inplace=True)
    x.dropna(axis=0, subset=['rtk_calc'], inplace=True)
    x.dropna(axis=0, subset=['horas_voadas'], inplace=True)
    # x = x
    return x

def numerize(df, colname):
    x = df[colname].unique()
    d = dict(enumerate(x.flatten()))
    d_inv = {v: k for k, v in d.items()}
    df[colname] = df[colname].replace(d_inv)
    return d

df2 = data_transform(df)


imin = 3
imax = 6
    
fpcs = []
centers = []
clusters = []

for i in range(imin, imax):
    center, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(\
        df2.transpose(), i, 2, error=0.001, \
        maxiter=10000, init=None)
    cluster_membership = np.argmax(u, axis=0)
    
#agrupa funcao de desempenho
    fpcs.append(fpc)
#agrupa os centroides
    centers.append(pd.DataFrame(center, columns=df2.columns))
#agrupa o peso dos centroides
    clusters.append(cluster_membership)


X_train = df2
y = df2['rtk_calc'] - df2['rtk']

from sklearn import linear_model
from sklearn import svm

classifiers = [
    svm.SVR(),
    linear_model.SGDRegressor(),
    linear_model.BayesianRidge(),
    linear_model.LassoLars(),
    linear_model.ARDRegression(),
    linear_model.PassiveAggressiveRegressor(),
    linear_model.TheilSenRegressor(),
    linear_model.LinearRegression()]

for item in classifiers:
    print(item)
    clf = item
    clf.fit(X_train, y)
    print(clf.predict(X_train),'\n')