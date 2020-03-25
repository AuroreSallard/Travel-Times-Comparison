import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def scatter(df, dic_mb, dic_gb, dic_mg, hour=0, congested=False):
    data = df.copy()
    
    if hour in [2,5,7,11,18]:
        data = data[data["departure_h"]== hour]
    elif hour != 0:
        return "Enter a valid departure time"
    
    if congested:
        m = data["matsim_congested"].values.tolist()
        b = data["bing_congested"].values.tolist()
        g = data["google_congested"].values.tolist()
    else:
        m = data["matsim_non_congested"].values.tolist()
        b = data["bing_non_congested"].values.tolist()
        
    rel_diff_mb = [(mv-bv)/bv * 100 for (mv, bv) in list(zip(m,b))]
    rel_diff_gb = [(bv-gv)/gv * 100 for (bv, gv) in list(zip(b,g))]
    rel_diff_mg = [(mv-gv)/gv * 100 for (mv, gv) in list(zip(m,g))]
    
    #if congested and hour==0:
    #    for k in range(len(rel_diff)):
    #        if abs(rel_diff[k]) > 25:
    #            large.append(data[data["trip_id"]==k]["dist_car"].values.tolist())
                
    print(str(hour) + ", congested = " + str(congested))
    print(np.mean(rel_diff_mb))
    print(np.mean(rel_diff_gb))
    print(np.mean(rel_diff_mg))
    
    if hour == 0:
        title = "All day, "
    elif hour != 18:
        title = str(hour) + " AM, "
    elif hour == 18:
        title = str(hour-12) + " PM, "
        
    if congested:
        title += "with congestion"
    else:
        title += "no congestion"
        
    dic_mb[title] = rel_diff_mb
    dic_gb[title] = rel_diff_gb
    dic_mg[title] = rel_diff_mg
    

filepath = "/home/asallard/Dokumente/Projects/Comparison Travel Times Bing Matsim/SP/1pct/Data/MatsimGoogleBing/"

matsim = pd.read_csv(filepath + "traveltimes_6sec.csv")
bing = pd.read_csv(filepath + "output_bing_5000.csv")
google = pd.read_csv(filepath + "google_1_2000.csv")

bing = bing[["trip_id", "travelDuration_car", "travelDurationTraffic_car", "departure_time", "dist_car"]]
google = google[["Tripnr", "Total_Time_WT_Traffic"]]
google.rename(columns={"Total_Time_WT_Traffic":"google_congested", "Tripnr":"trip_id"}, inplace=True)

matsim.rename(columns={"freespeed_travel_time": "matsim_non_congested", 
                       "congested_travel_time": "matsim_congested"}, inplace=True)

matsim["departure_time"] = [ 5 * (i % 4 == 0) + 7 * (i % 4 == 1) + 11 * (i%4 == 2)
                            + 18 * (i%4 == 3) for i in matsim["trip_id"].values.tolist()]

google["departure_time"] = [ 5 * (i % 4 == 0) + 7 * (i % 4 == 1) + 11 * (i%4 == 2)
                            + 18 * (i%4 == 3) for i in google["trip_id"].values.tolist()]

merged = pd.merge(bing, matsim, how="inner", on=["trip_id"])
merged.drop(columns=["departure_time_x"], inplace=True)
merged.rename(columns={"departure_time_y":"departure_h",
                       "travelDuration_car": "bing_non_congested",
                       "travelDurationTraffic_car": "bing_congested"}, inplace=True)

merged = pd.merge(merged, google, how='inner', on=["trip_id"])

## Clean data ##

matsim_false = merged.index[merged["matsim_non_congested"] > merged["matsim_congested"]].tolist()
matsim_false_index = merged.index.isin(matsim_false)
matsim_false_df = merged[matsim_false_index]
merged = merged[~matsim_false_index]

bing_false = merged.index[merged["bing_non_congested"] > merged["bing_congested"]].tolist()
bing_false_index = merged.index.isin(bing_false)
bing_false_df = merged[bing_false_index]
merged = merged[~bing_false_index]

## Global comparison
hours = [0,5,7,11,18]
booleans = len(hours) * [True]
#hours *= 2

param = list(zip(hours, booleans))

output_dic_mb = {}
output_dic_gb = {}
output_dic_mg = {}

for p in param:
    r = scatter(merged, output_dic_mb, output_dic_gb, output_dic_mg, hour=p[0], congested=p[1])
    
    
fig, ax = plt.subplots(3,1, figsize = (15,20), sharex = True, sharey = True)
ax[0].set_title("Comparison between MATSim and Bing.\n Relative Difference with Bing as a reference, in percentage points.")
ax[0].boxplot(output_dic_mb.values())
ax[0].set_xticklabels(output_dic_mb.keys())

ax[1].set_title("Comparison between Google and Bing.\n Relative Difference with Google as a reference, in percentage points.")
ax[1].boxplot(output_dic_gb.values())
ax[1].set_xticklabels(output_dic_gb.keys())

ax[2].set_title("Comparison between MATSim and Google.\n Relative Difference with Google as a reference, in percentage points.")
ax[2].boxplot(output_dic_mg.values())
ax[2].set_xticklabels(output_dic_mg.keys())

plt.xticks(rotation = 75)
#plt.yticks([10 * (-6 + k) for k in range(16)])

plt.savefig("/home/asallard/Bilder/comparison_bing_matsim_google_SP_6sec.png")


