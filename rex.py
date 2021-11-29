import sys
if sys.platform=='win32':
    import Plots_all
    import Plots_series
import numpy as np
import time
import Settings
import Load_data
import Model
import pickle
import os
if sys.platform == 'win32':
    rerun_models=True
    prefix=''
else:
    #in the server, the data is inside the folder 'rex'
    prefix='rex/'
    rerun_models=False
    #the first argument is the file with the data to run
    Settings.data_file=sys.argv[1]
rerun_races=True
ini_time=time.time()

if sys.platform=='win32':
    for file in ['validation/starting_missing.txt','validation/starting_incoherent.txt','validation/finishing_incoherent.txt','validation/non_valid_races.txt','validation/not_enough_drivers.txt']:
        if os.path.exists(file):
            os.remove(file)

#Finds all models that needs to be created, based on the series in the settings file
if Settings.model_type=='All':
    models=['All']
elif Settings.model_type == 'AllType':
    models = ['AllType']
elif Settings.model_type == 'AllSeries':
    models = ['AllSeries']
elif Settings.model_type == 'AllSeriesMerge':
    models = ['AllSeriesMerge']

if sys.platform=='win32':
    if not os.path.exists("Plots/" + Settings.model_type):
        os.mkdir("Plots/" + Settings.model_type)
    if not os.path.exists("series_values/" + Settings.model_type):
        os.mkdir("series_values/" + Settings.model_type)
    if not os.path.exists("EntropyResults/" + Settings.model_type):
        os.mkdir("EntropyResults/" + Settings.model_type)

#Creates each individual model and saves it
for model_name in models:
    filename = prefix+ 'models/' + model_name + '.pickle'
    start_time=time.time()
    if rerun_models or not os.path.exists(filename):
        model=Model.create(model_name)
        with open(filename, 'wb') as f:
            pickle.dump([model], f)
        if sys.platform == 'win32':
            print("Model: " + model_name + " created. Time elapsed: " + str(round(time.time()-start_time,2)) + "s")

entropy_avg_series=[]
entropy_avg_type={}
for type in Settings.types:
    entropy_avg_type[type]=[]
total_races=[]
classified_pos_total=np.empty([0, 2])
entropy_list_all=[]

_, series = Load_data.get_data()

#Goes through each series
for serie in series:
    start_time=time.time()
    filename_entropy = 'series_values/' + Settings.model_type + '/' + serie + '.pickle'
    if os.path.exists(filename_entropy) and not rerun_races:
        with open(filename_entropy, 'rb') as f:
            [entropy_list] = pickle.load(f)
    else:
        entropy_list = []

    if Settings.model_type == 'All':
        filename = 'models/All.pickle'
    elif Settings.model_type == 'AllType':
        filename = 'models/AllType.pickle'
    elif Settings.model_type == 'AllSeries':
        filename = 'models/AllSeries.pickle'
    elif Settings.model_type == 'AllSeriesMerge':
        filename = 'models/AllSeriesMerge.pickle'
    with open(prefix+filename, 'rb') as f:
        [model] = pickle.load(f)
    races, retirement_dist, classified_pos, classified_pair_dist, races_info, races_classified, races_retired =Load_data.load(serie)
    if len(races)>0:
        classified_pos_total=np.concatenate((classified_pos_total,classified_pos))

        race_list=[race[Settings.entropy_race_id_index] for race in entropy_list]
        entropy_total=sum([race[Settings.entropy_calcs_index] for race in entropy_list])
        new_races=0
        for race in list(np.setdiff1d(races,race_list)):
            race_info = races_info[race]
            race_id=race_info[0][Settings.race_id_index]
            series_name=race_info[0][Settings.series_name_index]
            race_name=race_info[0][Settings.race_name_index]
            circuit_id=race_info[0][Settings.circuit_id_index]
            circuit_name=race_info[0][Settings.circuit_name_index]
            year=int(str(race_info[0][Settings.date_index])[0:4])
            decade=int(str(year)[0:3]+'0')
            entropy=Model.calc_entropy(model, race_info, races_classified[race], races_retired[race])
            entropy_total+=entropy
            entropy_list.append([series_name,race_id,race_name,circuit_id,circuit_name,entropy,year,decade])
            if serie in Settings.series_type:
                entropy_avg_type[Settings.series_type[serie]].append(entropy)
            new_races=1
        if sys.platform == 'win32':
            Plots_series.draw(serie,entropy_list)
        entropy_avg_series.append([serie,entropy_total/len(races)])
        total_races.append([serie,len(races)])
        num_max_entropy=[race[Settings.entropy_calcs_index]>=10 for race in entropy_list].count(1)
        if new_races:

            if sys.platform == 'win32':
                with open('EntropyResults/' + Settings.model_type + '/' + serie + '_entropy.txt', 'w') as file:
                    for race_entropy in entropy_list:
                        file.write(str(race_entropy[0]) + ";" + str(race_entropy[1]) + ";" + str(race_entropy[2]) + ";" + str(race_entropy[3]) +  ";" + str(race_entropy[4]) + ";" + str(race_entropy[5]) + "\n")
                with open(filename_entropy, 'wb') as f:
                    pickle.dump([entropy_list], f)
            else:
                if Settings.error==False:
                    print('REXOK')
                    for race_entropy in entropy_list:
                        print(int(race_entropy[5]*10))
        entropy_list_all += entropy_list
        if sys.platform == 'win32':
            print("Series: " + serie + " analyzed. Time elapsed: " + str(round(time.time()-start_time,2)) + "s, number of races: " + str(len(entropy_list)) + ", number of races with max entropy: " + str(num_max_entropy))

if sys.platform=='win32' and len(entropy_list_all)>0:
    Plots_all.draw(entropy_list_all,np.array(entropy_avg_series,dtype=object),np.array([[key,np.mean(values)] for key, values in zip(entropy_avg_type.keys(),entropy_avg_type.values())],dtype=object),classified_pos_total, np.array(total_races,dtype=object))

if sys.platform == 'win32':
    print("Total Time Elapsed: " + str(time.time()-ini_time))
    print('')
