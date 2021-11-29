import numpy as np
from scipy.stats import norm, lognorm
import Settings
import Load_data
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sys import platform
if platform=='win32':
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib import rcParams
    rcParams.update({'figure.autolayout': True})

def calc_percentile(pos, max_pos):
    return 100 * (pos - 1) / (max_pos - 1)

def placing_pair(model,driver1_ini,driver1_fin,driver2_ini,driver2_fin,num_drivers):
    if (driver1_ini-driver2_ini)/(driver1_fin-driver2_fin)>0:
        return 0
    else:
        prob_nochange = (model.calc_pair(driver1_ini, driver2_ini) - model.min_pair) / (model.max_pair - model.min_pair)
        #para polinomios 4d
        #prob_nochange = (model.calc_pair(driver1_ini, driver2_ini, num_drivers) - model.min_pair) / (model.max_pair - model.min_pair)
        return prob_nochange

def calc_entropies(model, race_info, race_classified,race_retired):
    max_ini=race_info[-1,Settings.ini_pos_index]
    year = int(str(race_info[0][Settings.date_index])[0:4])
    if year>Settings.model_year:
        year=Settings.model_year
    num_ret = np.sum(race_info[:, Settings.fin_pos_index] <= 0)
    perc_ret=num_ret/max_ini
    mean_ret=model.ret_params[max(year,model.min_year)][0]
    std_ret=model.ret_params[max(year,model.min_year)][1]
    p_ret=0.5+0.2*max(0,((perc_ret-mean_ret)/std_ret))**1.2

    entropy_classified = 0
    race_classified[:, 0] = [calc_percentile(driver_ini, max_ini) for driver_ini in race_classified[:, 0]]
    num_classified=len(race_classified)
    num_retired=len(race_retired)

    for driver in race_classified:
        entropy_driver=0
        for opponent in race_classified:
            if driver[0]!=opponent[0]:
                try:
                    entropy_driver+=placing_pair(model,driver[0],driver[1],opponent[0],opponent[1],num_classified+num_retired)
                except:
                    print(race_info[0,2])
                    entropy_driver += placing_pair(model, driver[0], driver[1], opponent[0], opponent[1],num_classified+num_retired)
        entropy_classified+=entropy_driver/(num_classified-1)
    entropy_retired=0
    if num_retired>0:
        race_retired = [calc_percentile(driver_ini, max_ini) for driver_ini in race_retired]
        #entropy_retired=sum(p_ret * (-1 / 120 * np.array(race_retired) + 1))
        if race_info[0,Settings.series_name_index] in Settings.series_type:
            ret_first_vs_last=Settings.ret_first_vs_last[Settings.series_type[race_info[0,Settings.series_name_index]]]
        else:
            ret_first_vs_last=Settings.ret_first_vs_last['SingleSeater']
        entropy_retired=sum(p_ret * (-ret_first_vs_last * np.array(race_retired) + 1+50*ret_first_vs_last-50/120))
    return entropy_classified, num_classified, entropy_retired, num_retired

def calc_entropy(model, race_info, race_classified,race_retired):
    entropy_classified, num_classified, entropy_retired, num_retired=calc_entropies(model,race_info, race_classified,race_retired)
    return entropy_formula(model,entropy_classified, num_classified, entropy_retired, num_retired)


def entropy_formula(model, entropy_classified,num_classified,entropy_retired,num_retired):
    entropy = (model.classified_vs_retired * entropy_classified + entropy_retired) / (num_classified + num_retired)
    if model.shape+model.loc+model.scale!=0:
        #entropy = round(Settings.entropy_scale*lognorm.cdf(entropy,model.shape,loc=model.loc,scale=model.scale),1)
        entropy = round(1.0*Settings.entropy_scale*sum(entropy>model.entropy_list)/len(model.entropy_list),1)
        #only define 0 entropy for races that literally nothing happened, otherwise at least 0.1
        if entropy==0 and entropy_classified + num_retired>0:
            entropy=0.1
        #entropy = round(min(float(10),Settings.entropy_scale*np.log2(1 + (model.classified_vs_retired * entropy_classified + entropy_retired) / (num_classified + num_retired)/(model.max_entropy))),1)
    return entropy

class Model:
    def __init__(self, races_info, races_classified, races_retired, retirement_dist, ret_params, min_year, calc_pairs, poly, model_name):
        self.model_name=model_name
        self.ret_params = ret_params
        #FLCNOself.races_info = races_info
        #FLCNOself.races_classified = races_classified
        #FLCNOself.races_retired = races_retired
        #FLCNOself.retirement_dist = retirement_dist
        self.calc_pairs = calc_pairs
        self.min_pair = 10e100
        self.max_pair = -10e100
        self.poly = poly
        self.shape = 0
        self.loc = 0
        self.scale = 0
        self.classified_vs_retired = 1
        #FLCNOself.pair_hist = {}
        self.decimal_places=3
        self.min_year=min_year
        for driver1 in [0,100]:
            for driver2 in np.linspace(0,100,501):
                for num_drivers in range(8,50):
                    if driver1!=driver2:
                        new_pair = self.calc_pair(driver1,driver2)
                        #para polinomios 4d
                        #new_pair = self.calc_pair(driver1,driver2,num_drivers)
                        if new_pair<self.min_pair:
                            self.min_pair=new_pair
                        if new_pair>self.max_pair:
                            self.max_pair=new_pair

    def set_entropy_list(self,entropy_list):
        self.entropy_list=entropy_list

    def set_entropy_scale(self,shape,loc,scale):
        self.shape=shape
        self.loc=loc
        self.scale=scale

    def set_classified_vs_retired(self, classified_vs_retired):
        self.classified_vs_retired=classified_vs_retired

    def pair(self,driver1,driver2):
        [driver1,driver2]=sorted([driver1,driver2])
        driver1=round(driver1,self.decimal_places)
        driver2=round(driver2,self.decimal_places)
        return driver1,driver2

    def calc_pair(self,driver1,driver2):
        driver1,driver2=self.pair(driver1,driver2)
        #FLCNOif (driver1,driver2) not in self.pair_hist:
        #FLCNOself.pair_hist[driver1,driver2]=self.calc_pairs.predict(self.poly.fit_transform([[driver1, driver2]]))[0]
        #FLCNOreturn self.pair_hist[driver1,driver2]
        return self.calc_pairs.predict(self.poly.fit_transform([[driver1, driver2]]))[0]
    # Para polinomios 4d
    # def calc_pair(self, driver1, driver2, num_drivers):
    #     driver1, driver2 = self.pair(driver1, driver2)
    #     if (driver1, driver2, num_drivers) not in self.pair_hist:
    #         self.pair_hist[driver1, driver2, num_drivers] = \
    #         self.calc_pairs.predict(self.poly.fit_transform([[driver1, driver2, num_drivers]]))[0]
    #     return self.pair_hist[driver1, driver2, num_drivers]

def create(model_name):
    races, retirement_dist, classified_pos, classified_pair_dist, races_info, races_classified, races_retired = Load_data.load(model_name,True)

    poly = PolynomialFeatures(degree=3)
    X_t = poly.fit_transform(classified_pair_dist[:,0:2])
    calc_pairs = LinearRegression().fit(X_t,classified_pair_dist[:,2])
    #Para fazer polinomios 4d:
    # X_t = poly.fit_transform(classified_pair_dist[:,0:3])
    # calc_pairs = LinearRegression().fit(X_t,classified_pair_dist[:,3])
    ret_params = dict()
    min_year=3000
    for year_ret in np.unique(retirement_dist[:, 0]):
        min_year=min(year_ret,min_year)
        ret_data=retirement_dist[np.where(np.logical_and(abs(retirement_dist[:, 0] - year_ret) <= 4,retirement_dist[:, 0] <= Settings.model_year))[0]][:, 1]
        ret_mean=np.mean(ret_data)
        ret_data_low=list(ret_data[np.where(ret_data<=ret_mean)])+list(ret_data[np.where(ret_data <= ret_mean)] + 2 * (ret_mean - ret_data[np.where(ret_data <= ret_mean)]))
        ret_data_high=list(ret_data[np.where(ret_data>ret_mean)])+list(ret_data[np.where(ret_data > ret_mean)] - 2 * (ret_data[np.where(ret_data > ret_mean)] - ret_mean))
        #FLC In endurance, the last 5 years (2017+) have literally 0 retirements, which makes the fit not work, so I'm using last year
        #falar com o pai a ver se faz sentido nao haver retirements e o q fazer sobre isso
        if np.mean(ret_data)==0:
            ret_params[year_ret] = ret_params[year_ret-1]
        else:
            ret_params[year_ret] = (np.mean(ret_data),norm.fit(ret_data_high)[1],norm.fit(ret_data_low)[1])

    if platform == 'win32':
        X=[]
        Y=[]
        Y_min=[]
        Y_max=[]
        for param in ret_params:
            X.append(param)
            Y.append(ret_params[param][0])
            Y_min.append(ret_params[param][0]-ret_params[param][2])
            Y_max.append(ret_params[param][0]+ret_params[param][1])

        plt.plot(X, Y, 'k-',linewidth=3)
        plt.plot(X, Y_min, 'c-')
        plt.plot(X, Y_max, 'c-')
        plt.fill_between(X, Y_min, Y_max, alpha=0.15,color='red')
        plt.ylim([0,1])
        plt.xlabel('Year')
        plt.ylabel('Retirement probability')
        plt.title(model_name + " Retirement % Over the Years")
        plt.legend(['Mean','1 Std Dev'])
        plt.savefig("Plots/" + Settings.model_type + "/RetProb_" + model_name + ".png")
        plt.show()

    model=Model(races_info, races_classified, races_retired, retirement_dist, ret_params, min_year, calc_pairs, poly, model_name)

    # X = np.arange(0, 101, 1)
    # Y = np.arange(0, 101, 1)
    # X, Y = np.meshgrid(X, Y)
    # Z = np.zeros(X.shape)
    # for x_i in range(X.shape[0]):
    #     for y_i in range(X.shape[1]):
    #         Z[x_i,y_i]=model.calc_pair(X[x_i,y_i],Y[x_i,y_i])
    # fig = plt.figure()
    # #ax = fig.gca(projection='3d')
    # ax = fig.add_subplot(projection='3d')
    # ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,linewidth=0)
    # plt.title(model_name + " Likelihood of Switching Relative Position", fontsize=12, pad=20)
    # ax.set_xlabel('Driver 1 starting pos.', fontsize=10, labelpad=10)
    # ax.set_ylabel('Driver 2 starting pos.', fontsize=10, labelpad=10)
    # ax.set_zlabel('Unlikelihood', fontsize=10, labelpad=10)
    # plt.savefig("Plots/" + Settings.model_type + "/Switching_Unlikelihood_" + model_name + ".jpg")
    # plt.show()

    total_entropy_classified=0
    total_classified=0
    total_entropy_retired=0
    total_retired=0
    entropies_list=[]
    for race in races:
        entropy_1,num_1,entropy_2,num_2=calc_entropies(model,races_info[race],races_classified[race],races_retired[race])
        total_entropy_classified+=entropy_1
        total_entropy_retired+=entropy_2
        total_classified+=num_1
        total_retired+=num_2
        entropies_list.append([entropy_1,num_1,entropy_2,num_2])


    model.set_classified_vs_retired((total_entropy_retired/total_retired)/(total_entropy_classified/total_classified))

    # max_entropy = 0
    # for entropy in entropies_list:
    #     max_entropy = max(max_entropy, entropy_formula(model, entropy[0], entropy[1], entropy[2], entropy[3]))

    entropy_list = []
    min_ent=10
    min_race=None
    for race, entropy in zip(races, entropies_list):
        final_ent=entropy_formula(model, entropy[0], entropy[1], entropy[2], entropy[3])
        entropy_list.append(final_ent)
        if final_ent<min_ent:
            min_race=race
            min_ent=final_ent

    #This is here to solve the problem that the minimum entropy races start with 0.1 even though it should be like 0.3
    for i in range(350):
        entropy_list.append(0.035425021057640976*i/350)
    shape, loc, scale = lognorm.fit(entropy_list)
    if platform == 'win32':
        plt.hist(entropy_list,bins=50,density=True)
        plt.plot(np.arange(0,2,0.01),lognorm.pdf(np.arange(0,2,0.01),shape,loc=loc,scale=scale),'r-',lw=2)
        plt.xlim([0,1.5])
        plt.title(model_name + " - entropy distribution before scaling")
        plt.savefig("Plots/" + Settings.model_type + "/" + model_name + "_EntropyDist.png")
        plt.show()
    model.set_entropy_list(entropy_list)
    model.set_entropy_scale(shape,loc,scale)
    return model

