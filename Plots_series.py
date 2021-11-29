import matplotlib.pyplot as plt
import numpy as np
import Settings
import os
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

def draw(serie,entropy_list):
    if not os.path.exists("Plots/" + Settings.model_type + "/" + serie):
        os.mkdir("Plots/" + Settings.model_type + "/" + serie)

    entropy_mean_list=[]
    entropy_array=np.array(entropy_list,dtype=object)
    entropy_array=entropy_array[np.where(entropy_array[:,Settings.entropy_series_name_index]==serie)]
    entropy_array=entropy_array[entropy_array[:,Settings.entropy_calcs_index].argsort(),:]
    entropy_array[:,Settings.entropy_race_id_index]=[str(race[Settings.entropy_race_id_index])[0:4]+' '+race[Settings.entropy_race_name_index] for race in entropy_array]
    entropy_mean_list.append([serie,np.mean(entropy_array[:,Settings.entropy_calcs_index])])

    entropy_bars=[]
    for i in range(1,11):
        entropy_bars.append(((i-1 <= entropy_array[:,Settings.entropy_calcs_index]) & (entropy_array[:,Settings.entropy_calcs_index] < i)).sum())
    entropy_bars.append((entropy_array[:,Settings.entropy_calcs_index]>=10).sum())
    plt.bar(x=range(11), height=entropy_bars, width=1, align='edge', edgecolor='k', linewidth=0.5,tick_label=[str(i) for i in range(11)])
    for i in range(0,11):
        if entropy_bars[i]/max(entropy_bars)>0.06:
            plt.text(i+0.45,entropy_bars[i]-max(entropy_bars)*0.05, " "+str(entropy_bars[i]), color='white', ha='center', fontweight='bold')
        else:
            plt.text(i + 0.45, entropy_bars[i] + max(entropy_bars)*0.01, " " + str(entropy_bars[i]), color='black', ha='center', fontweight='bold')
    plt.title(serie + " Entropy Histogram")
    plt.xlabel('Entropy')
    plt.ylabel('# of Races')
    plt.xlim([0, 11])
    plt.savefig("Plots/" + Settings.model_type + "/" + serie + "/Entropy_Histogram_" + serie + ".png")
    plt.show()

    if len(entropy_array)<=25:
        plt.barh(np.arange(21) + .5, entropy_array[:, Settings.entropy_calcs_index],align='center')
        plt.yticks(np.arange(21) + .5, entropy_array[:, Settings.entropy_race_id_index])
    else:
        plt.barh(np.arange(21)+.5,np.concatenate((entropy_array[0:10,Settings.entropy_calcs_index],np.zeros(1),entropy_array[-10:,Settings.entropy_calcs_index])),align='center')
        plt.yticks(np.arange(21)+.5,np.concatenate((entropy_array[0:10,Settings.entropy_race_id_index],np.array(['...']),entropy_array[-10:,Settings.entropy_race_id_index])))
    plt.xlabel('Entropy')
    plt.title(serie + " Races with most/least entropy")
    plt.xlim([0,10])
    #plt.xlim(left=0)
    plt.savefig("Plots/" + Settings.model_type + "/" + serie + "/Races_" + serie + ".png")
    plt.show()

    # years=np.unique(entropy_array[:,Settings.entropy_year])
    # years_list=[]
    # for year in years:
    #     entropy_values=entropy_array[np.where(entropy_array[:,Settings.entropy_year]==year),Settings.entropy_calcs_index][0]
    #     entropy_mean=np.mean(entropy_values)
    #     years_list.append([year,entropy_mean])
    # years_array=np.array(years_list,dtype=object)
    # plt.figure(figsize=(10, 15))
    # plt.barh(np.arange(len(years_array)) + .5, years_array[:, 1], align='center')
    # plt.yticks(np.arange(len(years_array)) + .5, years_array[:, 0])
    # plt.xlabel('Entropy')
    # plt.title(serie + " Yearly Average Entropy")
    # plt.xlim([0,10])
    # plt.savefig("Plots/" + Settings.model_type + "/" + serie + "/Years_" + serie + ".jpg")
    # plt.show()

    # decades=np.unique(entropy_array[:,Settings.entropy_decade])
    # decades_list=[]
    # for decade in decades:
    #     entropy_values=entropy_array[np.where(entropy_array[:,Settings.entropy_decade]==decade),Settings.entropy_calcs_index][0]
    #     entropy_mean=np.mean(entropy_values)
    #     decades_list.append([decade,entropy_mean])
    # decades_array=np.array(decades_list,dtype=object)
    # plt.barh(np.arange(len(decades_array)) + .5, decades_array[:, 1], align='center')
    # plt.yticks(np.arange(len(decades_array)) + .5, decades_array[:, 0])
    # plt.xlabel('Entropy')
    # plt.title(serie + " Decade Average Entropy")
    # plt.xlim([0,10])
    # plt.savefig("Plots/" + Settings.model_type + "/" + serie + "/Decades_" + serie + ".jpg")
    # plt.show()

    # circuit_names=np.unique(entropy_array[:,Settings.entropy_circuit_name_index])
    # circuit_list=[]
    # for circuit in circuit_names:
    #     entropy_values=entropy_array[np.where(entropy_array[:,Settings.entropy_circuit_name_index]==circuit),Settings.entropy_calcs_index][0]
    #     entropy_mean=np.mean(entropy_values)
    #     num_races=len(entropy_values)
    #     if num_races>=5:
    #         circuit_list.append([serie,circuit,entropy_mean,num_races])
    # if len(circuit_list)>0:
    #     circuit_array=np.array(circuit_list,dtype=object)
    #     circuit_array=circuit_array[circuit_array[:,2].argsort(),:]
    #     i=0
    #     if len(circuit_array)<=25:
    #         plt.barh(np.arange(len(circuit_array)) + .5, circuit_array[:, 2], align='center')
    #         plt.yticks(np.arange(len(circuit_array)) + .5, circuit_array[:, 1])
    #         for entropy, num_races in circuit_array[:, 2:]:
    #             plt.text(entropy, i+0.5, " " + str(num_races), color='red', va='center')
    #             i += 1
    #     else:
    #         plt.barh(np.arange(21) + .5, np.concatenate((circuit_array[0:10, 2],np.zeros(1),circuit_array[-10:, 2])), align='center')
    #         plt.yticks(np.arange(21) + .5, np.concatenate((circuit_array[0:10, 1], np.array(['...']), circuit_array[-10:, 1])))
    #         for entropy,num_races in np.concatenate((circuit_array[0:10,2:],[[0,0]],circuit_array[-10:,2:])):
    #             if num_races>0:
    #                 plt.text(entropy, i+0.5, " "+str(num_races), color='red', va='center')
    #             i+=1
    #
    #     plt.xlabel('Entropy')
    #     plt.title(serie + " Circuits with most/least average entropy")
    #     plt.xlim([0,10])
    #     plt.savefig("Plots/" + Settings.model_type + "/" + serie + "/Circuits_" + serie + ".jpg")
    #     plt.show()