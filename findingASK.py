# -*- coding: utf-8 -*-
"""
Created on Sat May  8 20:37:16 2021

@author: thiag
"""

import os
import pandas as pd
import seaborn as sns
import unidecode
import numpy as np

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

# df['rpk'] = df['rpk'].fillna(0)
# df['ask'] = df['ask'].fillna(0)
# df['rtk'] = df['rtk'].fillna(0)
# df['atk'] = df['atk'].fillna(0)
df['bagagem_kg'] = df['bagagem_kg'].fillna(0)

dummy = []
for index, x in df.iterrows():
    if x['ask'] == 0:
        dummy.append(0)
    elif x['ask'] < x['rpk']:
        dummy.append(x['passageiros_pagos']/x['assentos'])
    else:
        dummy.append(x['rpk']/x['ask'])
         
df['rpk-ask'] = dummy
del dummy




from sklearn.model_selection import GridSearchCV


from sklearn.neural_network import MLPRegressor


X = df[[
        'passageiros_pagos', 
#        'passageiros_gratis',
        'carga_paga_kg',
#        'carga_gratis_kg',
#        'correio_kg',
        'distancia_voada_km',
        'decolagens',
#        'assentos',
#        'carga_paga_km',
#        'carga_gratis_km',
#        'correio_km',
#        'payload',
        'bagagem_kg'
        ]]

X = X.fillna(value=0)

Y1 = df['rtk']
Y2 = df['atk']

regr = MLPRegressor(random_state=1, max_iter=1000).fit(X, Y1)

Ypred = regr.predict(X)

print(regr.score(X,Y1))

for z in X.columns:
    print(z, np.corrcoef(X[z],Y1)[0,1])
    
dummy3 = df['rtk']*1000*df['decolagens']/df['distancia_voada_km']/(
    90*df['passageiros_pagos']+df['carga_paga_kg']+df['correio_kg']+
    df['bagagem_kg'])


def matching(k):
    
    dummy = []
    for index, x in df.iterrows():
        if x['decolagens'] == 0:
            dummy.append(abs(x['rtk']) < 1000)
        else:
            dummy.append(abs(x['rtk'] - (k*x['passageiros_pagos']+x['carga_paga_kg']+x['correio_kg']+x['bagagem_kg'])*x['distancia_voada_km']/
                             (1000*x['decolagens'])) < 1000)
    return 1/sum(dummy)

def matching_br(k):
    
    dummy = []
    for index, x in df[df['empresa_nacionalidade']=='BRASILEIRA'].iterrows():
        if x['decolagens'] == 0:
            dummy.append(abs(x['rtk']) < 1000)
        else:
            dummy.append(abs(x['rtk'] - (k*x['passageiros_pagos']+x['carga_paga_kg']+x['correio_kg']+x['bagagem_kg'])*x['distancia_voada_km']/
                             (1000*x['decolagens'])) < 1000)
    return 1/sum(dummy)

def matching_frgn(k):
    
    dummy = []
    for index, x in df[df['empresa_nacionalidade']=='ESTRANGEIRA'].iterrows():
        if x['decolagens'] == 0:
            dummy.append(abs(x['rtk']) < 1000)
        else:
            dummy.append(abs(x['rtk'] - (k*x['passageiros_pagos']+x['carga_paga_kg']+x['correio_kg']+x['bagagem_kg'])*x['distancia_voada_km']/
                             (1000*x['decolagens'])) < 1000)
    return 1/sum(dummy)

from scipy import optimize

res = optimize.minimize_scalar(matching, bounds=(70,150), method='bounded',
                                options={'maxiter':100})

print(res)


res_br = optimize.minimize_scalar(matching_br, bounds=(70,150), method='bounded',
                                options={'maxiter':100})

print(res_br)

res_frgn = optimize.minimize_scalar(matching_frgn, bounds=(70,150), method='bounded',
                                options={'maxiter':100})

print(res_frgn)
