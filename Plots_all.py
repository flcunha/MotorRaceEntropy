import matplotlib.pyplot as plt
import numpy as np
import Settings
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

def draw(entropy_list_all,entropy_list_series,entropy_list_type,classified_pos, total_races):

    entropy_array=np.array(entropy_list_all,dtype=object)
    entropy_array=entropy_array[entropy_array[:,Settings.entropy_calcs_index].argsort(),:]
    entropy_array[:,Settings.entropy_race_id_index]=[str(race[Settings.entropy_race_id_index])[0:4]+' '+race[Settings.entropy_race_name_index] for race in entropy_array]

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
    plt.title("All Entropy Histogram")
    plt.xlabel('Entropy')
    plt.ylabel('# of Races')
    plt.xlim([0, 11])
    plt.savefig("Plots/" + Settings.model_type + "/Entropy_Histogram_All.png")
    plt.show()

    plt.barh(np.arange(len(entropy_list_series)) + .5, entropy_list_series[:, 1], align='center')
    plt.yticks(np.arange(len(entropy_list_series)) + .5, entropy_list_series[:, 0])
    plt.xlabel('Entropy')
    plt.title("Average Series Entropy")
    plt.xlim([0, 10])
    plt.savefig("Plots/" + Settings.model_type + "/Series_comp.png")
    plt.show()

    plt.barh(np.arange(len(entropy_list_type)) + .5, entropy_list_type[:, 1], align='center')
    plt.yticks(np.arange(len(entropy_list_type)) + .5, entropy_list_type[:, 0])
    plt.xlabel('Entropy')
    plt.title("Average Type Entropy")
    plt.xlim([0, 10])
    plt.savefig("Plots/" + Settings.model_type + "/Types_comp.png")
    plt.show()

    plt.barh(np.arange(len(total_races)) + .5, total_races[:, 1], align='center')
    plt.yticks(np.arange(len(total_races)) + .5, total_races[:, 0])
    plt.xlabel('Number of Races')
    plt.title("Total Races per Series")
    plt.savefig("Plots/" + Settings.model_type + "/Races_per_Series.png")
    plt.show()


    x=classified_pos[:,0]
    y=classified_pos[:,1]
    xy,counts=np.unique(classified_pos,axis=0,return_counts=True)
    x=xy[:,0]
    y=xy[:,1]
    plt.scatter(x,y, marker='o', c='b', s=150*counts/max(counts), label='the data')
    plt.plot(range(0, int(1 + max(x))), c='r', linewidth=2)
    plt.savefig("Plots/" + Settings.model_type + "/Scatter_ini_vs_fin.png")
    plt.show()
