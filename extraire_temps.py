#In[]:
# Selenium allows to control chrome programmatically
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

#beautifulsoup is used to parse the dom of the html page
import bs4 as BeautifulSoup

import time 
from random import uniform
import configparser
import numpy as np

import pandas as pd
import matplotlib.pyplot as plt
import os
#In[]:


chrome_options = Options()
#chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path = '.\\chromedriver.exe', chrome_options=chrome_options)

temps = []

nb = 10

longitudeDestination1 = 48.9361537
latitudeDestination1 = 2.2507129

longitudeDestination2 =48.7783875
latitudeDestination2 = 2.1803534

#In[]:
ctn = 0
for coordX in np.linspace(48.8, 48.9, nb):
    for coordY in np.linspace(2,2.26, nb):
        
        resultats = None
        url_journey1 = f"https://www.google.com/maps/dir/{coordX},{coordY}/@{longitudeDestination1},{latitudeDestination1},12z/data=!3m1!4b1!4m14!4m13!1m0!1m5!1m1!1s0x47e67bff078f6575:0x95df2619f9304bd7!2m2!1d2.1825421!2d48.778384!2m4!2b1!6e0!7e2!8j1570521600!3e0"
        url_journey2 = f'https://www.google.com/maps/dir/{coordX},{coordY}/@{longitudeDestination2},{latitudeDestination2},14z/data=!3m1!4b1!4m14!4m13!1m0!1m5!1m1!1s0x47e665df0cb0b919:0x5f513cdf2fe6d39d!2m2!1d2.2572779!2d48.9368666!2m4!2b1!6e0!7e2!8j1570521600!3e0'

        driver.get(url_journey1)

        while resultats == None :
            soupe = BeautifulSoup.BeautifulSoup(driver.page_source, "lxml")
            soupe.select("section-directions-trip-numbers")
            resultats = soupe.find('div',attrs={"class":u"section-directions-trip-numbers"})
        temps_marie = resultats.find_all("span")[2]

        resultats = None
        
        driver.get(url_journey2)
        while resultats == None :
            soupe = BeautifulSoup.BeautifulSoup(driver.page_source, "lxml")
            #soupe.select("section-directions-trip-numbers")
            resultats = soupe.find('div',attrs={"class":u"section-directions-trip-numbers"})
        temps_guillaume = resultats.find_all("span")[2]
        ctn += 1
        print(ctn/(nb*nb)*100)
        temps.append([coordX, coordY, temps_marie.text, temps_guillaume.text, f'https://www.google.com/maps/place/{coordX},{coordY}'])

print(temps)

#%%
def analyse_time(time):
    """
    Analyse the time given by google maps, splits the lower and higher estimate and converts them to minutes
    """
    tlow = time.split(" - ")[0].replace("\xa0", " ")
    thigh = time.split(" - ")[1].replace("\xa0", " ")

    if ("min" not in tlow) and ("h" not in tlow):
        #example : 26 
        tlow = int(tlow.replace(" ", ""))
    elif "h" not in tlow :
        # example 26 min 
        tlow = tlow.replace("min", "")
        tlow = int(tlow.replace(" ", ""))
    else :
        if "min" in tlow:
            #example 1h 26min
            tlow = tlow.split("h")
            tlow = 60*int(tlow[0].replace(" ", "")) + int(tlow[1].replace("min", "").replace(" ", ""))
        else:
            #example 1h
            tlow = 60*int(tlow.replace("h", ""))
    
    if "h" not in thigh :
        thigh = thigh.replace("min", "")
        thigh = int(thigh.replace(" ", ""))
    else :
        if "min" in thigh:
            thigh = thigh.split("h")
            thigh = 60*int(thigh[0].replace(" ", "")) + int(thigh[1].replace("min", "").replace(" ", ""))
        else:
            thigh = 60*int(thigh.replace("h", ""))

    

    return (tlow, thigh)

#%%
df = []
for t in temps:
    lat = t[0]
    lon = t[1]
    t1 = analyse_time(t[2])
    t2 = analyse_time(t[3])
    geomlow = np.sqrt(t1[0]*t2[0])
    geomhigh = np.sqrt(t1[1]*t2[1])
    df.append([lat, lon, geomlow, geomhigh, t1[0], t1[1], t2[0], t2[1]])
    print([lat, lon, geomlow, geomhigh, t1[0], t1[1], t2[0], t2[1]])

    

#%%

traveltime = pd.DataFrame(df, columns = ["latitude", "longitude", "geometric mean low", "geometric mean high", "time low 1", "time high 1", "time low 2", "time high 2"])
traveltime = traveltime.sort_values("geometric mean low")
traveltime = traveltime.reset_index()
traveltime.to_csv("extraction.csv", index=False)
#traveltime.sort_values("geometric mean low")
traveltime

#%%
traveltime = pd.read_csv(".\\extraction.csv")
traveltime
#%%
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy

import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

#%%
plt.rcParams['figure.figsize'] = 20, 12
# Create a Stamen terrain background instance.
stamen_terrain = cimgt.Stamen('terrain-background')
stamen_terrain = cimgt.GoogleTiles()
fig = plt.figure()
# Create a GeoAxes in the tile's projection.
ax = fig.add_subplot(1, 1, 1, projection=stamen_terrain.crs)
# Limit the extent of the map to a small longitude/latitude range.
ax.set_extent([1.9,2.3, 48.7, 49], crs=ccrs.Geodetic())
# Add the Stamen data at zoom level 10.
ax.add_image(stamen_terrain, 10)



for i, point in traveltime.sort_values("time low 1").iterrows():
    if i < 10 :
        ax.plot( point.longitude, point.latitude, marker='o', 
            c ='red', markersize=point["time low 2"],
            alpha=1, transform=ccrs.Geodetic())

for i, point in traveltime.sort_values("time low 2").iterrows():
    if i < 10 :
        ax.plot( point.longitude, point.latitude, marker='o', 
            c ='blue', markersize=point["time low 1"],
            alpha=1, transform=ccrs.Geodetic())
        
        
# Add a marker for destination 1
ax.plot( latitudeDestination1, longitudeDestination1, marker='*', 
            c ='green', markersize=25,
            alpha=1, transform=ccrs.Geodetic())
# Add a marker for destination 2
ax.plot( latitudeDestination2, longitudeDestination2, marker='*', 
            c ='orange', markersize=25,
            alpha=1, transform=ccrs.Geodetic())        

geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
text_transform = offset_copy(geodetic_transform, units='dots', x=-25)

plt.show()



#%%


#%%
