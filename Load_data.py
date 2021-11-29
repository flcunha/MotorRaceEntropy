import numpy as np
import Settings
import itertools
import random
import sys

def calc_percentile(pos, max_pos):
    return 100 * (pos - 1) / (max_pos - 1)

def list_to_types(s):
    for i in range(len(s)):
        try:
            int(s[i])
            s[i] = int(s[i])
        except ValueError:
            pass
    return s

def get_data():
    data_file = Settings.data_file
    with open(data_file, 'r') as file:
        data = [list_to_types(line.rstrip('\n').split(';')) for line in file.readlines()]
    data=[line for line in data if line[0]!='rch']
    series=list(set([line[Settings.series_name_index] for line in data]))
    return data, series

def load(serie,modelQ=False):
    if modelQ:
        year_max=Settings.model_year
    else:
        year_max=3000
    data, series=get_data()
    if Settings.model_type in ['AllSeries','AllType','All','AllSeriesMerge'] and modelQ:
        data = [line for line in data if line[Settings.series_name_index] in series]
    else:
        data = [line for line in data if line[Settings.series_name_index] == serie]

    classifications = np.array(data, dtype='object')
    races = np.unique(classifications[:, Settings.race_id_index])
    ##FLC ESTA PROXIMA LINHA E SO PARA CORRER RAPIDAMENTE E DESCOBRIR BUGS, REMOVER!!!
    #races = np.unique(classifications[:, Settings.race_id_index][np.array([int(str(date)[0:4]) for date in classifications[:, Settings.date_index]])>2015])
    retirement_dist = []
    classified_pos = []
    classified_pair_dist = []
    races_info = {}
    races_classified = {}
    races_retired = {}
    series_count = {}
    series_races = {}
    unused_races=[]
    non_valid_races=[]
    trackpos_changes=np.where(np.logical_and.reduce((classifications[:, Settings.fin_trackpos_index] > 0, [int(a[0:4])>1970 for a in classifications[:, Settings.date_index]])))
    classifications[trackpos_changes, Settings.fin_pos_index] = classifications[trackpos_changes, Settings.fin_trackpos_index]
    for race in races[::-1]:
        race_info = classifications[np.where(classifications[:, Settings.race_id_index] == [race])[0], :]
        max_ini = max(race_info[:, Settings.ini_pos_index])
        year = int(str(race_info[0][Settings.date_index])[0:4])
        if race_info[0][Settings.series_name_index] in Settings.min_year:
            year_min = Settings.min_year[race_info[0][Settings.series_name_index]]
        else:
            year_min = 1900
        error = False
        if len(race_info) >= Settings.min_drivers and year<=year_max and year>=year_min and race_info[0,Settings.ignore_flag_index]==0 and max(race_info[:,Settings.fin_pos_index])<1000:
            if max_ini > len(race_info):
                missing=[]
                for ini in range(1,max_ini+1):
                    if ini not in race_info[:,Settings.ini_pos_index]:
                        missing.append(ini)
                if sys.platform!='win32':
                    if Settings.error==False:
                        Settings.error=True
                        print('ERROR')
                    print(str(race) + " , " + race_info[0][Settings.series_name_index].ljust(15) + " - I received " + str(len(race_info)).ljust(2) + " drivers, maximum starting grid " + str(max_ini).ljust(2) + ", missing drivers starting at: " + str(missing) + "\n")
                elif modelQ:
                    with open('validation/starting_missing.txt', 'a') as file:
                        file.write(str(race) + " , " + race_info[0][Settings.series_name_index].ljust(15) + " - I received " + str(len(race_info)).ljust(2) + " drivers, maximum starting grid " + str(max_ini).ljust(2) + ", missing drivers starting at: " + str(missing) + "\n")
                error=True
            elif sum(race_info[:,Settings.ini_pos_index])!=max(race_info[:,Settings.ini_pos_index])*(1+max(race_info[:,Settings.ini_pos_index]))/2:
                for ini in range(1, max_ini + 1):
                    if len(np.where(ini==race_info[:, Settings.ini_pos_index])[0])>1:
                        if sys.platform != 'win32':
                            if Settings.error == False:
                                Settings.error = True
                                print('ERROR')
                            print(str(race) + " , " + race_info[0][Settings.series_name_index].ljust(15) + " - multiple drivers starting at: " + str(ini) + "\n")
                        if modelQ:
                            with open('validation/starting_incoherent.txt', 'a') as file:
                                file.write(str(race) + " , " + race_info[0][Settings.series_name_index].ljust(15) + " - multiple drivers starting at: " + str(ini) + "\n")
                error=True

        # #houve desqualificacoes? poe no lugar em q acabaram
            # dsq_index=np.where(np.logical_and.reduce((race_info[:,Settings.dsq_flag_index]==1,race_info[:,Settings.ret_flag_index]==0)))[0]
            # if len(dsq_index)>0:
            #     dsq_list=race_info[dsq_index, :]
            #     dsq_list=dsq_list[np.argsort(dsq_list[:, Settings.fin_pos_index]), :]
            #     for dsq in dsq_list:
            #         if race_info[np.where(race_info[:,Settings.driver_id_index]==dsq[Settings.driver_id_index])[0],Settings.fin_pos_index]>0:
            #             race_info[np.where(race_info[:,Settings.fin_pos_index]>=dsq[Settings.fin_pos_index])[0],Settings.fin_pos_index]+=1
            #             #race_info[np.where(race_info[:,Settings.driver_id_index]==dsq[Settings.driver_id_index])[0],Settings.fin_pos_index]*=-1

            #houve drivers que se retiraram mas classificaram? por nao classificado e diminui todos os que se classificaram depois
            ret_index=np.where(np.logical_and.reduce((race_info[:,Settings.dsq_flag_index]==0,race_info[:,Settings.ret_flag_index]==1,race_info[:,Settings.fin_pos_index]>0)))[0]
            if len(ret_index)>0:
                ret_list=race_info[ret_index,:]
                ret_list = ret_list[np.argsort(-ret_list[:, Settings.fin_pos_index]), :]
                for ret in ret_list:
                    race_info[np.where(race_info[:,Settings.fin_pos_index]>ret[Settings.fin_pos_index])[0],Settings.fin_pos_index]-=1
                    race_info[np.where(race_info[:,Settings.driver_id_index]==ret[Settings.driver_id_index])[0],Settings.fin_pos_index]=0

            #houve drivers q nao se classificaram mas acabaram a corrida? poe em ultimo
            classified_index=np.where(np.logical_and.reduce((race_info[:,Settings.dsq_flag_index]==0,race_info[:,Settings.ret_flag_index]==0,race_info[:,Settings.fin_pos_index]<=0)))[0]
            if len(classified_index)>0:
                classified_list = race_info[classified_index,:]
                classified_zero=np.where(classified_list[:,Settings.fin_pos_index]==0)[0]
                if len(classified_zero)>0:
                    classified_list[classified_zero,Settings.fin_pos_index]=-1000
                classified_list = classified_list[np.argsort(-classified_list[:, Settings.fin_pos_index]), :]
                for classified in classified_list:
                    race_info[np.where(race_info[:,Settings.driver_id_index]==classified[Settings.driver_id_index])[0],Settings.fin_pos_index]=max(race_info[:,Settings.fin_pos_index])+1

            for index in np.where(race_info[:,Settings.fin_pos_index]<0)[0]:
                race_info[index,Settings.fin_pos_index]=0

            #check if duplicate/missing final positions
            if sum(race_info[:,Settings.fin_pos_index])!=max(race_info[:,Settings.fin_pos_index])*(1+max(race_info[:,Settings.fin_pos_index]))/2 and not error:
                found=False
                error=True
                for fin in range(1,max(race_info[:,Settings.fin_pos_index])+1):
                    if len(np.where(race_info[:,Settings.fin_pos_index]==fin)[0])>1:
                        found=True
                        if sys.platform != 'win32':
                            if Settings.error == False:
                                Settings.error = True
                                print('ERROR')
                            print(str(race) + " , " + race_info[0][Settings.series_name_index].ljust(15) + " - Multiple drivers finishing in " + str(fin) + ": " + ', '.join(driver_aux) + "\n" if isinstance(driver_aux,np.ndarray) else driver_aux + "\n")
                        if modelQ:
                            driver_aux = race_info[np.where(race_info[:, 10] == fin)[0], Settings.driver_name_index]
                            with open('validation/finishing_incoherent.txt', 'a') as file:
                                file.write(str(race) + " , " + race_info[0][Settings.series_name_index].ljust(15) + " - Multiple drivers finishing in " + str(fin) + ": " + ', '.join(driver_aux) + "\n" if isinstance(driver_aux,np.ndarray) else driver_aux + "\n")
                        #print("   Multiple drivers finishing in " + str(fin) + ":")
                        #for driver_fin in race_info[np.where(race_info[:,10]==fin)[0],Settings.driver_name_index]:
                        #    print("      " + str(driver_fin))
                    if fin not in race_info[:,Settings.fin_pos_index]:
                        found=True
                        if len(np.where(race_info[:,Settings.fin_pos_index]==fin-1)[0])>0:
                            prev=race_info[np.where(race_info[:,Settings.fin_pos_index]==fin-1)[0][0],Settings.driver_name_index]
                        else:
                            prev='N/A'
                        if len(np.where(race_info[:, Settings.fin_pos_index] == fin + 1)[0]) > 0:
                            next=race_info[np.where(race_info[:,Settings.fin_pos_index]==fin+1)[0][0],Settings.driver_name_index]
                        else:
                            next='N/A'
                        if sys.platform != 'win32':
                            if Settings.error == False:
                                Settings.error = True
                                print('ERROR')
                            print(str(race) + " , " + race_info[0][Settings.series_name_index].ljust(15) + " - No driver finishing in " + str(fin).ljust(2) + "            " + str(fin-1).ljust(2) + ": " + prev.ljust(25) + " " + str(fin+1).ljust(2) + ": " + next.ljust(25) + "\n")
                        if modelQ:
                            with open('validation/finishing_incoherent.txt', 'a') as file:
                                file.write(str(race) + " , " + race_info[0][Settings.series_name_index].ljust(15) + " - No driver finishing in " + str(fin).ljust(2) + "            " + str(fin-1).ljust(2) + ": " + prev.ljust(25) + " " + str(fin+1).ljust(2) + ": " + next.ljust(25) + "\n")
                if found==False:
                    if sys.platform != 'win32':
                        if Settings.error == False:
                            Settings.error = True
                            print('ERROR')
                        print(str(race) + " , " + race_info[0][Settings.series_name_index] + " - UNKNOWN ERROR\n")
                    if modelQ:
                        with open('validation/finishing_incoherent.txt', 'a') as file:
                            file.write(str(race) + " , " + race_info[0][Settings.series_name_index] + " - UNKNOWN ERROR\n")

            if error:
                non_valid_races.append(race)
            else:
                classifications[np.where(classifications[:, Settings.race_id_index] == [race])[0], :] = race_info
                if Settings.model_type in ['AllSeries','AllType','AllSeriesMerge'] and modelQ:
                    if Settings.model_type=='AllType':
                        race_series=Settings.series_type[race_info[0, Settings.series_name_index]]
                    else:
                        race_series = race_info[0, Settings.series_name_index]
                        if Settings.model_type=='AllSeriesMerge':
                            if race_series in ['Indy Lights']:
                                race_series='IndyCar'
                            if race_series in ['IMSA SC','ELMS','ALMS']:
                                race_series='WEC'
                            if race_series in ['FIA F3','Formula E','GP3','GP2']:
                                race_series='FIA F2'
                            if race_series in ['WTCC']:
                                race_series='WTCR'
                            if race_series in ['Moto3']:
                                race_series='Moto2'
                    if race_series in series_count:
                        series_count[race_series]+=1
                        series_races[race_series].append(race)
                    else:
                        series_count[race_series] = 1
                        series_races[race_series] = [race]
        else:
            if sys.platform != 'win32':
                if Settings.error == False:
                    Settings.error = True
                    print('ERROR')
                print(str(race) + " , " + race_info[0][Settings.series_name_index] + " - UNKNOWN ERROR2 - Perhaps not enough drivers\n")
            unused_races.append(race)
    final_races=np.setdiff1d(races,unused_races)
    final_races=np.setdiff1d(final_races,non_valid_races)
    if modelQ:
        with open('validation/non_valid_races.txt', 'a') as file:
            for non_valid_race in non_valid_races:
                file.write(str(non_valid_race) + "\n")
    if modelQ:
        with open('validation/not_enough_drivers.txt', 'a') as file:
            for unused_race in unused_races:
                race_info = classifications[np.where(classifications[:, Settings.race_id_index] == [unused_race])[0], :]
                year = int(str(race_info[0][Settings.date_index])[0:4])
                if year<=year_max and year>=year_min and race_info[0,Settings.ignore_flag_index]==0:
                    file.write(str(unused_race) + " " + serie + "\n")

    num_runs={}
    for race in final_races:
        num_runs[race]=1

    if Settings.model_type in ['AllSeries','AllType','AllSeriesMerge'] and modelQ:
        max_races=max(series_count.values())
        for adjust_series in list(series_count.keys()):
            while sum([num_runs[race] for race in series_races[adjust_series]])+len(series_races[adjust_series])<=max_races:
                for race in series_races[adjust_series]:
                    num_runs[race] += 1
            while sum([num_runs[race] for race in series_races[adjust_series]]) < max_races:
                min_run=min([num_runs[i] for i in series_races[adjust_series]])
                [i for i in series_races[adjust_series] if num_runs[i] == min_run]
                num_runs[random.choice([i for i in series_races[adjust_series] if num_runs[i] == min_run])]+=1
            if modelQ:
                print(adjust_series + " - Max Runs: " + str(max([value for key,value in zip(num_runs.keys(),num_runs.values()) if key in series_races[adjust_series]])) + ", Min Runs: " + str(min([value for key,value in zip(num_runs.keys(),num_runs.values()) if key in series_races[adjust_series]])))

    for race in final_races:
        race_info = classifications[np.where(classifications[:, Settings.race_id_index] == [race])[0], :]
        max_ini = max(race_info[:, Settings.ini_pos_index])
        year = int(str(race_info[0][Settings.date_index])[0:4])
        race_info = race_info[race_info[:, Settings.ini_pos_index].argsort()]
        races_info[race] = race_info
        races_classified[race] = race_info[np.where(race_info[:, Settings.fin_pos_index] > 0)[0],
                                 Settings.ini_pos_index:Settings.fin_pos_index + 1]
        races_retired[race] = race_info[np.where(race_info[:, Settings.fin_pos_index] <= 0)[0], Settings.ini_pos_index]
        race_pairs = race_info[np.where(race_info[:, Settings.fin_pos_index] > 0)[0],
                     Settings.ini_pos_index:Settings.fin_pos_index + 1]
        race_pairs[:, 0] = [calc_percentile(driver_ini, max_ini) for driver_ini in race_pairs[:, 0]]
        for _ in range(num_runs[race]):
            retirement_dist.append([year, 1.0*len(np.where(race_info[:, Settings.fin_pos_index] <= 0)[0]) / len(race_info)])
            for pair in itertools.combinations(race_pairs, r=2):
                classified_pair_dist.append([pair[0][0], pair[1][0], 0 if 1.0*(pair[0][1] - pair[1][1]) / (pair[0][0] - pair[1][0]) < 0 else 1])
                classified_pair_dist.append([pair[1][0], pair[0][0], 0 if 1.0*(pair[0][1] - pair[1][1]) / (pair[0][0] - pair[1][0]) < 0 else 1])
                #Para fazer polinomios 4d:
                #classified_pair_dist.append([pair[0][0], pair[1][0],len(race_info), 0 if (pair[0][1] - pair[1][1]) / (pair[0][0] - pair[1][0]) < 0 else 1])
                #classified_pair_dist.append([pair[1][0], pair[0][0],len(race_info), 0 if (pair[0][1] - pair[1][1]) / (pair[0][0] - pair[1][0]) < 0 else 1])

            for driver_info in race_info:
                if driver_info[Settings.fin_pos_index] > 0:
                    classified_pos.append([driver_info[Settings.ini_pos_index], driver_info[Settings.fin_pos_index]])

    retirement_dist = np.array(retirement_dist, dtype=object)
    classified_pos = np.array(classified_pos)
    classified_pair_dist = np.array(classified_pair_dist)
    return final_races, retirement_dist, classified_pos, classified_pair_dist, races_info, races_classified, races_retired
