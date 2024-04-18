import pandas as pd
import ETL.Files as Files 
import ETL.Entries as Entries
import ETL.Output as Output
import re

def initDataFrames():
    for fileObj in Files.TargetFiles.FileLst: 
        subdf = getattr(fileObj, "data")
        AnalysisFrames(subdf,fileObj.nr, fileObj.date, fileObj.outlet, fileObj.title, fileObj.author, fileObj.path).numeralize(subdf)
    fulldf = pd.concat([f.df for f in AnalysisFrames.FrameLst if "ByMedium" not in str(f.scope)])
    AnalysisFrames(fulldf,"Total","","","","","").numeralize(fulldf)
    count = 0
    for outlet in Files.TargetFiles.OutletSt: 
        Entries.getOutletFrame(outlet, count)
        count += 1 
def ExcelWriter(TargetDir):
    mediacount = 0
    path = TargetDir + "\\Results.xlsx"
    writer = pd.ExcelWriter(path)   
    for f in AnalysisFrames.FrameLst:
        #Frames on File-Level (f.scope = FileNr)
        if type (f.scope) == int: 
            targetSheets = ["AllCodedFiles", f.og_outlet] #"All Coded Files" and Outlet-specific Sheet
            for sheet in targetSheets:
                sheObj = initSheets(sheet)
                #Metadata
                f.write_meta(writer,str(sheObj.name), sheObj.offsetR, sheObj.offsetC)
                sheObj.offsetR += 4
                # Results
                sheObj.offsetR = f.write_results(writer,str(sheObj.name), sheObj.offsetR, sheObj.offsetC)[0]                  
                #Details
                sheObj.offsetR = f.write_details(writer,sheObj.name,  sheObj.offsetR, sheObj.offsetC)
                #Reset Row Offset for Sheet
                sheObj.offsetR = 1
                sheObj.offsetC = sheObj.offsetC + 8

        #For any Frame with global designation
        elif type (f.scope) == str: 
                #By-outlet evaluation
                if f.scope.startswith("ByMedium"): 
                        targetSheets = ["Overview"]
                        for sheet in targetSheets:
                            orgC = 0 
                            sheObj = initSheets(sheet)
                            if sheObj.offsetC < 14 + mediacount*6: 
                                orgC = sheObj.offsetC 
                                sheObj.offsetC = 14 + mediacount*6
                            sheObj.offsetC = f.export_full(writer, sheet, sheObj.offsetR, sheObj.offsetC)
                            sheObj.offsetC = sheObj.offsetC if sheObj.offsetC > orgC else orgC
                            mediacount =+1
                elif f.scope.startswith("DATE"):
                    targetSheet = "ByDateSplice"
                    sheObj = initSheets(targetSheet)
                    sheObj.offsetR = f.write_datemeta(writer,targetSheet, sheObj.offsetR,sheObj.offsetC) # +3 R
                    sheObj.offsetR = f.write_results(writer,targetSheet, sheObj.offsetR,sheObj.offsetC)[0] # +len(idx) R
                    x = f.outletstats(writer,targetSheet,sheObj.offsetR,sheObj.offsetC)
                    sheObj.offsetC = sheObj.offsetC + 8
                    sheObj.offsetR = 1
                #Other generally scoped Frames
                elif f.scope == "Total":
                        targetSheets = ["Overview", "AllData"]
                        for sheet in targetSheets:
                            sheObj = initSheets(sheet)
                            if sheet == "Overview":
                                orgC = 0
                                if sheObj.offsetC >=14: 
                                    orgC = sheObj.offsetC 
                                    sheObj.offsetC = 1
                                sheObj.offsetC = f.write_results(writer,"Overview", sheObj.offsetR,sheObj.offsetC)[1]
                                sheObj.offsetC = f.outletstats(writer,"Overview",sheObj.offsetR,sheObj.offsetC)
                                sheObj.offsetC = sheObj.offsetC if sheObj.offsetC > orgC else orgC
                            elif sheet == "AllData": 
                                f.df.index.name = "Index"
                                sheObj.offsetC = f.export_full(writer, sheet, sheObj.offsetR, sheObj.offsetC)                   
    writer.close()

###############Class############

def initSheets(sheet): 
    if sheet not in Sheets.SheetsDct:
            Sheets(sheet)
    return Sheets.SheetsDct[sheet]


class Sheets: 
    SheetsDct = {}
    def __init__(self, name):
        self.name = name
        self.offsetR = 1
        self.offsetC = 1
        Sheets.SheetsDct.update({self.name:self})

########## Class##########
class AnalysisFrames:
    FrameLst = []
    def __init__(self, df, scope, date, outlet, title, author, path):
        self.df = df
        self.scope = scope #FileNr or Total
        self.freqMap = None
        self.insights = None
        self.og_date = date
        self.og_outlet = outlet
        self.og_author = author
        self.og_title = title
        self.og_path = path
        self.group = None
        AnalysisFrames.FrameLst.append(self)
        if "DATE" in str(scope): 
            self.group = scope.replace("DATE", "")

    def setgroup (self, group):
        self.group = group 
    def numeralize (self, df):
        dff = df.groupby(["Category","Polarity"]).size().unstack(level=1).fillna(0).astype(int).reindex(columns=["Positive","Negative"])        
        #Add Totals
        if type(self.scope) == str:
            if self.scope.startswith("DATE"):
                if len(dff) < 11:
                    for emptycat in [x for x in range(1,11) if x not in dff.index]:
                        tu = pd.DataFrame.from_dict({ emptycat:[0,0]}, orient="index",columns=["Positive","Negative"])
                        dff = pd.concat([dff,tu]).sort_index()       
        try:
            TP = dff["Positive"].sum().sum()
        except:
            dff["Positive"] = 0; TP = 0
        try:
            TN = dff["Negative"].sum().sum()
        except:
            dff["Negative"] = 0; TN = 0  

        dff.loc["Total"] = [TP, TN]
        dff["Cat Total"] = dff.sum(axis=1)
        dff = dff.fillna(0).astype(int)        
        
        


        self.freqMap = dff
        self.insights = self.ee(self.freqMap)
        

    def ee(self, df):
        df = df/df.loc["Total", "Cat Total"]
        df["Positivity"] = df["Positive"]/df["Cat Total"]
        return df

    ###Scope: Single File###
    def write_meta(self, writer, sheetname, offsetR, offsetC):
        metadata = pd.DataFrame.from_dict([{"FileNr":self.scope, "Title":self.og_title, "Outlet" : self.og_outlet, "Author": self.og_author, "Path": self.og_path, "Date" : self.og_date}])       
        meta_l = metadata.loc[0][:2]; meta_r = metadata.loc[0][2:-2]; meta_path = metadata.loc[0][-2:].to_frame()
        meta_l.to_excel(writer,sheet_name=sheetname, header = None, startrow=offsetR, startcol=offsetC)
        meta_r.to_excel(writer,sheet_name=sheetname,header = None, startrow=offsetR, startcol=offsetC+2)
        meta_path.to_excel(writer,sheet_name=sheetname,header = None, startrow=offsetR, startcol=offsetC+4)
        Output.Tables(str(self.scope)+"Link",str(sheetname)).scope(offsetC+4, offsetR, meta_path)
    
    def write_details (self, writer, sheet, offsetR, offsetC):
        details = self.df.iloc[:,0:3]
        details["X"] = " " #Cheesy workaround to prevent Excel overflowing entry text into subsequent cells
        details.index.name = "Index"
        details.to_excel(writer,sheet_name=sheet,startrow=offsetR, startcol=offsetC)
        Output.Tables(str(sheet)+str(self.scope)+"Details",str(sheet)).scope(offsetC,offsetR,details)
        return 1 
    ####Scope: Single File AND Global###

    def write_results(self, writer, sheet, offsetR, offsetC):
        results = self.freqMap.copy()
        results ["Share"] = self.insights["Cat Total"]
        results["Positivity"] = self.insights["Positivity"]
        results = results.reindex(["Share","Cat Total","Positive","Negative","Positivity"],axis=1) 
        results.to_excel(writer,sheet_name=sheet,startrow=offsetR, startcol=offsetC)
        Output.Tables(str(sheet) + str(self.scope)+"Results",str(sheet)).scope(offsetC,offsetR,results)  
        return offsetR + len(results.index) +2, offsetC + len(results.columns)+2
        
    #######Scope: Overview Analysis#########
    def write_datemeta(self, writer, sheetname, offsetR, offsetC):
        groupname = self.scope.replace("DATE","")
        targetfiles = [file.nr for file in Files.TargetFiles.FileLst if file.group == groupname]

        metadata = pd.DataFrame.from_dict([{"From":self.group.split("to")[0], "Files":[targetfiles], "To":self.group.split("to")[1]}])     
        meta_l = metadata.loc[0][:2]; meta_r = metadata.loc[0][2:]
        meta_l.to_excel(writer,sheet_name=sheetname, header = None, startrow=offsetR, startcol=offsetC)
        meta_r.to_excel(writer,sheet_name=sheetname,header = None, startrow=offsetR, startcol=offsetC+2)
        return offsetR + 3
    
    
    def outletstats(self, writer, sheetname, offsetR, offsetC):
        if sheetname == "Overview": 
            targetfiles = Files.TargetFiles.FileLst
            targetentries = Entries.CodedEntries.CodedEntryLst
            add = "cutefluffy"
        else: 
            targetfiles = [file for file in Files.TargetFiles.FileLst if file.group == self.group]
            tf = [t.nr for t in targetfiles]
            targetentries = [entry for entry in Entries.CodedEntries.CodedEntryLst if entry.fileEnum in tf]
            add = self.group 

        mediaDf = pd.DataFrame(columns=["Articles", "Coded Entries","Entries/Article","Positivity"])
        all_files = len(targetfiles)

        if all_files == 0: 
            return offsetC
        else: 
            all_entries = len(targetentries)
        for outlet in Files.TargetFiles.OutletSt:
            #Get needed info
            fileObjs = list(filter(lambda p: p.outlet == outlet, targetfiles))
            articles = len(fileObjs); fileNrs = [Obj.nr for Obj in fileObjs]
            entryObjs = list(filter(lambda p: p.fileEnum in fileNrs, targetentries))
            entries = len(entryObjs)
            try: positivity = len([p for p in entryObjs if p.PN == "Positive"])/entries
            except: positivity = "N/A"
            #Write to df    
            try: avg = entries/articles
            except: avg = "N/A"
            mediaDf.loc[outlet] = [articles, entries, avg, positivity]
        mediaDf.loc["Total"] = [all_files, all_entries, all_entries/all_files,"TBD"]
        mediaDf.index.name = "Outlet"
        mediaDf.to_excel(writer,sheet_name=str(sheetname),startrow=offsetR, startcol=offsetC)
        Output.Tables("Media"+add,sheetname).scope(offsetC,offsetR,mediaDf)
        return offsetC + len(mediaDf.columns)+2
    
    def export_full(self, writer, sheetname, offsetR, offsetC):
        self.df.to_excel(writer,sheet_name=sheetname,startrow=offsetR, startcol=offsetC)
        Output.Tables(self.scope,sheetname).scope(offsetC,offsetR,self.df)
        return offsetC + 7

