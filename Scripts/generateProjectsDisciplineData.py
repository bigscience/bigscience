import pandas as pd
import json
import ujson
import struct
from pathlib import Path
import numpy as np
from tqdm.auto import tqdm
from collections import Counter

def counterFromFrequencyTuplesWeights(tupleList):
  resultCounter = Counter()
  for entry,count in tupleList:
    if entry in resultCounter:
      resultCounter[entry] += count
    else:
      resultCounter[entry] = count
  return resultCounter



def counterFromFrequencyTuples(tupleList):
  resultCounter = Counter()
  for entry,count in tupleList:
    if entry in resultCounter:
      resultCounter[entry] += 1
    else:
      resultCounter[entry] = 1
  return resultCounter

dataPath = Path("../Data")

subDiscipline2DisciplineData = pd.read_csv(dataPath/"ScienceMapSubDisciplineToDiscipline.tsv",sep="\t")
subDiscipline2Discipline = dict(zip(subDiscipline2DisciplineData["subd_id"],subDiscipline2DisciplineData["disc_id"]))

counterFunctions = {
  "count":counterFromFrequencyTuples,
  "weights":counterFromFrequencyTuplesWeights,
}

for counterName,counterFunction in counterFunctions.items():
  topSubjByProjectByTypeByYear = {}
  topDiscByProjectByTypeByYear = {}
  for projectCategory,projectName in tqdm([("Physics","BaBar"),("Physics","ATLAS"),("Physics","LIGO"),("Physics","IceCube"),("Biomedical","HGP"),("Biomedical","HuBMAP+HCA")]):
    topSubjByTypeByYear = {}
    topSubjByProjectByTypeByYear[projectName] = topSubjByTypeByYear
    topDiscByTypeByYear = {}
    topDiscByProjectByTypeByYear[projectName] = topDiscByTypeByYear
    for edgesType in ["Referenced","Citing"]:
      topSubjByYear = {}
      topSubjByTypeByYear[edgesType] = topSubjByYear
      topDiscByYear = {}
      topDiscByTypeByYear[edgesType] = topDiscByYear
      edgesTable = pd.read_csv(dataPath/"ToMapOfScience"/("%s_Edges_%s_%s_tomap_keywords.csv.gz"%(projectCategory,edgesType,projectName)))
      
      if(edgesType == "Referenced"):
        externalTag = "Cited"
      else:
        externalTag = "Citing"

      edgesTableFiltered = edgesTable[edgesTable[externalTag+" Top Subject ID"].notna()].copy()
      edgesTableFiltered[externalTag+" Top Discipline ID"] = [subDiscipline2Discipline[int(entry)] for entry in edgesTableFiltered[externalTag+" Top Subject ID"]]
      externalSubjectCounts = counterFunction(zip(zip(edgesTableFiltered["Citing Publication Year"],[int(entry) for entry in edgesTableFiltered[externalTag+" Top Subject ID"]]),edgesTableFiltered[externalTag+" Top Subject Weight"]))
      externalDisciplineCounts = counterFunction(zip(zip(edgesTableFiltered["Citing Publication Year"],[int(entry) for entry in edgesTableFiltered[externalTag+" Top Discipline ID"]]),edgesTableFiltered[externalTag+" Top Subject Weight"]))
      for (year,subjID),weight in externalSubjectCounts.items():
        if(year not in topSubjByYear):
          topSubjByYear[year] = {}
        topSubjByYear[year][subjID] = weight
      
      for (year,discID),weight in externalDisciplineCounts.items():
        if(year not in topDiscByYear):
          topDiscByYear[year] = {}
        topDiscByYear[year][discID] = weight

  with open(dataPath/"PlotData"/("subDisciplinesByYear_%s.json"%counterName),"wt") as fd:
    json.dump(topSubjByProjectByTypeByYear,fd)
    

  with open(dataPath/"PlotData"/("disciplinesByYear_%s.json"%counterName),"wt") as fd:
    json.dump(topDiscByProjectByTypeByYear,fd)
  