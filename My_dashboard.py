#!/usr/bin/env python
# coding: utf-8

# ## Covid19 Dashboard

# In[20]:


from IPython.display import clear_output
import ipywidgets as wdg
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from uk_covid19 import Cov19API


# In[21]:


get_ipython().run_line_magic('matplotlib', 'inline')
# make figures larger
plt.rcParams['figure.dpi'] = 100


# In[29]:


with open("testingdata.json", "rt") as INFILE:
    data=json.load(INFILE)


# In[30]:


datalist=data["data"]
dates=[dictionary["date"] for dictionary in datalist]
dates.sort()


# In[31]:


def parse_date(datestring):
    """Convert a date string into a pandas datetime object"""
    return pd.to_datetime(datestring, format="%Y-%m-%d")


# In[32]:


startdate=parse_date(dates[0])
enddate=parse_date(dates[-1])
index=pd.date_range(startdate, enddate, freq="D")
testdatadf=pd.DataFrame(index=index, columns=["newcases", "cumcases", "newpcr", "cumpcr"])


# In[33]:


for entry in datalist: #each entry is a dictionary with new and cum data for PCR and cases
    date=parse_date(entry["date"])
    for column in ["newcases", "cumcases", "newpcr", "cumpcr"]:
    #first check to make sure there is nothing in there in case data was duplicated
        if pd.isna(testdatadf.loc[date,column]):
            #replace all none with 0 in our data
            value=float(entry[column]) if entry[column]!=None else 0.0
            # .loc is how you access a specific location in the dataframe
            #put index,column in a single set of []
            testdatadf.loc[date, column]=value
                    
#fill in the holes with 0.0 to replace missing data
testdatadf.fillna(0.0, inplace=True)
print(testdatadf)


# To refresh the data from PHE press the button below.

# In[36]:


def access_api(button):
    #this code polls the API
    from uk_covid19 import Cov19API
    filters = [
    'areaType=nation',
    'areaName=England'
    ]


    # values here are the names of the PHE metrics
    structure = {
        "date": "date",
        "newcases": "newCasesBySpecimenDate", #new cases by Specimen date
        "cumcases": "cumCasesBySpecimenDate", #cumulative cases by specimen date
        "newpcr": "newCasesPCROnlyBySpecimenDate", #new cases by PCR by specimen date
        "cumpcr": "cumPCRTestsBySpecimenDate" #cumulative cases by PCR by specimen date
    }

    api = Cov19API(filters=filters, structure=structure)

    testingdata=api.get_json()
    apibutton.icon="check"
    apibuttotn.disabled=True
    
apibutton=wdg.Button(
    description="Refresh data",
    disabled=False,
    button_style="success",
    tooltip="Click to download current Public Health England data.",
    icon="download"
)

apibutton.on_click(access_api)

# this is an iPython function that generalises print for Jupyter Notebooks; we use it to 
# display the widgets
display(apibutton)


# ## Graph comparing number of Covid cases compared to number of PCR tests
# 
# This graph demonstrates the relationship between the number of new Covid 19 cases and the number of PCR tests. This graph also allows the user to compare the cumulative data versus the new data to compare trends in both.

# In[35]:


series=wdg.SelectMultiple(
    options=["newcases", "cumcases", "newpcr", "cumpcr"],
    value=["newcases", "cumcases", "newpcr", "cumpcr"],
    rows=4,
    description="Stats:",
    disabled=False
)

scale=wdg.RadioButtons(
    options=["linear", "log"],
    description="Scale:",
    disabled=False
)

controls=wdg.HBox([series, scale])

def testdata_graph(gcols, gscale):
    if gscale=="linear":
        logscale=False
    else:
        logscale=True
    ncols=len(gcols)
    if ncols>0:
        testdatadf[list(gcols)].plot(logy=logscale)
        plt.show()
    else:
        print("Click to select data for graph")
        print("(CTRL-Click to select more than one category)")

graph=wdg.interactive_output(testdata_graph, {"gcols": series, "gscale": scale})

display(controls, graph)


# In[ ]:




