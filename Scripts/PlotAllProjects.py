# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%

# %%

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
from collections import OrderedDict
from os.path import join as PJ
from pathlib import Path

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

dataPath = Path("../Data")

disciplineData = pd.read_csv(dataPath/"ScienceMapDisciplineData.tsv",sep="\t")
subDiscipline2DisciplineData = pd.read_csv(dataPath/"ScienceMapSubDisciplineToDiscipline.tsv",sep="\t")

subDiscipline2Discipline = OrderedDict(zip(subDiscipline2DisciplineData["subd_id"],subDiscipline2DisciplineData["disc_id"]))
discipline2Name = OrderedDict(zip(disciplineData["disc_id"],disciplineData["disc_name"]))
discipline2Color = OrderedDict(zip(disciplineData["disc_id"],disciplineData["color"]))



#Enables smoothing of the non cumulative curves
useSmoothing = True;
smoothingWindow=1


# %%
dataFiles = {}
dataFiles["Authors"] = ["BioMed_AuthorsData.json","Physics_AuthorsData.json"];
dataFiles["Total Authors"] = ["BioMed_TotalAuthorsData.json","Physics_TotalAuthorsData.json"]
dataFiles["Citations"] = ["BioMed_CitationsData.json","Physics_CitationsData.json"]
# dataFiles["Total Citations"] = ["BioMed_CumulativeCitationsData.json","Physics_CumulativeCitationsData.json"]
dataFiles["Publications"] = ["BioMed_PublicationsData.json","Physics_PublicationsData.json"]
dataFiles["Total Affiliations"] = ["BioMed_TotalAffiliationsData.json","Physics_TotalAffiliationsData.json"]
dataFiles["Affiliations"] = ["BioMed_AffiliationsData.json","Physics_AffiliationsData.json"]

with open(dataPath/"PlotData"/"subDisciplinesByYear_count.json","rt") as fd:
  subDiscByProjectByTypeByYear = json.load(fd)

with open(dataPath/"PlotData"/"disciplinesByYear_count.json","rt") as fd:
  discByProjectByTypeByYear = json.load(fd)


projectColors = OrderedDict([
    ('ATLAS',np.array([231,41,138])/255.0),
    ('BaBar',np.array([27,158,119])/255.0),
    ('LIGO',np.array([166,86,40])/255.0),
    ('IceCube',np.array([55,126,184])/255.0),
    ('HGP',np.array([255,127,0])/255.0),
    ('HuBMAP+HCA',np.array([228,26,28])/255.0),
    ]
)

lastYear = 2020

projectStart = {
    'ATLAS'     : 1997,
    'BaBar'     : 1995,
    'LIGO'      : 1991,
    'IceCube'   : 2004,
    'HGP'       : 1988,
    'HuBMAP+HCA': 2017,
}

propertyStyles = OrderedDict([
    ('Publications',"-"),
    ('Citations',"-."),
    ('Authors',":"),
    ('Affiliations',"--"),
    ]
)

constructionPhase = "Co"
researchPhase = "R"
closurePhase = "Cl"
upgradePhase = "U"
prototypingPhase = "Pr"
planningPhase = "Pl"
dataPhase = "D"


projectStages = {
  "BaBar":[
    (constructionPhase,(1995,1999)),
    (researchPhase,(1999,2008)),
    (closurePhase,(2008,2020))
  ],
  "Virgo-LIGO":1990,
  "Virgo":[
    (constructionPhase,(1996,2003)),
    (researchPhase,(2003,2011)),
    (upgradePhase,(2011,2017)),
    (researchPhase,(2017,2020)),
  ],
  "LIGO":[
    (planningPhase,(1991,1994)),
    (constructionPhase,(1994,2003)),
    (researchPhase,(2003,2008)),
    (upgradePhase,(2008,2014)),
    (researchPhase,(2014,2020)),
  ],
  "ATLAS":[
    (planningPhase,(1992,1998)),
    (constructionPhase,(1998,2007)),
    (researchPhase,(2007,2013)),
    (upgradePhase,(2013,2015)),
    (researchPhase,(2015,2020)),
  ],
  "IceCube":[
    (prototypingPhase,(2000,2005)),
    (constructionPhase,(2005,2011)),
    (researchPhase,(2011,2020)),
  ],
  "HGP":[
    (planningPhase,(1988,1994)),
    (prototypingPhase,(1994,1999)),
    (researchPhase,(1999,2003)),
    (closurePhase,(2003,2020)),
  ],
  "HuBMAP+HCA":[
    (planningPhase,(2016,2017)),
    (prototypingPhase,(2017,2018)),
    (dataPhase,(2018,2020)),
   ]
}

stageColors = {
 "Co" : np.array([32,63,48])/255.0,
 "R" : np.array([155,76,30])/255.0,
 "Cl" : np.array([88,88,88])/255.0,
 "U" : np.array([75,20,22])/255.0,
 "Pr" : np.array([198,120,74])/255.0,
 "Pl" : np.array([11,31,124])/255.0,
 "D" : np.array([54,70,0])/255.0,
}

plotData = {}
for propertyName,filenames in dataFiles.items():
    plotData[propertyName] = {}
    for filename in filenames:
        with open("../Data/PlotData/%s"%filename,"rt") as fd:
            projectsData = json.load(fd)
#             if("HCA+HuBMap" in projectsData):
#                 projectsData["HuBMAP+HCA"] = projectsData["HCA+HuBMap"]
#             elif ("HuBMAP+HCA" in projectsData):
#                 projectsData["HuBMAP+HCA"] = projectsData["HuBMAP+HCA"]
            plotData[propertyName].update(projectsData)


plotData["Total Publications"] = {}
for projectName,(years,counts) in plotData["Publications"].items():
    plotData["Total Publications"][projectName] = [years,np.cumsum(counts).tolist()]
    
plotData["Total Citations"] = {}
for projectName,(years,counts) in plotData["Citations"].items():
    plotData["Total Citations"][projectName] = [years,np.cumsum(counts).tolist()]


# %%



# %%



# %%
def first_nonzero(arr):
    return (np.array(arr)!=0).argmax(axis=0)

def last_nonzero(arr):
    return np.max(np.nonzero(np.array(arr)))


# %%



# %%
gr = 1.61803398875*0.95
figScale = 2;
fig = plt.figure(figsize=(figScale*6,figScale*gr))

prefix = ""
for projectIndex,projectName in enumerate(projectColors):
    ax = plt.subplot(1,len(projectColors),1+projectIndex)
    for propertyIndex,propertyName in enumerate(propertyStyles):
        years,counts = plotData[prefix+propertyName][projectName]
        first = first_nonzero(counts)
        last = last_nonzero(counts)
        while (years[last]>lastYear):
            last-=1
        years = years[first:(last+1)]
        counts = counts[first:(last+1)]
        
        if(useSmoothing and len(counts)>4*smoothingWindow):
            counts = np.convolve(counts, np.ones(smoothingWindow*2+1)/(1+2*smoothingWindow), mode='valid')
            years = years[1:-1]
        ax.plot(np.array(years)-projectStart[projectName],counts,propertyStyles[propertyName],color=projectColors[projectName],label=propertyName)
    if(projectIndex==0):
        ax.set_ylabel("Count")
    ax.set_xlabel("Years since first funded")
    if(projectName in projectStages):
        projectStartYear = projectStart[projectName]
        stages = projectStages[projectName];
        for stageIndex,(stageName,(stageStart,stageEnd)) in enumerate(stages):
            ax.axvspan(stageStart-projectStartYear, stageEnd-projectStartYear, color=stageColors[stageName], alpha=0.25,
                       lw=0,ymin=0.88,ymax=0.94)
#             if(stageIndex%2==0):
#                 textPosition = 0.88
#                 textAlign = "top"
#             else:
#                 textPosition = 0.93
#                 textAlign = "bottom"
            textPosition = 0.909
            textAlign = "center"
            ax.text((stageStart+stageEnd)/2.0-projectStartYear,
                    textPosition, stageName,
                    color=stageColors[stageName],
                    horizontalalignment='center',verticalalignment=textAlign,
                    fontsize=11,
                    transform=ax.get_xaxis_transform())
 


    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_yscale("log")
    ax.set_ylim(1,10**5)
    ticksbins = 7
    if(len(years)<20):
        ticksbins=8;
    ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True,prune="both",nbins=ticksbins))
    if(projectIndex!=0):
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])
        ax.tick_params(axis='y', which='both', length=0)
#     else:
#         ax.xaxis.set_ticks_position('left')
        
#     ax.xaxis.set_ticks_position('left')
    ax.axvline(0,0.0,0.80,linewidth=2, color='k',alpha=0.1)
    ax.text(0,0.815,str(projectStart[projectName]),ha="center", color='k',alpha=0.5,transform=ax.get_xaxis_transform())
    if(projectIndex==0):
        ax.legend(handlelength=3,loc='lower right',fontsize="small",frameon=False)
#     # Only show ticks on the left and bottom spines
#     ax.xaxis.set_ticks_position('bottom')
    ax.set_title(projectName,c=projectColors[projectName])
plt.subplots_adjust(wspace=0.10,bottom=0.0,left=0.00,right=1.0,top=1.0)
plt.savefig("../Figures/allprojectsPlot.pdf")
plt.close()
# plt.show()


# %%
gr = 1.61803398875*0.95
figScale = 2;
fig = plt.figure(figsize=(figScale*6,figScale*gr))

prefix = "Total "
for projectIndex,projectName in enumerate(projectColors):
    ax = plt.subplot(1,len(projectColors),1+projectIndex)
    for propertyIndex,propertyName in enumerate(propertyStyles):
        years,counts = plotData[prefix+propertyName][projectName]
        first = first_nonzero(counts);
        last = last_nonzero(counts);
        while (years[last]>lastYear):
            last-=1
        years = years[first:(last+1)]
        counts = counts[first:(last+1)]
        
        ax.plot(np.array(years)-projectStart[projectName],counts,propertyStyles[propertyName],color=projectColors[projectName],label=propertyName)
    if(projectIndex==0):
        ax.set_ylabel("Total count")
    ax.set_xlabel("Years since first funded")
    if(projectName in projectStages):
        projectStartYear = projectStart[projectName]
        stages = projectStages[projectName];
        for stageIndex,(stageName,(stageStart,stageEnd)) in enumerate(stages):
            ax.axvspan(stageStart-projectStartYear, stageEnd-projectStartYear, color=stageColors[stageName], alpha=0.25,
                       lw=0,ymin=0.88,ymax=0.94)
#             if(stageIndex%2==0):
#                 textPosition = 0.88
#                 textAlign = "top"
#             else:
#                 textPosition = 0.93
#                 textAlign = "bottom"
            textPosition = 0.909
            textAlign = "center"
            ax.text((stageStart+stageEnd)/2.0-projectStartYear,
                    textPosition, stageName,
                    color=stageColors[stageName],
                    horizontalalignment='center',verticalalignment=textAlign,
                    fontsize=11,
                    transform=ax.get_xaxis_transform())
 


#         plt.ylim(0,np.max(totalsByYear)*1.5)
    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_yscale("log")
    ax.set_ylim(1,10**6)
    ticksbins = 7
    if(len(years)<22):
        ticksbins=8;
    ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True,prune="both",nbins=ticksbins))
    if(projectIndex!=0):
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])
        ax.tick_params(axis='y', which='both', length=0)
#     else:
#         ax.xaxis.set_ticks_position('left')
        
#     ax.xaxis.set_ticks_position('left')
    ax.axvline(0,0.0,0.80,linewidth=2, color='k',alpha=0.1)
    ax.text(0,0.815,str(projectStart[projectName]),ha="center", color='k',alpha=0.5,transform=ax.get_xaxis_transform())
    if(projectIndex==0):
        ax.legend(handlelength=3,loc='lower right',fontsize="small",frameon=False)
#     # Only show ticks on the left and bottom spines
#     ax.xaxis.set_ticks_position('bottom')
    ax.set_title(projectName,c=projectColors[projectName])
plt.subplots_adjust(wspace=0.10,bottom=0.0,left=0.00,right=1.0,top=1.0)
plt.savefig("../Figures/allprojectsPlotTotal.pdf")
plt.close()
# plt.show()

















def calculateEffective(data):
    p = np.array(list(data.values()))
    sump = np.sum(p)
    p = p/sump
    H = np.sum(-p*np.log(p))
    return np.exp(H)


disciplineLevelDict = {
    "disciplines":(discByProjectByTypeByYear,15),
    "subjects":(subDiscByProjectByTypeByYear,554)
}

maximumSubjects = 0
# %% disciplines
for disciplineLevel,(disciplineData,maxDisciplines) in disciplineLevelDict.items():
    for edgesType in ["Referenced","Citing"]:
        gr = 1.61803398875*0.95
        figScale = 2;
        fig = plt.figure(figsize=(figScale*6*1.1,figScale*gr*1.3))

        prefix = ""
        for projectIndex,projectName in enumerate(projectColors):
            ax = plt.subplot(1,len(projectColors),1+projectIndex)
            discByYear = disciplineData[projectName][edgesType]
            years = sorted([int(year) for year in discByYear.keys() if int(year)>0])
            uniqueCount = [len(discByYear[str(year)].keys()) for year in years]
            effectiveCount = [calculateEffective(discByYear[str(year)]) for year in years]
            maximumSubjects = max(maximumSubjects,np.max(uniqueCount))
            print("%s: %d subjects (%s)"%(projectName,np.max(uniqueCount),edgesType))
            ax.plot(np.array(years)-projectStart[projectName],uniqueCount,"-",color=projectColors[projectName],label="Unique")
            ax.plot(np.array(years)-projectStart[projectName],effectiveCount,"--",color=projectColors[projectName],label="Effective")
            
            if(projectIndex==0):
                ax.set_ylabel("Count")
            ax.set_xlabel("Years since first funded")
            if(projectName in projectStages):
                projectStartYear = projectStart[projectName]
                stages = projectStages[projectName];
                for stageIndex,(stageName,(stageStart,stageEnd)) in enumerate(stages):
                    ax.axvspan(stageStart-projectStartYear, stageEnd-projectStartYear, color=stageColors[stageName], alpha=0.25,
                            lw=0,ymin=0.88,ymax=0.94)
        #             if(stageIndex%2==0):
        #                 textPosition = 0.88
        #                 textAlign = "top"
        #             else:
        #                 textPosition = 0.93
        #                 textAlign = "bottom"
                    textPosition = 0.909
                    textAlign = "center"
                    ax.text((stageStart+stageEnd)/2.0-projectStartYear,
                            textPosition, stageName,
                            color=stageColors[stageName],
                            horizontalalignment='center',verticalalignment=textAlign,
                            fontsize=11,
                            transform=ax.get_xaxis_transform())
        


            
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.set_yscale("log")
            ax.set_ylim(1,maxDisciplines*3)
            ticksbins = 7
            if(len(years)<20):
                ticksbins=8;
            ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True,prune="both",nbins=ticksbins))
            if(projectIndex!=0):
                ax.spines['left'].set_visible(False)
                ax.set_yticks([])
                ax.tick_params(axis='y', which='both', length=0)
        #     else:
        #         ax.xaxis.set_ticks_position('left')
                
        #     ax.xaxis.set_ticks_position('left')
            ax.axvline(0,0.0,0.80,linewidth=2, color='k',alpha=0.1)
            ax.text(0,0.815,str(projectStart[projectName]),ha="center", color='k',alpha=0.5,transform=ax.get_xaxis_transform())
            if(projectIndex==0):
                ax.legend(handlelength=3,loc='lower right',fontsize="small",frameon=False)
        #     # Only show ticks on the left and bottom spines
        #     ax.xaxis.set_ticks_position('bottom')
            ax.set_title(projectName,c=projectColors[projectName])
        plt.subplots_adjust(wspace=0.10,bottom=0.2,left=0.05,right=0.95,top=0.9)
        plt.savefig("../Figures/%sOverTime_%s.pdf"%(disciplineLevel,edgesType))
        plt.close()
        # plt.show()






# %% disciplines
disciplineLevel = "disciplines"
disciplineData,maxDisciplines = disciplineLevelDict[disciplineLevel]
for plotType in ["relative","absolute"]:
    for edgesType in ["Referenced","Citing"]:
        gr = 1.61803398875*0.95
        figScale = 2;
        extraWideMultiplier = (1.00 if (plotType=="relative") else 1.20)
        fig = plt.figure(figsize=(figScale*6*1.1*extraWideMultiplier,figScale*gr*1.3))

        for projectIndex,projectName in enumerate(projectColors):
            ax = plt.subplot(1,len(projectColors),1+projectIndex)
            discByYear = disciplineData[projectName][edgesType]
            years = sorted([int(year) for year in discByYear.keys() if int(year)>0])
            uniqueCount = [len(discByYear[str(year)].keys()) for year in years]
            allDisciplines = [entry[0] for entry in sorted(discipline2Name.items(),key=lambda x:x[1],reverse=True)]
            disciplineWeightsByYear = [[discByYear[str(year)][str(discipline)] if str(discipline) in discByYear[str(year)] else 0 for year in years ] for discipline in allDisciplines]
            labels = [discipline2Name[disciplineID] for disciplineID in allDisciplines]
            colors = [discipline2Color[disciplineID] for disciplineID in allDisciplines]
            y = np.vstack(disciplineWeightsByYear)
            maxDistribValue = np.max(np.sum(y,axis=0));

            if(plotType=="relative"):
                y = y/y.sum(axis=0,keepdims=1)
            ax.stackplot(np.array(years)-projectStart[projectName], y, labels=labels,colors=colors)
            # ax.plot(np.array(years)-projectStart[projectName],uniqueCount,"-",color=projectColors[projectName],label="Unique")
            


            if(projectIndex==0):
                ax.set_ylabel("Count")
            ax.set_xlabel("Years since first funded")
            if(projectName in projectStages):
                projectStartYear = projectStart[projectName]
                stages = projectStages[projectName];
                for stageIndex,(stageName,(stageStart,stageEnd)) in enumerate(stages):
                    ax.axvspan(stageStart-projectStartYear, stageEnd-projectStartYear, color=stageColors[stageName], alpha=0.25,
                            lw=0,ymin=0.88,ymax=0.94)
        #             if(stageIndex%2==0):
        #                 textPosition = 0.88
        #                 textAlign = "top"
        #             else:
        #                 textPosition = 0.93
        #                 textAlign = "bottom"
                    textPosition = 0.909
                    textAlign = "center"
                    ax.text((stageStart+stageEnd)/2.0-projectStartYear,
                            textPosition, stageName,
                            color=stageColors[stageName],
                            horizontalalignment='center',verticalalignment=textAlign,
                            fontsize=11,
                            transform=ax.get_xaxis_transform())
        


            
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            # ax.set_yscale("log")
            if(plotType=="relative"):
                ax.set_ylim(0,1.2)
            else:
                ax.set_ylim(0,maxDistribValue*1.2)
                
            ticksbins = 7
            if(len(years)<20):
                ticksbins=8;
            ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True,prune="both",nbins=ticksbins))
            if(projectIndex!=0 and plotType=="relative"):
                ax.spines['left'].set_visible(False)
                ax.set_yticks([])
                ax.tick_params(axis='y', which='both', length=0)
        #     else:
        #         ax.xaxis.set_ticks_position('left')
                
        #     ax.xaxis.set_ticks_position('left')
            ax.axvline(0,0.0,0.80,linewidth=2, color='k',alpha=0.1)
            ax.text(0,0.815,str(projectStart[projectName]),ha="center", color='k',alpha=0.5,transform=ax.get_xaxis_transform())
            if(projectIndex==0):
                ax.legend(handlelength=3,fontsize="xx-small",frameon=False)
        #     # Only show ticks on the left and bottom spines
        #     ax.xaxis.set_ticks_position('bottom')
            ax.set_title(projectName,c=projectColors[projectName])
        plt.subplots_adjust(wspace=(0.10 if (plotType=="relative") else 0.25),bottom=0.2,left=0.05,right=0.95,top=0.9)
        plt.savefig("../Figures/%sOverTimeDistrib_%s_%s.pdf"%(disciplineLevel,edgesType,plotType))
        plt.close()
        # plt.show()
