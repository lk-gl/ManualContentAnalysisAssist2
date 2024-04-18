import pandas as pd
import sys
import ETL.ToExcel as di

def getOutletFrame(target,count):
        result = {}
        for entry in CodedEntries.CodedEntryLst:
            if entry.outlet == target:
                result.update({entry.index: [entry.cat, entry.PN, entry.outlet]})
        #Placeholder if there is no entry coded throughout Publication
        if result == {}: 
            if target is not "NotAssigned":
                df = pd.DataFrame.from_dict({"Total":[0,0,0]},orient="index", columns = ["Positive","Negative", "Total"])
                df.index.name = target
                di.AnalysisFrames(df,"ByMedium_"+ str(count), "", target,"","","")
                return df
        #Else create Frame
        else: 
            df = pd.DataFrame.from_dict(result,orient="index",columns = ["Category", "Polarity","Outlet"])
            df = df.groupby(["Category","Polarity"]).size().unstack(level=1).fillna(0).reindex(columns=["Positive","Negative"])
            try:
                TP = df["Positive"].sum().sum()
            except:
                df["Positive"] = 0;TP = 0
            try:
                TN = df["Negative"].sum().sum()
            except:
                df["Negative"] = 0; TN = 0 
            df.loc["Total"] = [TP,TN]
            df["Cat Total"] = df.sum(axis=1)
            df = df.fillna(0).astype(int)
            df["Positivity"] = df["Positive"]/df["Cat Total"]
            df["Share"] = df["Cat Total"]/df.loc["Total","Cat Total"]
            df = df.reindex(["Share","Cat Total","Positive","Negative","Positivity"],axis=1)
            df.index.name = target
            di.AnalysisFrames(df,"ByMedium_"+str(count), "", target,"","","")
            return df 
        
#############Class#############
class CodedEntries:
    CodedEntryLst = []
    def __init__ (self,cat,PN, ix,fileObj, outlet, date, title, author, path):
        self.cat = cat
        self.PN = PN
        self.text = None
        self.index = self.buildIndex(ix,fileObj)
        self.fileTitle = fileObj.title
        self.fileEnum = fileObj.nr
        self.outlet = outlet
        self.date = date
        self.title = title
        self.author = author
        self.path = path

    def buildIndex(self, ix,fileObj):
        idx_para = ix[0]+1
        idx_run = ix[1]
        FileId = 9900+(fileObj.nr*100)
        return idx_para + (idx_run/100)+FileId
    
    def assignText(self, text):
        if text != "":
            self.text = text

    def showParam():
        print("HI")
        for c in CodedEntries.CodedEntryLst:
            print(c.cat, c.PN, c.text, c.index, c.fileTitle, c.fileEnum)

