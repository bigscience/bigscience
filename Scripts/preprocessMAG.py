from tqdm.auto import tqdm
import os
from os.path import join as PJ
import bgzf
import struct
import os
import numpy as np
import subprocess
import gzip


# Set the PATH to MAG Folder
MAGPath = "../Data/MAG/"

minPaperCount = 1;
rebuildAll = False


dataPath = PJ("..","Data","Processed")
temporaryPath = PJ("..","Temp")
os.makedirs(dataPath, exist_ok=True)
os.makedirs(temporaryPath, exist_ok=True)


def dictFromList(aList):
    return {aList[i]:i for i in range(len(aList))}


print("\n Reading and Saving Journal Information");
# OK
# Processing Journal metadata
index2JournalID = [];
journalNames = [];
journalLongNames = [];
journalRankings = [];
journalPublishers = [];
journalPaperCounts = [];
journalISSN = [];
totalJournalCount = 0;
totalBigCount = 0;
totalISSNCount = 0;
with open(PJ(MAGPath,"Journals.txt"),"rt") as fd:
    for line in tqdm(fd):
        entries = line.split("\t");
        paperCount = int(entries[7]);
        issn = entries[4].strip();
        totalJournalCount+=1;
        if(paperCount>minPaperCount):
            totalBigCount+=1;
            if(issn):
                totalISSNCount+=1;
            index2JournalID.append(int(entries[0].strip()));
            journalRankings.append(int(entries[1].strip()));
            journalNames.append(entries[2].strip());
            journalLongNames.append(entries[3].strip());
            journalPublishers.append(entries[5].strip());
            journalISSN.append(issn);
            journalPaperCounts.append(int(entries[7].strip()));

journalID2Index = dictFromList(index2JournalID);
np.savetxt(PJ(dataPath,"MAGJournalIndex2ID.txt.gz"),index2JournalID,"%d")
np.savetxt(PJ(dataPath,"MAGJournalNames.txt.gz"),journalNames,"%s")
np.savetxt(PJ(dataPath,"MAGJournalLongNames.txt.gz"),journalLongNames,"%s")
np.savetxt(PJ(dataPath,"MAGJournalRankings.txt.gz"),journalRankings,"%d")
np.savetxt(PJ(dataPath,"MAGJournalPublishers.txt.gz"),journalPublishers,"%s")
np.savetxt(PJ(dataPath,"MAGJournalPaperCounts.txt.gz"),journalPaperCounts,"%d")
np.savetxt(PJ(dataPath,"MAGJournalISSN.txt.gz"),journalISSN,"%s")

print("Total With ISSN: %.0f%%"%(totalISSNCount/totalBigCount*100))
print("Final journals Count: %d"%len(index2JournalID))





print("\n Reading and Saving Paper 2 Journal Information");
estimatedCount = 242387326;# Used just to display status
paper2journalYear =  {}
paper2journalYearBGZPath = PJ(dataPath,"MAGPaper2JournalYear.bgz");
if(not rebuildAll and os.path.exists(paper2journalYearBGZPath)):
    print("Reading from BGZ file...");
    pbar = tqdm(total=estimatedCount);
    with bgzf.open(paper2journalYearBGZPath,"rb") as fd:
        while True:
            pbar.update(1);
            data = fd.read(8*3);
            if(len(data)==8*3):
                paperID, journal, year = struct.unpack("<QQQ",data);
                paper2journalYear[paperID] = (journal, year);
            else:
                break;
else:
    print("Reading from RAW file...");
    with open(PJ(MAGPath,"Papers.txt"),"rt") as fd:
        pbar = tqdm(total=estimatedCount);
        for line in fd:
            pbar.update(1);
            entries = line.split("\t");
            try:
                paperID = int(entries[0]);
                paperJournal = int(entries[11]);
                paperYear = int(entries[7]);
                if(paperJournal>0):
                    paper2journalYear[paperID] = (paperJournal,paperYear);
            except:
                pass;
    print("Saving from BGZ file...");
    with bgzf.open(paper2journalYearBGZPath,"wb") as fd:
        for paperID in tqdm(paper2journalYear):
            journal, year = paper2journalYear[paperID];
            fd.write(struct.pack("<QQQ",paperID,journal,year));




print("\n Reading and Saving Journal Information");

estimatedCount = 655732564;# Used just to display status
journalAuthorYearPaperPath = PJ(dataPath,"MAGJournalAuthorYearPaperOrder.txt");
if(not rebuildAll and os.path.exists(journalAuthorYearPaperPath)):
    print("Using saved Journal-Author-Year-Paper table...");
else:
    print("Generating Journal-Author-Year-Paper table...");
    with open(journalAuthorYearPaperPath,"w") as outfd:
        with open(PJ(MAGPath,"PaperAuthorAffiliations.txt"),"rt") as fd:
            pbar = tqdm(total=estimatedCount);
            for line in fd:
                pbar.update(1);
                entries = line.split("\t");
    #             try:
                paperID = int(entries[0]);
                paperAuthorID = int(entries[1]);
                if(entries[2].isdigit()):
                    paperAffiliationID = int(entries[2]);
                else:
                    paperAffiliationID=0;
                authorOrder = int(entries[3]);
                if(paperID in paper2journalYear):
                    journalID,year = paper2journalYear[paperID];
                    outfd.write("%d\t%d\t%d\t%d\t%d\n"%(journalID,paperAuthorID,year,paperID,authorOrder));
    #             except:


import subprocess
 
sortedJournalAuthorYearPaperPath = PJ(dataPath,"MAGJournalAuthorYearPaperOrder_byJournal.txt");
compressedJournalAuthorYearPaperPath = PJ(dataPath,"MAGJournalAuthorYearPaperOrder_byJournal.bgz");

#!sort --parallel=20 -T../../Temp/ -t$'\t' -nk1 -nk2 -nk4 ../../Data/ProcessedNew/JournalAuthorYearPaper.txt > ../../Data/ProcessedNew/JournalAuthorYearPaper_byJournal.txt


if(not rebuildAll and (os.path.exists(compressedJournalAuthorYearPaperPath) or os.path.exists(sortedJournalAuthorYearPaperPath))):
    print("Using Journal-Author-Year-Paper sorted table...");
else:
    print("Generating Journal-Author-Year-Paper sorted table...");
    with open(sortedJournalAuthorYearPaperPath,"w") as fd:
        subprocess.run(["sort", "--parallel=20", "-T%s"%temporaryPath,"-t","\t","-nk1","-nk2","-nk4",journalAuthorYearPaperPath],stdout=fd)


if(not rebuildAll and os.path.exists(compressedJournalAuthorYearPaperPath)):
    print("Using Journal-Author-Year-Paper compressed file...");
else:
    print("Generating Journal-Author-Year-Paper compressed file...");
    estimatedCount = 287137930;# Used just to display status
    with open(sortedJournalAuthorYearPaperPath,"r") as finput:
        with bgzf.open(compressedJournalAuthorYearPaperPath,"wb") as foutput:
            pbar = tqdm(total=287137930);
            for line in finput:
                pbar.update(1);
                entries = line.split("\t");
                journalID = int(entries[0]);
                paperAuthorID = int(entries[1]);
                year = int(entries[2]);
                paperID = int(entries[3]);
                authorOrder = int(entries[4]);
                foutput.write(struct.pack("<QQQQQ",journalID,paperAuthorID,year,paperID,authorOrder));

print("\nSorting Author list by AuthorID...");

#WRITE
#Authors
dataRAWFilePath = PJ(MAGPath,"Authors.txt");
sortedFilePath = PJ(dataPath,"MAGAuthors_byAuthorID.txt");

# !sort --parallel=20 --compress-program=bgzip -T../../Data/Temporary -t \t -nk1 /home/filsilva/Journal2Journal/Data/Raw/Authors.txt > ../../Data/ProcessedNew/Authors_byAuthorID.txt

with open(sortedFilePath,"wb") as fd: #
    subprocess.run(["sort", "--parallel=20", "-T%s"%temporaryPath,"-t","\t","-nk1",dataRAWFilePath],stdout=fd)



print("\nProcessing and saving author information...");

#WRITE
sortedAuthorsFilePath = PJ(dataPath,"MAGAuthors_byAuthorID.txt");
bgzAuthorsFilePath = PJ(dataPath,"MAGAuthors.bgz");

authorsDataTypes = [
("AuthorId", int),
("Rank", int),
("NormalizedName", str),
("DisplayName", str),
("LastKnownAffiliationId", int),
("PaperCount", int	),
("PaperFamilyCount", int), #NEW
("CitationCount", int),
("CreatedDate", str),
]

estimatedCount = 238938563;
currentPaperIndex=0;
with open(sortedAuthorsFilePath,"rb") as infd:
    with bgzf.open(bgzAuthorsFilePath,"wb") as outfd:
        pbar = tqdm(total=estimatedCount);
        aggregatedData = b''
        for line in infd:
            pbar.update(1);
            entries = line.strip().split(b"\t");
            paperID = int(entries[0]);
            entryData = struct.pack("<q",currentPaperIndex);
            currentPaperIndex+=1;
            for (typeIndex,(typeName,typeType)) in enumerate(authorsDataTypes):
                entryValue = entries[typeIndex]
                if(typeType==int):
                    if(entryValue):
                        entryData += struct.pack("<q",int(entryValue));
                    else:
                        entryData += struct.pack("<q",-1);
                else:
                    entryData += struct.pack("<q",len(entryValue));
                    entryData += entryValue;
            finalData = (struct.pack("<q",len(entryData))+entryData)
            aggregatedData+=finalData;
            if(len(aggregatedData)>2000):
                outfd.write(aggregatedData);
                aggregatedData=b''
#             if(currentPaperIndex>100000):
#                 break
        if(len(aggregatedData)>0):
            outfd.write(aggregatedData);
            aggregatedData=b''
            

print("\nProcessing and saving references information...");

#Processing citation data
#WRITE
import subprocess
import gzip
#References
dataRAWFilePath = PJ(MAGPath,"PaperReferences.txt");
sortedFilePath = PJ(dataPath,"MAGPaperReferencesByFrom.txt");

#!sort --parallel=20 -T./Temp/ -t$'\t' -nk1 -nk2 -nk4 JournalAuthorYearPaper.txt > JournalAuthorYearPaper_byJournal.txt

with open(sortedFilePath,"wb") as fd: #
    subprocess.run(["sort", "--parallel=20", "-T%s"%temporaryPath,"-t","\t","-nk1","-nk2",dataRAWFilePath],stdout=fd)


dataRAWFilePath = PJ(MAGPath,"PaperReferences.txt");
sortedFilePath = PJ(dataPath,"MAGPaperReferencesByTo.txt");

#!sort --parallel=20 -T./Temp/ -t$'\t' -nk1 -nk2 -nk4 JournalAuthorYearPaper.txt > JournalAuthorYearPaper_byJournal.txt

with open(sortedFilePath,"wb") as fd: #
    subprocess.run(["sort", "--parallel=20", "-T%s"%temporaryPath,"-t","\t","-nk2","-nk1",dataRAWFilePath],stdout=fd)
    

print("\nProcessing and saving Paper information...");

#WRITE
#Papers
dataRAWFilePath = PJ(MAGPath,"Papers.txt");
sortedFilePath = PJ(dataPath,"MAGPapersByPaper.txt");

#!sort --parallel=20 -T./Temp/ -t$'\t' -nk1 -nk2 -nk4 JournalAuthorYearPaper.txt > JournalAuthorYearPaper_byJournal.txt

with open(sortedFilePath,"wb") as fd: #
    subprocess.run(["sort", "--parallel=20", "-T%s"%temporaryPath,"-t","\t","-nk1","-nk8","-nk12",dataRAWFilePath],stdout=fd)



print("\nProcessing and saving Paper information...");


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


#WRITE
estimatedCount = 238938563;
currentPaperIndex=0;
with open(sortedPapersFilePath,"rb") as infd:
    with bgzf.open(bgzPapersFilePath,"wb") as outfd:
        pbar = tqdm(total=estimatedCount);
        aggregatedData = b''
        for line in infd:
            pbar.update(1);
            entries = line.strip().split(b"\t");
            paperID = int(entries[0]);
            entryData = struct.pack("<q",currentPaperIndex);
            currentPaperIndex+=1;
            for (typeIndex,(typeName,typeType)) in enumerate(papersDataTypes):
                entryValue = entries[typeIndex]
                if(typeType==int):
                    if(entryValue):
                        entryData += struct.pack("<q",int(entryValue));
                    else:
                        entryData += struct.pack("<q",-1);
                else:
                    entryData += struct.pack("<q",len(entryValue));
                    entryData += entryValue;
            finalData = (struct.pack("<q",len(entryData))+entryData)
            aggregatedData+=finalData;
            if(len(aggregatedData)>2000):
                outfd.write(aggregatedData);
                aggregatedData=b''
#             if(currentPaperIndex>100000):
#                 break
        if(len(aggregatedData)>0):
            outfd.write(aggregatedData);
            aggregatedData=b''    






print("\nProcessing and saving Paper indices...");
#WRITE
estimatedCount = 238938563;
magID2Index = {};
bgzPapersIndicesFilePath = PJ(dataPath,"MAGPapersIndices.bgz");
with bgzf.open(bgzPapersFilePath,"rb") as infd:
    with bgzf.open(bgzPapersIndicesFilePath,"wb") as outfd:
        pbar = tqdm(total=estimatedCount);
        aggregatedData = b''
        while True:
            pbar.update(1);
            seekPosition = infd.tell();
            lengthData = infd.read(8);
            if(len(lengthData)==8):
                length = struct.unpack("<q",lengthData)[0];
            else:
                break;
            data = infd.read(length);
            paperIndex = struct.unpack("<q",data[0:8])[0];
            paperID = struct.unpack("<q",data[8:16])[0];
            magID2Index[paperID]= paperIndex
            entryData = struct.pack("<qqq",paperIndex,seekPosition,paperID);
            aggregatedData+=entryData;
            if(len(aggregatedData)>2000):
                outfd.write(aggregatedData);
                aggregatedData=b''
        if(len(aggregatedData)>0):
            outfd.write(aggregatedData);
            aggregatedData=b''


print("\nc"); #WRITE" #references FromTo
estimatedCount = 1600002313/79684807;
sortedReferencesFromToList = PJ(dataPath,"MAGPaperReferencesByFrom.txt");
bgzReferencesFromToPath = PJ(dataPath,"MAGPaperReferencesFromTo.bgz");
entriesCount = 0;
with open(sortedReferencesFromToList,"r") as infd:
    with bgzf.open(bgzReferencesFromToPath,"wb") as outfd:
        pbar = tqdm(total=estimatedCount);
        aggregatedData = b''
        previousIndex = -1;
        entryData = b'';
        entriesCount=0;
        for line in infd:
            pbar.update(1);
            fromID, toID = line.strip().split("\t");
            
            fromID = int(fromID);
            toID = int(toID);
            
            if(fromID in magID2Index):
                fromIndex = magID2Index[fromID]
            else:
                fromIndex=-1;
                continue;
                
            if(toID in magID2Index):
                toIndex = magID2Index[toID]
            else:
                toIndex=-1;
                
            if(previousIndex==-1):
                previousIndex=fromIndex;
                entryData = struct.pack("<q",fromIndex);
                
            if(fromIndex==previousIndex):
                entryData +=struct.pack("<q",toIndex);
            else:
                aggregatedData+=struct.pack("<q",len(entryData))+entryData;
                if(len(aggregatedData)>2000):
                    outfd.write(aggregatedData);
                    aggregatedData=b''
                entryData =struct.pack("<q",fromIndex);
                entryData +=struct.pack("<q",toIndex);
            previousIndex=fromIndex;
            entriesCount+=1
#             if(entriesCount>100000):
#                 break;
        aggregatedData+=struct.pack("<q",len(entryData))+entryData;
        if(len(aggregatedData)>0):
            outfd.write(aggregatedData);
            aggregatedData=b''
# print("Reading from RAW file...");
# with open(PJ(MAGPath,"Papers.txt")) as fd:
#         for line in tqdm(fd):
#             entries = line.split("\t");
#             try:
#                 paperID = int(entries[0]);
#                 paperJournal = int(entries[10]);
#                 paperYear = int(entries[7]);
#                 if(paperJournal>0):
#                     paper2journalYear[paperID] = (paperJournal,paperYear);
#             except:
#                 pass;
#     print("Saving from BGZ file...");
#     with bgzf.open(paper2journalYearBGZPath,"wb") as fd:
#         for paperID in tqdm(paper2journalYear):
#             journal, year = paper2journalYear[paperID];
#             fd.write(struct.pack("<QQQ",paperID,journal,year));



#WRITE
#references ToFrom
estimatedCount = 1600002313;
sortedReferencesToFromList = PJ(dataPath,"MAGPaperReferencesByTo.txt");
bgzReferencesToFromPath = PJ(dataPath,"MAGPaperReferencesToFrom.bgz");
entriesCount = 0;
with open(sortedReferencesToFromList,"r") as infd:
    with bgzf.open(bgzReferencesToFromPath,"wb") as outfd:
        pbar = tqdm(total=estimatedCount);
        aggregatedData = b''
        previousIndex = -1;
        entryData = b'';
        entriesCount=0;
        for line in infd:
            pbar.update(1);
            fromID, toID = line.strip().split("\t");
            
            fromID = int(fromID);
            toID = int(toID);
            
            if(toID in magID2Index):
                toIndex = magID2Index[toID]
            else:
                toIndex=-1;
                continue;
                
            if(fromID in magID2Index):
                fromIndex = magID2Index[fromID]
            else:
                fromIndex=-1;
                
            if(previousIndex==-1):
                previousIndex=toIndex;
                entryData = struct.pack("<q",toIndex);
                
            if(toIndex==previousIndex):
                entryData +=struct.pack("<q",fromIndex);
            else:
                aggregatedData+=struct.pack("<q",len(entryData))+entryData;
                if(len(aggregatedData)>2000):
                    outfd.write(aggregatedData);
                    aggregatedData=b''
                entryData =struct.pack("<q",toIndex);
                entryData +=struct.pack("<q",fromIndex);
            previousIndex=toIndex;
            entriesCount+=1
#             if(entriesCount>100000):
#                 break;
        aggregatedData+=struct.pack("<q",len(entryData))+entryData;
        if(len(aggregatedData)>0):
            outfd.write(aggregatedData);
            aggregatedData=b''







