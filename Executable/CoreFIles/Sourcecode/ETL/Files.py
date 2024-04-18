import os, re
import ETL.Entries as Entries
import pandas as pd
import ETL.DateLogic as dl
###########Instance Constructor########
def initTgtFiles(TgtDir):
    tt = TgtDir + "\\ProcessedFiles"
    td = os.path.normpath(tt)
    tgtFiles = []
    u = os.scandir(td)
    for entry in u: 
        if entry.is_file():
            if "~$" not in entry.name: #weeds out potential temp files that might bug out the program
                tgtFiles.append(entry.name)
    
    fileInstanceLst = [None]*len(tgtFiles)
    for enum, file in enumerate(tgtFiles):
        path = tt + "\\" + file
        fileInstanceLst[enum] = TargetFiles(path,enum + 1)     
    
    return fileInstanceLst

#############Class#############
class TargetFiles:
    FileLst = []; OutletSt = set(); DateSt =set(); AuthorSt=set()
    def __init__(self,path, nr):
        self.path = path
        self.nr = nr
        self.title = None
        self.author = None
        self.date = None 
        self.outlet = None
        self.dict = None
        self.data = None
        self.group = None
        TargetFiles.FileLst.append(self)


    def decodeID(self,ID, val):
        dctID = {"author":["a"],"date":["d","date"], "outlet":["p","source"], "title": ["t","title"],"id":["id"]}
        
        for k, v in dctID.items():
            if ID == v or ID in v:
                if k == "date":
                   try: val = dl.harmonize(val)
                   except: val = val   
                setattr(self, k, val)

    def getMetadata(self, doc):
        # Look for manual Assignments 
        propIDs = ["a","d", "p","t"]
        for para in doc.paragraphs:
            props = re.findall("<<[a d p t]: (.*?)>>", para.text)
            if props != []:
                for prop in props:
                    pp = prop.split(" /")
                    propVal = pp[0]; propID = pp[1]
                    self.decodeID(propID, propVal)
                    propIDs.remove(propID)
        for ID in propIDs: 
           self.decodeID(ID, "NotAssigned") 
        # Overwrite with results auf Auto Metadata, if applicable
        Auto = False
        for i, para in enumerate(doc.paragraphs):
            if "#DONT CHANGE THE ABOVE#" in para.text: #Inserted Breaker in Analysis files
                Auto = True
                MetaEnd = i 
        if Auto == True: 
            i = 0
            while i < MetaEnd:
                para = doc.paragraphs[i]; metaprops = para.text.split("|")
                for elem in metaprops:
                    prop = elem.split(":")[0]; val = elem.split(":")[1]
                    if prop != "FileNr":
                        self.decodeID(prop,val)
                i =+1 
        #Append to sets of Metadata        
        TargetFiles.OutletSt.add(self.outlet)
        TargetFiles.DateSt.add(self.date)
        TargetFiles.AuthorSt.add(self.author)

    def buildDF(self):
        df = pd.DataFrame(columns=['Category', 'Polarity', 'Text', 'File Title', 'File Number', "Date", "Publication", "Author", "FilePath"])
        for entry in Entries.CodedEntries.CodedEntryLst:
            if entry.fileEnum == self.nr:
                df.loc[entry.index] = [entry.cat, entry.PN, entry.text,entry.fileTitle, entry.fileEnum, self.date, self.outlet, self.author, self.path] 
     #   if df.empty == True:
      #     df.loc["N/A"] = ["N/A", "N/A", "N/A", "N/A", self.nr, self.date, self.outlet, self.author, self.path]   
        self.data = df

