import pandas as pd
import json
import ujson
import struct
import bgzf
from pathlib import Path
import numpy as np
from tqdm.auto import tqdm
import nltk
from nltk.util import ngrams
from collections import Counter
nltk.download('punkt')


def getTokensSet(text):
  tokens = nltk.word_tokenize(text)
  tokensSet = set(tokens)
  for n in range(1,5):
    tokensSet.update(["_".join(entry) for entry in ngrams(tokens,n)])
  return tokensSet

dataPath = Path("../Data")


HEPBGZ = dataPath/"INSPIRE"/"20210108"/"Processed"/"HEP.bgzip";
def loadbgzip(filepath,estimated=1362493):
  entries=[];
  with bgzf.open(filepath,"rb") as fd:
    pbar = tqdm(total=estimated);
    while True:
        pbar.update(1);
        sizeBuffer = fd.read(8*1);
        if(len(sizeBuffer)==8*1):
            dataSize = struct.unpack("<Q",sizeBuffer)[0];
            data = fd.read(dataSize);
            entry = ujson.loads(data.decode("utf8"));
            entries.append(entry);
        else:
            break; 
  return entries;
HEPEntries = loadbgzip(HEPBGZ,estimated = 1404482);

keywordTable = pd.read_csv(dataPath/"ScienceMapKeyword2subjID.tsv",sep="\t")
keyword2subjID = {}
subjID2keyword = {}
for subjid, rawKeyword, weight in keywordTable.to_numpy().tolist():
  keyword = rawKeyword.lower()
  if keyword not in keyword2subjID:
    keyword2subjID[keyword] = []
  if subjid not in subjID2keyword:
    subjID2keyword[subjid] = []
  keyword2subjID[keyword].append((subjid,weight))
  subjID2keyword[subjid].append((keyword,weight))
  
keywordsSet = set(keyword2subjID.keys())


ID2Title = {int(entry["ID"]):entry["Title"] for entry in HEPEntries}


ID2subjIDs = {}
for id,rawTitle in tqdm(ID2Title.items()):
  counts = Counter()
  if(rawTitle):
    title = rawTitle.lower()
    tokensSet = getTokensSet(title)
    matchedKeywords = tokensSet.intersection(keywordsSet)
    for keyword in matchedKeywords:
      counts.update({subjID:weight for subjID,weight in keyword2subjID[keyword]})
  ID2subjIDs[id] = counts


for projectName in ["BaBar","ATLAS","LIGO","IceCube"]:
  for edgesType in ["Referenced","Citing"]:
    edgesTable = pd.read_csv(dataPath/"ToMapOfScience"/("Physics_Edges_%s_%s_tomap.csv.gz"%(edgesType,projectName)))
    for nodeType in ["Citing","Cited"]:
      nodeSubjects = []
      for nodeID in edgesTable["%s ID"%nodeType]:
        nodeSubjects.append(ID2subjIDs[int(nodeID)])
      nodeMostCommonSubject = [entry.most_common(1) for entry in nodeSubjects]
      edgesTable["%s Top Subject ID"%nodeType] = [entry[0][0] if entry else "NA"for entry in nodeMostCommonSubject]
      edgesTable["%s Top Subject Weight"%nodeType] = [entry[0][1] if entry else "NA"for entry in nodeMostCommonSubject]
      edgesTable["%s Subject IDs"%nodeType] = [json.dumps(entry) if entry else "NA" for entry in nodeSubjects]
    edgesTable.to_csv(dataPath/"ToMapOfScience"/("Physics_Edges_%s_%s_tomap_keywords.csv.gz"%(edgesType,projectName)))


def calculateValidInvalidTotal(toID):
  total = len(toID)
  invalid = np.sum(np.isnan(list(toID.values())))
  valid = total-invalid
  return {"Valid":valid,"Invalid":invalid,"Total":total,"Valid %":"%d%%"%round(100*valid/total)}

def matchesKeywords2(tableEntry):
  counts = [len(json.loads(ids)) if not isinstance(ids,float) else 0 for ids in tableEntry]
  return [c if c>=2 else float("nan") for c in counts]
  

allProjecsCounts = {}
for projectName in ["BaBar","ATLAS","LIGO","IceCube"]:
  projectCounts = {}
  allProjecsCounts[projectName] = projectCounts
  for edgesType in ["Referenced","Citing"]:
    edgesTable = pd.read_csv(dataPath/"ToMapOfScience"/("Physics_Edges_%s_%s_tomap_keywords.csv.gz"%(edgesType,projectName)))
    citingID2SciMapID = dict(zip(edgesTable["Citing ID"],edgesTable["Citing Venue SciMap ID"]))
    citedID2SciMapID = dict(zip(edgesTable["Cited ID"],edgesTable["Cited Venue SciMap ID"]))
    
    citingID2Keyword = dict(zip(edgesTable["Citing ID"],edgesTable["Citing Top Subject ID"]))
    citedID2Keyword = dict(zip(edgesTable["Cited ID"],edgesTable["Cited Top Subject ID"]))
    
    citingID2Keyword2 = dict(zip(edgesTable["Citing ID"],matchesKeywords2(edgesTable["Citing Subject IDs"])))
    citedID2Keyword2 = dict(zip(edgesTable["Cited ID"],matchesKeywords2(edgesTable["Cited Subject IDs"])))

    projectCounts["%s Citing Venue Matches"%edgesType] = calculateValidInvalidTotal(citingID2SciMapID)
    projectCounts["%s Cited Venue Matches"%edgesType] = calculateValidInvalidTotal(citedID2SciMapID)
    projectCounts["%s Citing Keyword Matches"%edgesType] = calculateValidInvalidTotal(citingID2Keyword)
    projectCounts["%s Cited Keyword Matches"%edgesType] = calculateValidInvalidTotal(citedID2Keyword)
    projectCounts["%s Citing at least 2 Keywords Matches"%edgesType] = calculateValidInvalidTotal(citingID2Keyword2)
    projectCounts["%s Cited at least 2 Keywords Matches"%edgesType] = calculateValidInvalidTotal(citedID2Keyword2)

projectMapCoverageTable = pd.DataFrame.from_dict({(i,j): allProjecsCounts[i][j] 
                           for i in allProjecsCounts.keys() 
                           for j in allProjecsCounts[i].keys()},
                       orient='index')

projectMapCoverageTable.to_csv(dataPath/"ToMapOfScience"/("Physics_projectMapCoverageTable.csv"))

