
model_type='All'
model_type='AllSeries'
model_type='AllType'
model_type='AllSeriesMerge'

model_type='AllType'
import sys
if sys.platform == 'win32':
    print(model_type)

data_file='data/Data.txt'
series_id_index=0
series_name_index=1
race_id_index=2
date_index=3
race_name_index=4
circuit_id_index=5
circuit_name_index=6
driver_id_index=7
driver_name_index=8
ini_pos_index=9
fin_pos_index=10
fin_trackpos_index=11
ret_flag_index=12
dsq_flag_index=13
ignore_flag_index=14
num_vars=15

model_year=2020#FLC O modelo devia ficar fechado ate 2020, mudar para 2020 quando for a altura de fechar o modelo

entropy_series_name_index=0
entropy_race_id_index=1
entropy_race_name_index=2
entropy_circuit_id_index=3
entropy_circuit_name_index=4
entropy_calcs_index=5
entropy_year=6
entropy_decade=7

ret_first_vs_last={}
#Value between 0 and 7/600 (0.01166666666), where 0 means that retirements between the 1st and last place of the grid
#are valued the same, while 7/600 means that the last place of the grid retiring means nothing to the REX
#In F1, the value is 1/120 = 0.00833333333
ret_first_vs_last['SingleSeater']=1/120
ret_first_vs_last['Moto']=1/120
ret_first_vs_last['NASCAR']=1/360
ret_first_vs_last['Endurance']=1/120
ret_first_vs_last['Turing']=1/120

series_type=dict()
types=[]
if sys.platform=='win32':
    types_file = 'data/Types.txt'
else:
    types_file = 'rex/data/Types.txt'
with open(types_file, 'r') as file:
    for line in file.readlines():
        [series,type]=line.rstrip('\r\n').split(':')
        series_type[series]=type
        if type not in types:
            types.append(type)

min_year=dict()
min_year['NASCAR Cup']=1972
min_year['MotoGP']=1977

min_drivers=5
entropy_scale=10
error=False
