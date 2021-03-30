import gzip
import pandas
import pymarc
#Please load the supplied version of pymarc (install using pip install ./)

import numpy as np

import ujson
import json
import bgzf
import struct
import os

from tqdm.auto import tqdm
from os.path import join as PJ

#Set to the location where INSPIRE dump is.
inspireDumpPath = PJ("..","Data","INSPIRE","20210108")
processedDataPath = PJ(inspireDumpPath,"Processed")
os.makedirs(processedDataPath, exist_ok=True)

def getTagSubtag(data,subtag,onErrorParent=True):
    if(isinstance(data,dict)):
      value = None
#       try: 
      if(subtag not in data):
        value = None;
      else:
        value = data[subtag];
#       except:
#         print((subtag,data));
#         raise error;
      return value;
    else:
      if(onErrorParent):
        return data;
      else:
        return None;

def getFirst(data,tag):
  value = None;
  if(tag in data):
    if(isinstance(data[tag],list)):
      value = data[tag][0];
    else:
      value = data[tag];
  return value;
  

def getAll(data,tag):
  value = [];
  if(tag in data):
    if(isinstance(data[tag],list)):
      value = data[tag];
    else:
      value = [data[tag]];
  return value;


def getEntry(data,tag,subtags=None,isList=False, onErrorParent=True):
  if(tag not in data):
    return None;
  if(subtags is not None):
    if(isList):
      dataList = getAll(data,tag);
      resultList = [];
      for dataValue in dataList:
        if(isinstance(subtags,dict)):
          resultEntry = {}
          for key in subtags:
            subTagResult = getTagSubtag(dataValue,subtags[key],onErrorParent);
            if(subTagResult):
              resultEntry[key] = subTagResult;
          resultList.append(resultEntry);
        else:
          subTagResult = getTagSubtag(dataValue,subtags,onErrorParent);
          if(subTagResult):
            resultList.append(subTagResult);
      return resultList
    else:
      dataValue = getFirst(data,tag);
      if(isinstance(subtags,dict)):
        resultEntry = {}
        for key in subtags:
          subTagResult = getTagSubtag(dataValue,subtags[key],onErrorParent);
          if(subTagResult):
            resultEntry[key] = subTagResult;
        return resultEntry;
      else:
        subTagResult = getTagSubtag(dataValue,subtags,onErrorParent);
        if(subTagResult):
          return subTagResult;
  else:
    if(isList):
      return getAll(data,tag);
    else:
      return getFirst(data,tag);

    
def processHEP(entryData):
  outData = {}
  
  propertyName = "ID"
  outData[propertyName] = getEntry(
    entryData,
    "001",
    subtags=None,
    isList=False,
    onErrorParent=True
  )
  
  propertyName = "DOI"
  outData[propertyName] = getEntry(
    entryData,
    "024",
    subtags={
      "Value": "a",
      "Type": "a",
    },
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Category"
  outData[propertyName] = getEntry(
    entryData,
    "037",
    subtags="c",
    isList=True,
    onErrorParent=False
  )
  
  propertyName = "FirstAuthor"
  outData[propertyName] = getEntry(
    entryData,
    "100",
    subtags={
      "ID": "x",
      "Name": "a",
      "Institution ID": "z",
      "ORCID": "k",
      "Email": "m",
    },
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Authors"
  outData[propertyName] = getEntry(
    entryData,
    "700",
    subtags={
      "ID": "x",
      "Name": "a",
      "Institution ID": "z",
      "ORCID": "k",
      "Email": "m",
    },
    isList=True,
    onErrorParent=False
  )
  
  propertyName = "Title"
  outData[propertyName] = getEntry(
    entryData,
    "245",
    subtags="a",
    isList=False,
    onErrorParent=True
  )
  
  propertyName = "PublicationDate"
  outData[propertyName] = getEntry(
    entryData,
    "260",
    subtags="c",
    isList=False,
    onErrorParent=True
  )

  propertyName = "PreprintDate"
  outData[propertyName] = getEntry(
    entryData,
    "269",
    subtags="c",
    isList=False,
    onErrorParent=True
  )
  
  propertyName = "NumberOfPages"
  outData[propertyName] = getEntry(
    entryData,
    "300",
    subtags="a",
    isList=False,
    onErrorParent=True
  )
  
  propertyName = "Degree"
  outData[propertyName] = getEntry(
    entryData,
    "500",
    subtags={
      "Type":"b",
      "Institution":"b",
      "Year":"d",
      "Institution ID":"z",
    },
    isList=False,
    onErrorParent=False
  )

#     outData[propertyName] = getEntry(
#       entryData,
#       "520",
#       subtags="a",
#       isList=False,
#       onErrorParent=True
#     )
    
  propertyName = "Classification"
  outData[propertyName] = getEntry(
    entryData,
    "650",
    subtags="a",
    isList=True,
    onErrorParent=False
  )
  
  propertyName = "Keywords"
  outData[propertyName] = getEntry(
    entryData,
    "653",
    subtags="a",
    isList=True,
    onErrorParent=True
  )
  
  propertyName = "Experiment"
  outData[propertyName] = getEntry(
    entryData,
    "693",
    subtags="e",
    isList=True,
    onErrorParent=False
  )
  
  propertyName = "Accelerator"
  outData[propertyName] = getEntry(
    entryData,
    "693",
    subtags="a",
    isList=True,
    onErrorParent=False
  )
  
  propertyName = "Beam line"
  outData[propertyName] = getEntry(
    entryData,
    "693",
    subtags="b",
    isList=True,
    onErrorParent=False
  )
  
  propertyName = "ControlledKeywords"
  outData[propertyName] = getEntry(
    entryData,
    "695",
    subtags="a",
    isList=True,
    onErrorParent=True
  )
  
  propertyName = "ControlledKeywords"
  outData[propertyName] = getEntry(
    entryData,
    "695",
    subtags="a",
    isList=True,
    onErrorParent=False
  )
  
  propertyName = "EnergyRange"
  outData[propertyName] = getEntry(
    entryData,
    "695",
    subtags="e",
    isList=True,
    onErrorParent=False
  )
  
  propertyName = "ThesisSupervisor"
  outData[propertyName] = getEntry(
    entryData,
    "701",
    subtags="a",
    isList=False,
    onErrorParent=True
  )
  
  propertyName = "Collaborations"
  outData[propertyName] = getEntry(
    entryData,
    "710",
    subtags="g",
    isList=True,
    onErrorParent=True
  )
  
  propertyName = "Venue Name"
  outData[propertyName] = getEntry(
    entryData,
    "773",
    subtags="p",
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Venue ISBN"
  outData[propertyName] = getEntry(
    entryData,
    "773",
    subtags="z",
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Venue ID"
  outData[propertyName] = getEntry(
    entryData,
    "773",
    subtags="0",
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Venue Acronym"
  outData[propertyName] = getEntry(
    entryData,
    "773",
    subtags="q",
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Venue Presented At"
  outData[propertyName] = getEntry(
    entryData,
    "773",
    subtags="t",
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Venue Extra"
  outData[propertyName] = getEntry(
    entryData,
    "773",
    subtags="x",
    isList=False,
    onErrorParent=False
  )
  
  
  propertyName = "Type"
  outData[propertyName] = getEntry(
    entryData,
    "980",
    subtags="a",
    isList=True,
    onErrorParent=True
  )
  
  propertyName = "References"
  outData[propertyName] = getEntry(
    entryData,
    "999",
    subtags={
      "ID": "0",
      "Journal ID": "1",
      "DOI": "a",
      "Year": "y",
      "Journal": "s",
    },
    isList=True,
    onErrorParent=False
  )
  

#   if("041" in entryData):
#     outData["Language"] = entryData["041"];

  return outData;


def processInstitution(entryData):
  outData = {}
  
  propertyName = "ID"
  outData[propertyName] = getEntry(
    entryData,
    "001",
    subtags=None,
    isList=False,
    onErrorParent=True
  )
  
  propertyName = "Geolocation"
  outData[propertyName] = getEntry(
    entryData,
    "034",
    subtags={
      "Lon": "d",
      "Lat": "f",
      "Source": "2",
      "Type": "q",
    },
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Name"
  outData[propertyName] = getEntry(
    entryData,
    "110",
    subtags="u",
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "InstitutionData"
  outData[propertyName] = getEntry(
    entryData,
    "110",
    subtags={
      "Institution": "a",
      "Department": "b",
      "ICN": "t",
    },
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Address"
  outData[propertyName] = getEntry(
    entryData,
    "371",
    subtags={
      "Address": "a",
      "City": "b",
      "State": "c",
      "Country": "d",
      "PostalCode": "e",
      "CountryCode": "g",
    },
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Field"
  outData[propertyName] = getEntry(
    entryData,
    "372",
    subtags="a",
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Accronyms"
  outData[propertyName] = getEntry(
    entryData,
    "410",
    subtags="a",
    isList=True,
    onErrorParent=False
  )
  
  propertyName = "Extra"
  outData[propertyName] = getEntry(
    entryData,
    "410",
    subtags="g",
    isList=True,
    onErrorParent=False
  )
  
  propertyName = "Related"
  outData[propertyName] = getEntry(
    entryData,
    "510",
    subtags={
      "type":"w",
      "ID":"0"
    },
    isList=True,
    onErrorParent=False
  )

  propertyName = "URL"
  outData[propertyName] = getEntry(
    entryData,
    "856",
    subtags="u",
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Tags"
  outData[propertyName] = getEntry(
    entryData,
    "980",
    subtags="a",
    isList=True,
    onErrorParent=True
  )
  
  return outData;




def processData(entryData):
  outData = {}
  
  propertyName = "ID"
  outData[propertyName] = getEntry(
    entryData,
    "001",
    subtags=None,
    isList=False,
    onErrorParent=True
  )
  
  propertyName = "Title"
  outData[propertyName] = getEntry(
    entryData,
    "245",
    subtags="a",
    isList=False,
    onErrorParent=True
  )
  
  propertyName = "PublicationDate"
  outData[propertyName] = getEntry(
    entryData,
    "260",
    subtags="c",
    isList=False,
    onErrorParent=True
  )

  propertyName = "PreprintDate"
  outData[propertyName] = getEntry(
    entryData,
    "269",
    subtags="c",
    isList=False,
    onErrorParent=True
  )
  
  propertyName = "NumberOfPages"
  outData[propertyName] = getEntry(
    entryData,
    "300",
    subtags="a",
    isList=False,
    onErrorParent=True
  )
  
  propertyName = "Collaborations"
  outData[propertyName] = getEntry(
    entryData,
    "710",
    subtags="g",
    isList=True,
    onErrorParent=True
  )
  
  propertyName = "Experiment"
  outData[propertyName] = getEntry(
    entryData,
    "693",
    subtags="e",
    isList=True,
    onErrorParent=False
  )
  
  propertyName = "MainPublication"
  outData[propertyName] = getEntry(
    entryData,
    "786",
    subtags="w",
    isList=False,
    onErrorParent=False
  )

#   if("041" in entryData):
#     outData["Language"] = entryData["041"];

  return outData;


def processJournal(entryData):
  outData = {}
  
  propertyName = "ID"
  outData[propertyName] = getEntry(
    entryData,
    "001",
    subtags=None,
    isList=False,
    onErrorParent=True
  )
  
  propertyName = "Title"
  outData[propertyName] = getEntry(
    entryData,
    "130",
    subtags="a",
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Abbreviation"
  outData[propertyName] = getEntry(
    entryData,
    "711",
    subtags="a",
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Abbreviation 2"
  outData[propertyName] = getEntry(
    entryData,
    "730",
    subtags="a",
    isList=False,
    onErrorParent=False
  )
  
  return outData;



def processConferences(entryData):
  outData = {}
  
  propertyName = "ID"
  outData[propertyName] = getEntry(
    entryData,
    "001",
    subtags=None,
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Title"
  outData[propertyName] = getEntry(
    entryData,
    "111",
    subtags="a",
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Date"
  outData[propertyName] = getEntry(
    entryData,
    "111",
    subtags="d",
    isList=False,
    onErrorParent=False
  )
  
  propertyName = "Location"
  outData[propertyName] = getEntry(
    entryData,
    "111",
    subtags="c",
    isList=False,
    onErrorParent=False
  )
  
  return outData;


def processAbstacts(entryData):
  outData = {}
  
  propertyName = "ID"
  outData[propertyName] = getEntry(
    entryData,
    "001",
    subtags=None,
    isList=False,
    onErrorParent=True
  )

  propertyName = "Abstract"
  outData[propertyName] = getEntry(
  entryData,
    "520",
    subtags="a",
    isList=False,
    onErrorParent=True
  )
  return outData
  

# with gzip.open("../Data/HEP-records.xml.gz","r") as fd:
#   data = ujson.loads(ujson.dumps(xmltodict.parse(fd.read())));

from pymarc import map_xml

# with gzip.open("../Data/HEP-records.xml.gz","r") as fd:
#   from pymarc import MARCReader

def readMARC(filename, parseFunction,estimated=1362493):
  entry = None;
  entries = [];
  thefield = None
  allKeys = {};
  allKeysExample = {};
  allKeysListCount = {};
  pbar = tqdm(total=estimated);
  with gzip.open(filename,"r") as fd:
    def print_title(r):
      nonlocal entry,entries,thefield,allKeys,allKeysExample,allKeysListCount,pbar
      pbar.update(1);
      entry = r;
      # print(r["961"].format_field())
      # fout.write(r.title()+"\n")
      keysSet = set();
      keysCount = {};
      keysContent = {};
      entryData = {};

      for field in r.fields:
        thefield = field;
        tag = field.tag;
        content = field.format_field();
        if(tag not in keysSet):
          keysSet.add(tag);
          keysCount[tag] = 0;
          keysContent[tag] = content;
        keysCount[tag] += 1;
  #           fout.write("\t%s: %s\n"%(tag,content));
        try:
          subfields = {};
          subfieldsLetter = {};
          if(len(field.subfields)>0):
            for subfieldIndex in range(0,len(field.subfields),2):
              subfieldName = field.subfields[subfieldIndex];
              subfieldValue = field.subfields[subfieldIndex+1];
              subTag = tag+"."+subfieldName;
              if(subTag not in keysSet):
                keysSet.add(subTag);
                keysCount[subTag] = 0;
                keysContent[subTag] = subfieldValue;
              keysCount[subTag] += 1;
              subfields[subTag] = subfieldValue;
              subfieldsLetter[subfieldName] = subfieldValue;
            if(tag in entryData):
              if(not isinstance(entryData[tag], list)):
                entryData[tag] = [entryData[tag]];
              entryData[tag].append(subfieldsLetter);
            else:
              entryData[tag] = subfieldsLetter;
  #               fout.write("\t\t%s: %s\n"%(subfieldName,subfieldValue));
        except AttributeError as error:
          pass
        
        if(len(subfields)==0):
          if(tag in entryData):
            if(not isinstance(entryData[tag], list)):
              entryData[tag] = [entryData[tag]];
            entryData[tag].append(content);
          else:
            entryData[tag] = content;
  #       fout.write("-----\n");

  #       fout.flush();
  #       entries.append(entry);
      for key in keysSet:
        if(key not in allKeys):
          allKeys[key] = 0;
          allKeysExample[key] = keysContent[key];
          allKeysListCount[key] = 0
        allKeysListCount[key] += keysCount[key];
        allKeys[key]+=1;
      processedEntry = parseFunction(entryData);
#       processedEntry["raw"] = entryData;
      entries.append(processedEntry)
#       raise ValueError()
    map_xml(print_title, fd)
  return (entries,allKeys,allKeysExample,allKeysListCount);



import re;
import urllib;
import time;
import json;
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def WOSGeocodeAddressNominatim(address):
	nominatimURL = 'http://nominatim.openstreetmap.org/search/';

	queryString = urllib.parse.urlencode({
		"q": address,
		"format": "json",
		"addressdetails": "1",
		"email": "filipinascimento@gmail.com",
		"accept-language": "en",
		"limit": "1",
		"extratags": "0"
	});

	time.sleep(0.75);
	queryURL = nominatimURL + '?' + queryString;
	fURL = urllib.request.urlopen(queryURL);
	structure = json.loads(fURL.read().decode("utf-8"));
	fURL.close();

	if(len(structure)>0):
		return structure[0];
	else:
		return None;


def WOSGeocodeAddress(address):
	location=None;
	newAddress = None;
	usedAddress = None;
	if(address!=None):
		newAddress = address;
		while(location is None and len(newAddress)>0):
			location = WOSGeocodeAddressNominatim(newAddress);
			usedAddress = newAddress;
			newAddress = ",".join(newAddress.split(",")[1:]);
		newAddress = address;
		while(location is None and len(newAddress)>0):
				location = WOSGeocodeAddressNominatim(newAddress);
				usedAddress = newAddress;
				newAddress = ",".join(newAddress.split(",")[0:-1]);
		findPostalCode = re.compile("([0-9]+)[ ,]");
		if(address!=None and len(findPostalCode.findall(address))>0):
			(location,usedAddress) = WOSGeocodeAddress(findPostalCode.sub("",address));
	return (location,usedAddress);
  

def savebgzip(filepath,entries):
  with bgzf.open(filepath,"wb") as fd:
      for entry in tqdm(entries):
          data = ujson.dumps(entry).encode("utf8");
          fd.write(struct.pack("<Q",len(data)))
          fd.write(data)
          
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

HEPBGZ = processedBGZ = PJ(processedDataPath,"HEP.bgzip");
institutionsBGZ = PJ(processedDataPath,"Institutions.bgzip");
dataBGZ = PJ(processedDataPath,"Data.bgzip");
namesBGZ = PJ(processedDataPath,"Names.bgzip");
jobsBGZ = PJ(processedDataPath,"Jobs-records.bgzip");
journalsBGZ = PJ(processedDataPath,"Journals-records.bgzip");
conferencesBGZ = PJ(processedDataPath,"Conferences-records.bgzip");
abstractsBGZ = PJ(processedDataPath,"Abstracts.bgzip")

print("\nProcessing HEP Entries:")
HEPEntries,allKeys,allKeysExample,allKeysListCount = \
  readMARC(PJ(inspireDumpPath,"HEP-records.xml.gz"),processHEP,estimated=1402493)

print("\nSaving HEP entries...")
savebgzip(HEPBGZ,HEPEntries)

print("\nProcessing HEP Abstracts Entries:")
HEPAbstracts,allKeys,allKeysExample,allKeysListCount = \
  readMARC(PJ(inspireDumpPath,"HEP-records.xml.gz"),processAbstacts,estimated=1402493)

print("\nSaving HEP Abstracts entries...")
savebgzip(abstractsBGZ,HEPAbstracts)
del HEPAbstracts


print("\nProcessing Institution Entries:")
institutionsEntries,allKeys,allKeysExample,allKeysListCount = \
  readMARC(PJ(inspireDumpPath,"Institutions-records.xml.gz"),processInstitution,estimated=11579)


print("\nGeolocating Institutions...")
for entry in institutionsEntries:
  if(entry["Field"] is None):
    if(entry["Name"].lower().find("coll.")>=0):
      entry["Field"] = "College"
count=0;
for entry in tqdm(institutionsEntries):
  if entry["Geolocation"] is None and entry["Address"] is not None:
    address = entry["Name"];
    entryAddress = entry["Address"];
    if("Address" in entryAddress and entryAddress["Address"] is not None):
      address+=", ".join(entry["Address"].values())
    entry["NormalizedAddress"] = address;
    geocode = WOSGeocodeAddress(address);
    entry["geocode"] = geocode;
#     count+=1;
#     if(count>=10):
#       break
      
# [entry["Name"]+", "+", ".join(entry["Address"].values()) for entry in institutionsEntries if entry["Geolocation"] is None and entry["Address"] is not None][0]
for entry in tqdm(institutionsEntries):
  if "geocode" in entry:
    geocode = entry["geocode"][0];
    if(geocode is not None):
      entry["geotype"] = geocode["type"]
      entry["Geolocation"] = {'Lon': geocode["lon"], 'Lat': geocode["lat"]}

      
print("\nSaving Institution Data...")
savebgzip(institutionsBGZ,institutionsEntries)



print("\nProcessing Data entries...")
dataEntries,allKeys,allKeysExample,allKeysListCount = \
  readMARC(PJ(inspireDumpPath,"Data-records.xml.gz"),processData,estimated=90488)

print("\nSaving Data entries...")
savebgzip(dataBGZ,dataEntries)

print("\nProcessing HEP Names entries...")
HEPNames,allKeys,allKeysExample,allKeysListCount = \
   readMARC(PJ(inspireDumpPath,"HepNames-records.xml.gz"),processHEP,estimated=128843)

print("\nSaving HEP Names entries...")
savebgzip(namesBGZ,HEPNames)

print("\nProcessing Journal entries...")
HEPJournals,allKeys,allKeysExample,allKeysListCount = \
   readMARC(PJ(inspireDumpPath,"Journals-records.xml.gz"),processJournal,estimated=3684)

print("\nSaving Journal entries...")
savebgzip(journalsBGZ,HEPJournals)

print("\nProcessing Journal entries...")
HEPConferences,allKeys,allKeysExample,allKeysListCount = \
   readMARC(PJ(inspireDumpPath,"Conferences-records.xml.gz"),processConferences,estimated=24168)

print("\nSaving Journal entries...")
savebgzip(conferencesBGZ,HEPConferences)


# for key in sorted(allKeys.keys()):
#   padding = ""
#   if(key.find(".")>0):
#     padding="    "
#   isList = " "
#   if(allKeysListCount[key]>allKeys[key]):
#     isList = "*"
    
#   if(allKeys[key]>=100):
#     print("%s%s: %6d (%3.1f%%) %3.0f%s (%s)"%(padding,key,allKeys[key],allKeys[key]/allKeys["001"]*100,allKeysListCount[key]/allKeys[key],isList,allKeysExample[key] ))
