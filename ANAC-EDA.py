# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 14:08:20 2021

@author: thiag
"""

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

dummy = []
for index, x in df.iterrows():
    if x['decolagens'] == 0:
        dummy.append(abs(x['atk']) < 1000)
    else:
        dummy.append(abs(x['atk'] - x['payload']*x['distancia_voada_km']/(1000*x['decolagens'])) < 1000)
print('The number of atk values that correspond to atk calculation is: {:.2f}%'.format(100*sum(dummy)/len(dummy)))
df['atk_calc']=df['payload']*df['distancia_voada_km']/(1000*df['decolagens'])

del dummy

df1 = pd.DataFrame(df.groupby(by='data').agg('sum')['decolagens'])

df1.reset_index(inplace=True)
ax = sns.catplot(x='data', y='decolagens', data=df1, kind='bar', color='b',
                 sharey=True)

ax.set_xticklabels(rotation=90, ha="right")    
ax.fig.suptitle('# TAKEOFFs per month')

df2 = pd.DataFrame(df.groupby(by='aeroporto_de_origem_nome').agg('sum')['decolagens'])
df2 = df2.sort_values(by=['decolagens'], ascending=False)
print(df2[:10])
df2.reset_index(inplace=True)

ax = sns.catplot(x='aeroporto_de_origem_nome', y='decolagens',
                 data=df2[:20], kind='bar', color='b', sharey=True)

ax.set_xticklabels(rotation=90, ha="right")
ax.fig.suptitle('# TAKEOFFs per airport')


df3 = df[df['aeroporto_de_origem_nome']=='GUARULHOS']


df4 = pd.DataFrame(df.groupby(by=['data', 'empresa_nacionalidade']).agg('sum')['decolagens'])

df4[df4.index.isin(['ESTRANGEIRA'],level=1)]['decolagens'].values

df4.reset_index(inplace=True)

ax = sns.catplot(x='data', y='decolagens',
                 data=df4, kind='bar', hue='empresa_nacionalidade', sharey=True)

ax.set_xticklabels(rotation=90, ha="right")
ax.fig.suptitle('# TAKEOFFs per airport - nationality')


# df5 = df4.unstack()
# df6 = df4.apply(lambda x: x/x.sum()*100, axis=1)



df5 = pd.DataFrame(df.groupby(by=['rota_nome']).agg('sum')['decolagens'])
df5 = df5.sort_values(by=['decolagens'], ascending=False)
df5.reset_index(inplace=True)

ax = sns.catplot(x='rota_nome', y='decolagens',
                 data=df5[:20], kind='bar', color='b', sharey=True)

ax.set_xticklabels(rotation=90, ha="right")
ax.fig.suptitle('# TAKEOFFs per route')


toproutes = df5['rota_nome'][:5]

df6 = pd.DataFrame(df[df['rota_nome'].isin(list(toproutes))]
                   .groupby(by=['data', 'rota_nome'])
                   .agg('sum')['decolagens'])
df6.reset_index(inplace=True)


ax = sns.catplot(x='data', y='decolagens', #hue='rota (nome)', 
            col='rota_nome', color='b', data=df6, kind='bar', col_wrap=2,
            sharey=True)

ax.set_xticklabels(rotation=90, ha="right")
ax.fig.suptitle('# TAKEOFFs per month - route')


df7 = pd.DataFrame(df.groupby(by=['rota_nome', 'empresa_nacionalidade'])
                   .agg('sum')['rpk'])

df7 = df7.sort_values(by=['rpk'], ascending=False)

df7.reset_index(inplace=True)

ax = sns.catplot(x='rota_nome', y='rpk', #hue='rota_nome', col='empresa_nacionalidade',
                 data=df7[0:20], kind='bar', color='b', #col_wrap=2,
                 sharey=True)

ax.set_xticklabels(rotation=90, ha="right")
ax.fig.suptitle('RPK per route')

toprpkroutes = df7['rota_nome'].loc[:19]

df8 = pd.DataFrame(df[df['rota_nome'].isin(list(toprpkroutes))]
                    .groupby(by=['rota_nome', 
                                 'empresa_nome',
                                 'data']).agg(
                                       rpk=pd.NamedAgg('rpk','sum'),
                                       decolagens=pd.NamedAgg('decolagens','sum')
                                       ))
df8.reset_index(inplace=True)
ax = sns.catplot(x='data', y='rpk', #hue='decolagens',
                 col='rota_nome',
                 data=df8, kind='bar', col_wrap=4,
                 sharey=True, )

ax.set_xticklabels(rotation=90, ha="right")
ax.fig.suptitle('RPK per month - route')

df9 = pd.DataFrame(df.groupby(by=['quarter',
                                  'aeroporto_de_origem_nome']).agg('sum')[
                                      'decolagens'])
df9.reset_index(inplace=True)

df9 = df9.pivot(index='aeroporto_de_origem_nome',columns=['quarter'],values='decolagens').fillna(0)
df9['delta'] = df9['2019-2Q']-df9['2020-2Q']