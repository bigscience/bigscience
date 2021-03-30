#!/usr/bin/env python
# coding: utf-8

import math
from tqdm.auto import tqdm
import pandas as pd
import ujson
import numpy as np;
import pickle
import os
import xnetwork as xn
import bgzf
import json
import struct
import os
import igraph as ig
import matplotlib.pyplot as plt 
from os.path import join as PJ
import gzip
import sys
import re
from datetime import datetime as dt
import sys
import matplotlib
import nltk

nltk.download("stopwords")
from nltk.corpus import stopwords

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


MAGPath = PJ("..","Data","MAG") #PATH TO THE MAG DATA
MAGPath = PJ("/gpfs/sciencegenome/AuthorDynamics/MAG/mag-2021-01-05/mag")
dataPath = PJ("..","Data","Processed")
figuresPath = PJ("..","Figures")
graycolor = "#808080"

HCAProjectDataPath = PJ("..","Data","Publications","Biomedical Papers","HumanCellAtlas.json")
HGPTitles2MAGPath = PJ("..","Data","Publications","Biomedical Papers","HGP_Publications_MAG.tsv")

minPaperCount = 1;
rebuildAll = False

temporaryPath = PJ("..","Temp")
os.makedirs(dataPath, exist_ok=True)
os.makedirs(temporaryPath, exist_ok=True)


def dictFromList(aList):
    return {aList[i]:i for i in range(len(aList))}


STOPWORDS = stopwords.words('english')
STOPWORDS = set(STOPWORDS)
import re
def text_prepare(text, STOPWORDS=STOPWORDS):
    """
        text: a string
        
        return: a clean string
    """
    REPLACE_BY_SPACE_RE = re.compile('[\n\"\'/(){}\[\]\|@,;#\.]')
    text = re.sub(REPLACE_BY_SPACE_RE, ' ', text)
    text = re.sub(' +', ' ', text)
    text = text.lower()

    # delete stopwords from text
    text = ' '.join([word for word in text.split() if word not in STOPWORDS]) 
    text = text.strip()
    return text

  
sortedPapersFilePath = PJ(dataPath,"MAGPapersByPaper.txt");
bgzPapersFilePath = PJ(dataPath,"MAGPapers.bgz");

papersDataTypes = [
    ("PaperId", int),
    ("Rank", int),
    ("Doi", str),
    ("DocType", str),
    ("PaperTitle", str),
    ("OriginalTitle", str),
    ("BookTitle", str),
    ("Year", int),
    ("Date", str),
    ("OnlineDate", str),
    ("Publisher", str),
    ("JournalId", int),
    ("ConferenceSeriesId", int),
    ("ConferenceInstanceId", int),
    ("Volume", str),
    ("Issue", str),
    ("FirstPage", str),
    ("LastPage", str),
    ("ReferenceCount", int),
    ("CitationCount", int),
    ("EstimatedCitation", int),
    ("OriginalVenue", str),
    ("FamilyId", int),
    ("FamilyRank",int),
    ("CreatedDate", str),
]


# Getting paper Metadata
def processTitleYearJournal(bgzPapersFilePath,papersDataTypes):
    estimatedCount = 233745561;
    index2magID = []
    index2Title = []
    index2DOI = []
    index2Year = []
    index2OnlineDate = []
    index2JournalID = []
    count = 0;
    with bgzf.open(bgzPapersFilePath,"rb") as infd:
        pbar = tqdm(total=estimatedCount);
        while True:
            pbar.update(1);
            lengthData = infd.read(8);
            if(len(lengthData)==8):
                length = struct.unpack("<q",lengthData)[0];
            else:
                break;
            data = infd.read(length);
            paperIndex = struct.unpack("<q",data[0:8])[0];
            currentPointer = 8;
    #         paperID = struct.unpack("<q",data[8:16])[0];
            dataDict = {};
            for (typeIndex,(typeName,typeType)) in enumerate(papersDataTypes):
                if(typeType==int):
                    entryValue, = struct.unpack("<q",data[currentPointer:currentPointer+8]);
                    currentPointer+=8;
                    dataDict[typeName] = entryValue;
                else:
                    entryLength, = struct.unpack("<q",data[currentPointer:currentPointer+8]);
                    currentPointer+=8;
                    entryData = data[currentPointer:currentPointer+entryLength].decode("utf8");
                    currentPointer+=entryLength;
                    dataDict[typeName] = entryData;
            index2Title.append(dataDict["PaperTitle"])
            index2Year.append(dataDict["Year"])
            index2magID.append(dataDict["PaperId"])
            index2DOI.append(dataDict["Doi"])
            index2OnlineDate.append(dataDict["OnlineDate"])
            index2JournalID.append(dataDict["JournalId"])
            count+=1;
#             if(count>100000):
#                 break;
    return index2Title,index2magID,index2Year,index2OnlineDate,index2JournalID,index2DOI;


index2Title,index2magID,index2Year,index2OnlineDate,index2JournalID,index2DOI=processTitleYearJournal(bgzPapersFilePath,papersDataTypes)
index2FirstYear = []
for i in tqdm(range(len(index2Year))):
    year = index2Year[i]
    if(index2OnlineDate[i]):
        onlineDate = int(index2OnlineDate[i][0:4])
        if(onlineDate<year):
            year=onlineDate
    index2FirstYear.append(year)
del index2OnlineDate


magID2Index = dictFromList(index2magID)


# Loading extended attributes

# PAPER EXTENDED ATTRIBUTES
# Column #	Name	Type	Note
# 1	PaperId	long	FOREIGN KEY REFERENCES Papers.PaperId
# 2	AttributeType	int	1: PatentId
#                       2: PubMedId
#                       3: PmcId
#                       4: Alternative Title
# 3	AttributeValue	string	

paperExtendedAttributesFilePath = PJ(MAGPath,"PaperExtendedAttributes.txt");
index2PubMedId = [None]*len(index2magID)
index2PmcId = [None]*len(index2magID)
missingPaperIDs = set()
estimatedCount = 233745561;
previousPaperID = 0
currentIndex = 0
magCount = len(index2magID)
with open(paperExtendedAttributesFilePath,"rt") as fd:
    pbar = tqdm(total=estimatedCount);
    pbar2 = tqdm(total=estimatedCount);
    for line in fd:
        pbar.update(1);
        entries = line.strip().split("\t");
        paperID = int(entries[0]);
        if(paperID<previousPaperID):
            print("Problem!!! Out of order!")
            break
        previousPaperID = paperID;
        currentMAGID = index2magID[currentIndex]
        while(currentMAGID<paperID and currentIndex<magCount):
            currentIndex+=1;
            currentMAGID = index2magID[currentIndex]
            pbar2.update(1);
        if(currentMAGID==paperID):
            attributeType = int(entries[1]);
            attributeValue = str(entries[2]);
            if(attributeType==2):
                index2PubMedId[currentIndex] = attributeValue
            if(attributeType==3):
                index2PmcId[currentIndex] = attributeValue
        else:
            continue;
            
            
            
# Matching HCA Projects
with open(HCAProjectDataPath,"rt") as fd:
    HCAProjectData = ujson.load(fd);
for entry in HCAProjectData:
    if("links" in entry):
        entry.update({x.split(": ")[0]:x.split(": ")[1] for x in entry["links"] if len(x.split(": "))>1})

#By
#PMC
#DOI
#TITLES
#PUBMED

#HCA Match2MAG
HCAProjectDOISets = {}
HCAProjectTitleSets = {}
HCAProjectPMCSets = {}
HCAProjectPUBMEDSets = {}
for entry in HCAProjectData:
    if("DOI" in entry):
        HCAProjectDOISets[entry["DOI"].lower()] = entry;
        
    if("PMC" in entry):
        HCAProjectPMCSets[entry["PMC"].lower()] = entry;
        
    if("PUBMED" in entry):
        HCAProjectPUBMEDSets[entry["PUBMED"].lower()] = entry;
        
    HCAProjectTitleSets[text_prepare(entry["title"].lower())] = entry;

    
selectedDOIMatches = {}
selectedTitleMatches = {}
selectedPMCMatches = {}
selectedPUBMEDMatches = {}
for i in tqdm(range(len(index2Year))):
    DOI = index2DOI[i].lower()
    if(DOI in HCAProjectDOISets):
        selectedDOIMatches[DOI] = i;
        continue;
    
    PMCID = index2PmcId[i]
    if(PMCID):
        PMCID = PMCID.lower() 
        if(PMCID in HCAProjectPMCSets):
            selectedPMCMatches[PMCID] = i;
            continue;
    
    PUBMEDID = index2PubMedId[i]
    if(PUBMEDID):
        PUBMEDID = PUBMEDID.lower() 
        if(PUBMEDID in HCAProjectPUBMEDSets):
            selectedPUBMEDMatches[PUBMEDID] = i;
            continue;
    
    reducedTitle = text_prepare(index2Title[i].lower())
    if(reducedTitle in HCAProjectTitleSets):
        selectedTitleMatches[reducedTitle] = i;
        continue;

        

#Matching HCA projects

HCAProjectMAGIndices = set(selectedDOIMatches.values()).union(set(selectedTitleMatches.values()))

#Human Cell Atlas
HCAMissingData = []
for entry in HCAProjectData:
    matchesCount = 0;
    if("DOI" in entry and entry["DOI"].lower() in selectedDOIMatches):
        matchesCount+=1
    if("title" in entry and text_prepare(entry["title"].lower()) in selectedTitleMatches):
        matchesCount+=1
    if(matchesCount>0):
#         print(checkDouble);
        continue
    HCAMissingData.append(entry)
# print(missingData)

#Saving HCA Matched MAG Indices
with open(PJ("..","Data","Publications","Biomedical Papers","HCA_MAGIndices.json"),"wt") as fd:
    ujson.dump(list(HCAProjectMAGIndices),fd)
    
with open(PJ("..","Data","Publications","Biomedical Papers","HCA_MissingEntries.json"),"wt") as fd:
    ujson.dump(list(HCAMissingData),fd)



#Human Genome Project
dfHGP = pd.read_csv(HGPTitles2MAGPath,sep="\t")
HGPProjectMAGIndices = set()
HGPMissingData = []
for referece,url in dfHGP[["Reference","MAG URL"]].to_numpy():
    if(url==url):
        magID = int(re.search(r'https\:\/\/academic\.microsoft\.com\/paper\/(.*?)\/reference', url).group(1))
        if(magID in magID2Index):
            index = magID2Index[magID]
            HGPProjectMAGIndices.add(index)
            continue;
        
    HGPMissingData.append(referece);

with open(PJ("..","Data","Publications","Biomedical Papers","HGP_MAGIndices.json"),"wt") as fd:
    ujson.dump(list(HGPProjectMAGIndices),fd)
    
with open(PJ("..","Data","Publications","Biomedical Papers","HGP_MissingEntries.json"),"wt") as fd:
    ujson.dump(list(HGPMissingData),fd)

HBMapDataPaths = [
    PJ("..","Data","Publications","Biomedical Papers","Pubhl_Export_21Jan2021_084406.csv"),
    PJ("..","Data","Publications","Biomedical Papers","Pubhl_Export_21Jan2021_084445.csv"),
    PJ("..","Data","Publications","Biomedical Papers","Publ_18Jan2021_014100_86642982.csv")
]

HBMapTitleKey = "Title (Link to full-text in PubMed Central)"
HBMapDfs = [pd.read_csv(filename,dtype={"PMC ID":str,"PMID":str}) for filename in HBMapDataPaths]
HBMapDf = pd.concat(HBMapDfs,sort=False)


HBMapTitles = HBMapDf[HBMapTitleKey].to_list()
HBMapReducedTitles = set(text_prepare(title.lower()) for title in HBMapTitles if isinstance(title,str))
HBMapPMCIDs = set(pmcid.lower() for pmcid in HBMapDf["PMC ID"].to_list() if isinstance(pmcid,str))
HBMapPUBMEDIDs = set(pubmedID.lower() for pubmedID in HBMapDf["PMID"].to_list() if isinstance(pubmedID,str))


HBMapSelectedDOIMatches = {}
HBMapSelectedTitleMatches = {}
HBMapSelectedPMCMatches = {}
HBMapSelectedPUBMEDMatches = {}

pbarnew = tqdm(desc='Added');
for i in tqdm(range(len(index2Year))):    
    PMCID = index2PmcId[i]
    if(PMCID):
        PMCID = PMCID.lower() 
        if(PMCID in HBMapPMCIDs):
            HBMapSelectedPMCMatches[PMCID] = i;
            pbarnew.update(1);
            continue;
    
    PUBMEDID = index2PubMedId[i]
    if(PUBMEDID):
        PUBMEDID = PUBMEDID.lower() 
        if(PUBMEDID in HBMapPUBMEDIDs):
            HBMapSelectedPUBMEDMatches[PUBMEDID] = i;
            pbarnew.update(1);
            continue;
    
    reducedTitle = text_prepare(index2Title[i].lower())
    if(reducedTitle in HBMapReducedTitles):
        HBMapSelectedTitleMatches[reducedTitle] = i;
        pbar2.update(1);
        continue;


HBMapProjectMAGIndices = set(HBMapSelectedPMCMatches.values()).union(set(HBMapSelectedPUBMEDMatches.values()).union(set(HBMapSelectedTitleMatches.values())))

HBMapMissingData = []
for title,PMCID,PMID in HBMapDf[[HBMapTitleKey,"PMC ID","PMID"]].to_numpy():
    matchesCount = 0;
    if(PMCID in HBMapSelectedPMCMatches):
        matchesCount+=1
    if(PMID in HBMapSelectedPUBMEDMatches):
        matchesCount+=1
    if(title==title and text_prepare(title.lower()) in HBMapSelectedTitleMatches):
        matchesCount+=1
    if(matchesCount>0):
#         print(checkDouble);
        continue
    if(title==title):
        HBMapMissingData.append(title)
        
HBMapMissingData = set(HBMapMissingData)

#Included by manually searching missing in MAG
HBMapManualMAGIDIncludes = [
    3092960214,
    3099559583,
    3099294714,
    3089472526,
    3100967665,
    3038602829,
    3092108146,
    3081828282,
    3099559583,
]
          
          
#Only adding matches in currentMAGData
for magID in HBMapManualMAGIDIncludes:
    if(magID in magID2Index):
        HBMapProjectMAGIndices.add(magID2Index[magID])

with open(PJ("..","Data","Publications","Biomedical Papers","HBMap_MAGIndices.json"),"wt") as fd:
    ujson.dump(list(HBMapProjectMAGIndices),fd)
    
with open(PJ("..","Data","Publications","Biomedical Papers","HBMap_MissingEntries.json"),"wt") as fd:
    ujson.dump(list(HBMapMissingData),fd)

          

# In[402]:


#Statistics:
print("Summary")
print("HCA")
print("\tMatches: %d\n\tMissing:%d"%(len(HCAProjectMAGIndices),len(HCAMissingData)))
print("HuBMAP")
print("\tMatches: %d\n\tMissing:%d"%(len(HBMapProjectMAGIndices),len(HBMapMissingData)))
print("HGP")
print("\tMatches: %d\n\tMissing:%d"%(len(HGPProjectMAGIndices),len(HGPMissingData)))



# Testing open
with open(PJ("..","Data","Publications","Biomedical Papers","HCA_MAGIndices.json"),"rt") as fd:
    HCAProjectMAGIndices = set(ujson.load(fd))
    
with open(PJ("..","Data","Publications","Biomedical Papers","HBMap_MAGIndices.json"),"rt") as fd:
    HBMapProjectMAGIndices = set(ujson.load(fd))
    
with open(PJ("..","Data","Publications","Biomedical Papers","HGP_MAGIndices.json"),"rt") as fd:
    HGPProjectMAGIndices = set(ujson.load(fd))


# Recovering References from MAG


#references FromTo
estimatedCount = 79684807
bgzReferencesFromToPath = PJ(dataPath,"MAGPaperReferencesFromTo.bgz")
entriesCount = 0
# setOfJournalsReferenced = set()
# setOfJournalsWithPublications = set()
HCACitationsPerYear = {}
HBMapCitationsPerYear = {}
HCAHuBMapCitationsPerYear = {}
HGPCitationsPerYear = {}


projectCitations = {
    "HCA":(HCAProjectMAGIndices,HCACitationsPerYear),
    "HuBMAP":(HBMapProjectMAGIndices,HBMapCitationsPerYear),
    "HuBMAP+HCA":(HBMapProjectMAGIndices.union(HCAProjectMAGIndices),HCAHuBMapCitationsPerYear),
    "HGP":(HGPProjectMAGIndices,HGPCitationsPerYear)
}

MAGID2CitationYear = {}
with bgzf.open(bgzReferencesFromToPath,"rb") as infd:
    pbar = tqdm(total=estimatedCount)
    count = 0
    while True:
        pbar.update(1)
        lengthData = infd.read(8)
        if(len(lengthData)==8):
            length = struct.unpack("<q",lengthData)[0]
        else:
            break
        data = infd.read(length)
        edgesCount = length/8-1
        fmt = "<%dq" % (edgesCount+1)
        edgeData  = list(struct.unpack(fmt,data))
        fromIndex = edgeData[0]
        fromID = index2magID[fromIndex]
        count+=1
        if(len(edgeData)>1):
            year = index2FirstYear[fromIndex]
            for projectName,(indices,citationsPerYear) in projectCitations.items():
                toIndices = set(edgeData[1:]).intersection(indices)
                if(toIndices):
                    if(year not in citationsPerYear):
                        citationsPerYear[year] = set()
                    citationsPerYear[year].add(fromIndex)
                    for toID in [index2magID[index] for index in toIndices]:
                        if(toID not in MAGID2CitationYear):
                            MAGID2CitationYear[toID] = []
                        MAGID2CitationYear[toID].append((fromID,year))
            

HCAReferencesPerYear = {}
HBMapReferencesPerYear = {}
HCAHuBMapReferencesPerYear = {}
HGPReferencesPerYear = {}

projectReferences = {
    "HCA":(HCAProjectMAGIndices,HCAReferencesPerYear),
    "HuBMAP":(HBMapProjectMAGIndices,HBMapReferencesPerYear),
    "HuBMAP+HCA":(HBMapProjectMAGIndices.union(HCAProjectMAGIndices),HCAHuBMapReferencesPerYear),
    "HGP":(HGPProjectMAGIndices,HGPReferencesPerYear)
}

bgzReferencesToFromPath = PJ(dataPath,"MAGPaperReferencesToFrom.bgz");
entriesCount = 0;
MAGID2ReferenceYear = {};
with bgzf.open(bgzReferencesToFromPath,"rb") as infd:
    pbar = tqdm(total=estimatedCount);
    count = 0;
    while True:
        pbar.update(1);
        lengthData = infd.read(8);
        if(len(lengthData)==8):
            length = struct.unpack("<q",lengthData)[0];
        else:
            break;
        data = infd.read(length);
        edgesCount = length/8-1;
        fmt = "<%dq" % (edgesCount+1)
        edgeData  = list(struct.unpack(fmt,data))
        fromIndex = edgeData[0];
        fromID = index2magID[fromIndex]
        count+=1;
        if(len(edgeData)>1):
            for projectName,(indices,referencesPerYear) in projectReferences.items():
                toIndices = set(edgeData[1:]).intersection(indices)
                if(toIndices):
                    if(year not in referencesPerYear):
                        referencesPerYear[year] = set();
                    referencesPerYear[year].add(fromIndex);
                    for toIndex,toID in [(index,index2magID[index]) for index in toIndices]:
                        year = index2FirstYear[fromIndex];
                        if(toID not in MAGID2ReferenceYear):
                            MAGID2ReferenceYear[toID] = [];
                        MAGID2ReferenceYear[toID].append((fromID,year));
            

projectCitationsIndices = {}
projectReferencesIndices = {}

projectCitationsEdges = {}
projectReferencesEdges = {}

for projectName,(indices,citationsPerYear) in projectCitations.items():
    citationsEdges = []
    citationsSet = set()
    projectCitationsEdges[projectName] = citationsEdges
    projectCitationsIndices[projectName] = citationsSet
    for paperIndex in indices:
        paperID = index2magID[paperIndex]
        if paperID in MAGID2CitationYear:
            for toID,year in MAGID2CitationYear[paperID]:
                citationsEdges.append((paperID,toID))
                citationsSet.add(toID)

for projectName,(indices,referencesPerYear) in projectReferences.items():
    referencesEdges = []
    referencesSet = set()
    projectReferencesEdges[projectName] = referencesEdges
    projectReferencesIndices[projectName] = referencesSet
    for paperIndex in indices:
        paperID = index2magID[paperIndex]
        if paperID in MAGID2ReferenceYear:
            for fromID,year in MAGID2ReferenceYear[paperID]:
                referencesEdges.append((paperID,fromID))
                referencesSet.add(fromID)


HCAAffiliationsPerYear = {};
HuBMapAffiliationsPerYear = {};
HGPAffiliationsPerYear = {};

HCAAuthorsPerYear = {};
HuBMapAuthorsPerYear = {};
HGPAuthorsPerYear = {};

projectAuthorAffiliations = {
    "HCA":(HCAProjectMAGIndices,HCAAffiliationsPerYear,HCAAuthorsPerYear),
    "HuBMAP":(HBMapProjectMAGIndices,HuBMapAffiliationsPerYear,HuBMapAuthorsPerYear),
    "HuBMAP+HCA":(set(HBMapProjectMAGIndices).union(set(HCAProjectMAGIndices)),HuBMapAffiliationsPerYear,HuBMapAuthorsPerYear),
    "HGP":(HGPProjectMAGIndices,HGPAffiliationsPerYear,HGPAuthorsPerYear)
}



allMAGIDs = {index2magID[entry] for entry in HCAProjectMAGIndices|HBMapProjectMAGIndices|HGPProjectMAGIndices}

MAGID2AuthorsIDs = {}
MAGID2AffiliationIDs = {}

estimatedCount = 655732564;# Used just to display status
with open(PJ(MAGPath,"PaperAuthorAffiliations.txt"),"rt") as fd:
    pbar = tqdm(total=estimatedCount);
    for line in fd:
        pbar.update(1);
        entries = line.split("\t");
        paperID = int(entries[0]);
        if(paperID in allMAGIDs):
            paperAuthorID = int(entries[1]);
            if(entries[2].isdigit()):
                paperAffiliationID = int(entries[2]);
            else:
                paperAffiliationID=0;
            authorOrder = int(entries[3]);
            paperIndex = magID2Index[paperID]
            paperYear = index2FirstYear[paperIndex]
            if(paperID not in MAGID2AuthorsIDs):
                MAGID2AuthorsIDs[paperID] = [];

            if(paperID not in MAGID2AffiliationIDs):
                MAGID2AffiliationIDs[paperID] = [];
            
            MAGID2AuthorsIDs[paperID].append(paperAuthorID);
            MAGID2AffiliationIDs[paperID].append(paperAffiliationID);
            
            for projectName,(indices,affiliationsPerYear,authorsPerYear) in projectAuthorAffiliations.items():
                if(paperIndex in indices):
                    if(paperYear not in authorsPerYear):
                        authorsPerYear[paperYear] = set();
                    authorsPerYear[paperYear].add(paperAuthorID);
                    if(paperAffiliationID):
                        if(paperYear not in affiliationsPerYear):
                            affiliationsPerYear[paperYear] = set();
                        affiliationsPerYear[paperYear].add(paperAffiliationID);



indicesByProject = {
"HCA" : HCAProjectMAGIndices,
"HuBMAP" : HBMapProjectMAGIndices,
"HuBMAP+HCA" : set(HBMapProjectMAGIndices).union(set(HCAProjectMAGIndices)),
"HGP" : HGPProjectMAGIndices
}
          
magIDsByProject = {}
allMAGIDs = set()
for projectName,indices in indicesByProject.items():
    magIDsByProject[projectName] = {index2magID[index] for index in indices}
    allMAGIDs.update(magIDsByProject[projectName])

exportFilesByProject = {}
for projectName,indices in indicesByProject.items():
    exportFilesByProject[projectName] = open(PJ("..","Data", "Publications","Biomedical_Papers_%s.tsv"%projectName),"w")
    headers = [entryName for entryName,_ in papersDataTypes]
    headers.append("Author IDs")
    headers.append("Affiliation IDs")
    headers.append("Citation IDs")
    headers.append("Citation Years")
    exportFilesByProject[projectName].write("\t".join(headers));
    exportFilesByProject[projectName].write("\n");
    

with open(PJ(MAGPath,"Papers.txt"),"rt") as fd:
    pbar = tqdm(total=estimatedCount);
    pbar2 = tqdm(desc="matches");
    for line in fd:
        pbar.update(1);
        entries = line.strip().split("\t");
        paperID = int(entries[0]);
        if(paperID in allMAGIDs):
            pbar2.update(1)
            for projectName,magIDs in magIDsByProject.items():
                if(paperID in magIDs):
                    exportFilesByProject[projectName].write(line.strip());
                    exportFilesByProject[projectName].write("\t%s"%";".join([str(entry) for entry in MAGID2AuthorsIDs[paperID] if entry!=0]))
                    exportFilesByProject[projectName].write("\t%s"%";".join([str(entry) for entry in MAGID2AffiliationIDs[paperID] if entry!=0]))
                    if(paperID in MAGID2CitationYear):
                        exportFilesByProject[projectName].write("\t%s"%";".join([str(entry) for entry,year in MAGID2CitationYear[paperID] if entry!=0]))
                        exportFilesByProject[projectName].write("\t%s"%";".join([str(year) for entry,year in MAGID2CitationYear[paperID] if year!=0]))
                    else:
                        exportFilesByProject[projectName].write("\t");
                        exportFilesByProject[projectName].write("\t");
                    exportFilesByProject[projectName].write("\n")
for projectName,indices in indicesByProject.items():
    exportFilesByProject[projectName].close()


# Loading MAG Data
journalIndex2MAGID = np.loadtxt(PJ(dataPath,"MAGJournalIndex2ID.txt.gz"),dtype=int)
journalMAGID2Index = dictFromList(journalIndex2MAGID)
journalMAGID2Index = {ID:index for index,ID in enumerate(journalIndex2MAGID)};
with gzip.open(PJ(dataPath,"MAGJournalNames.txt.gz"),"rt") as fd:
    journalMAGNames = [line.strip() for line in fd]
    
with gzip.open(PJ(dataPath,"MAGJournalLongNames.txt.gz"),"rt") as fd:
    journalMAGLongNames = [line.strip() for line in fd]
    
with gzip.open(PJ(dataPath,"MAGJournalRankings.txt.gz"),"rt") as fd:
    journalMAGRankings = [int(line.strip()) for line in fd]
    
with gzip.open(PJ(dataPath,"MAGJournalPublishers.txt.gz"),"rt") as fd:
    journalMAGPublishers = [line.strip() for line in fd]
    
with gzip.open(PJ(dataPath,"MAGJournalPaperCounts.txt.gz"),"rt") as fd:
    journalMAGPaperCounts = [int(line.strip()) for line in fd]
    
with gzip.open(PJ(dataPath,"MAGJournalISSN.txt.gz"),"rt") as fd:
    journalMAGISSN = [line.strip() for line in fd]


dfBioMed = {
    "HuBMAP+HCA": pd.read_csv(PJ("..","Data","Publications","Biomedical_Papers_HuBMAP+HCA.tsv"),sep="\t"),
    "HGP": pd.read_csv(PJ("..","Data","Publications","Biomedical_Papers_HGP.tsv"),sep="\t")
}

#Fixing journal names
for projectName,df in dfBioMed.items():
    df["Journal Name"] = [journalMAGNames[journalMAGID2Index[int(ID)]] if ID else "NA" for ID in df["JournalId"]]
    df["Journal Long Name"] = [journalMAGLongNames[journalMAGID2Index[int(ID)]] if ID else "NA" for ID in df["JournalId"]]
    df.to_csv(PJ("..","Data", "Publications","Biomedical_Papers_%s.csv"%projectName))





import re
def canonizeName(name):
  name = name.strip("\"").strip("\'")
  name = name.lower().replace("."," ").replace("  "," ").replace("  "," ").strip()
  name = re.sub('^nat ','nature ',name)
  name = re.sub('journal ','j ',name)
  names = name.split()
  return " ".join([subname[0:3] if len(subname)==4 else subname  for subname in names])

# Loading dictionaries for Journal matching
with open("../Data/ScienceMapJournalDictionary_Map2ID.json","rt") as fd:
    allToMapID = ujson.load(fd)

with open("../Data/ScienceMapJournalDictionary_Map2Name.json","rt") as fd:
    allToMapName = ujson.load(fd)

with open("../Data/ScienceMapJournalDictionary_ISSN2ID.json","rt") as fd:
    ISSNToMapID = ujson.load(fd)

from collections import Counter
noMatch = Counter()
def venueName2MapName(origName):
  name = canonizeName(origName)
  if(name in allToMapName):
    return allToMapName[name]
  noMatch.update([origName])
  return "NA"

def venueName2MapID(origName):
  name = canonizeName(origName)
  if(name in allToMapID):
    return allToMapID[name]
  noMatch.update([origName])
  return "NA"


def venueISSN2MapID(origISSN):
  name = origISSN.replace("-","").lower()
  if(origISSN in ISSNToMapID):
    return ISSNToMapID[origISSN]
  return "NA"


def getVenueData(paperID):
    journalID = index2JournalID[magID2Index[paperID]]
    if(journalID<0):
        return "NA","NA"
    journalIndex = journalMAGID2Index[journalID]
    longName = journalMAGLongNames[journalIndex]
    name = journalMAGNames[journalIndex]
    issn = journalMAGISSN[journalIndex]
    mapID = venueISSN2MapID(issn)
    if(mapID=="NA"):
        mapID = venueName2MapID(issn)
    if(mapID=="NA"):
        mapID = venueName2MapID(name)
    if(mapID=="NA"):
        mapID = venueName2MapID(longName)
    return name,mapID

def getYearData(paperID):
    return index2Year[magID2Index[paperID]]

minYear = 1980
maxYear = 2020

# Saving all publication data
for projectName, edgeEntries in tqdm(projectCitationsEdges.items(), desc="Project"):
  edgesData = {
      "Citing ID": [],
      "Citing Venue Name": [],
      "Citing Venue SciMap ID": [],
      "Citing Publication Year": [],
      "Cited ID": [],
      "Cited Venue Name": [],
      "Cited Venue SciMap ID": [],
      "Cited Publication Year": [],
  }
  for (citedEntryID,citingEntryID) in tqdm(edgeEntries):
    citedEntryYear = 0
    citedEntryVenueName,citedEntryVenueMapID = getVenueData(citedEntryID)
    citedEntryYear = getYearData(citedEntryID)
    if(citedEntryYear<minYear or citedEntryYear>maxYear):
      continue
    #Received Citations
    citingEntryVenueName,citingEntryVenueMapID = getVenueData(citingEntryID)
    citingYear = getYearData(citingEntryID)
    if(citingYear<minYear or citingYear>maxYear):
        continue
    edgesData["Citing ID"].append(citingEntryID)
    edgesData["Citing Venue Name"].append(citingEntryVenueName)
    edgesData["Citing Venue SciMap ID"].append(citingEntryVenueMapID)
    edgesData["Citing Publication Year"].append(citingYear)
    edgesData["Cited ID"].append(citedEntryID)
    edgesData["Cited Venue Name"].append(citedEntryVenueName)
    edgesData["Cited Venue SciMap ID"].append(citedEntryVenueMapID)
    edgesData["Cited Publication Year"].append(citedEntryYear)
  dfEdges = pd.DataFrame.from_dict(edgesData)
  dfEdges.to_csv(PJ("..","Data","ToMapOfScience","Biomedical_Edges_Citing_%s_tomap.csv.gz"%(projectName)),index=False)




# Saving all publication data
for projectName, edgeEntries in tqdm(projectReferencesEdges.items(), desc="Project"):
  edgesData = {
      "Citing ID": [],
      "Citing Venue Name": [],
      "Citing Venue SciMap ID": [],
      "Citing Publication Year": [],
      "Cited ID": [],
      "Cited Venue Name": [],
      "Cited Venue SciMap ID": [],
      "Cited Publication Year": [],
  }
  for (citingEntryID,citedEntryID) in tqdm(edgeEntries):
    citedEntryYear = 0
    citedEntryVenueName,citedEntryVenueMapID = getVenueData(citedEntryID)
    citedEntryYear = getYearData(citedEntryID)
    if(citedEntryYear<minYear or citedEntryYear>maxYear):
      continue
    #Received Citations
    citingEntryVenueName,citingEntryVenueMapID = getVenueData(citingEntryID)
    citingYear = getYearData(citingEntryID)
    if(citingYear<minYear or citingYear>maxYear):
        continue
    edgesData["Citing ID"].append(citingEntryID)
    edgesData["Citing Venue Name"].append(citingEntryVenueName)
    edgesData["Citing Venue SciMap ID"].append(citingEntryVenueMapID)
    edgesData["Citing Publication Year"].append(citingYear)
    edgesData["Cited ID"].append(citedEntryID)
    edgesData["Cited Venue Name"].append(citedEntryVenueName)
    edgesData["Cited Venue SciMap ID"].append(citedEntryVenueMapID)
    edgesData["Cited Publication Year"].append(citedEntryYear)
  dfEdges = pd.DataFrame.from_dict(edgesData)
  dfEdges.to_csv(PJ("..","Data","ToMapOfScience","Biomedical_Edges_Referenced_%s_tomap.csv.gz"%(projectName)),index=False)




allProjectsIDs = set()
for projectName in ["HGP","HuBMAP+HCA"]:
    dfCiting = pd.read_csv(PJ("..","Data","ToMapOfScience","Biomedical_Edges_Citing_%s_tomap.csv.gz"%(projectName)))
    dfReferences = pd.read_csv(PJ("..","Data","ToMapOfScience","Biomedical_Edges_Referenced_%s_tomap.csv.gz"%(projectName)))
    dfPapers = pd.read_csv(PJ("..","Data","ToMapOfScience","Biomedical_Papers_%s_tomap.csv"%(projectName)))
    allProjectsIDs.update(list(dfCiting["Citing ID"]))
    allProjectsIDs.update(list(dfCiting["Cited ID"]))
    allProjectsIDs.update(list(dfReferences["Citing ID"]))
    allProjectsIDs.update(list(dfReferences["Cited ID"]))
    allProjectsIDs.update(list(dfPapers['PaperId']))


allProjectsID2Title = {}
for magID in allProjectsIDs:
    title = index2Title[magID2Index[magID]]
    allProjectsID2Title[magID] = title

with open(PJ("..","Data","Biomedical_MAGID2Title.json"),"wt") as fd:
    json.dump(allProjectsID2Title,fd)


