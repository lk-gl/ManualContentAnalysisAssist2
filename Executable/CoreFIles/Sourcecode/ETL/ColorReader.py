
import ETL.Categories as Categories
import ETL.Entries as Entries
import ETL.Files as Files

def readColors (doc, fileObj):
    ix = []
    for Cat in Categories.CatGlobal.CatLst:
        if Cat.act == "Wahr":
            for col,polarity in {Cat.colP:"Positive", Cat.colN: "Negative"}.items():
                #Loop current file for coded instances
                i = 0 
                while i < len(doc.paragraphs):
                    p = doc.paragraphs[i]                    
                    run_counter = 0; curText = ""; newinstance = True; curEntryObj =None
                    for run in p.runs:
                        run_counter += 1
                        if run.font.color.rgb == col:
                            if newinstance == True: 
                                newinstance = False
                                ix = [i, run_counter]
                                curEntryObj = Entries.CodedEntries(Cat.enum, polarity, ix, fileObj, fileObj.outlet,fileObj.date, fileObj.title, fileObj.author, fileObj.path)
                                curText += run.text #Store runtext
                            else: #If not new instance, merge text with previous entry text
                                  curText += run.text 
                    #Entry endings...    
                        else:  #...within para
                            if curEntryObj != None:
                                if len(curText) > 3: # Makes sure a coded entry needs more than 3 Characters
                                    curEntryObj.assignText(curText)
                                    Entries.CodedEntries.CodedEntryLst.append(curEntryObj)
                            curEntryObj = None; newinstance = True; curText = ""
                    #...at end of para (by default)
                    if curEntryObj != None: 
                        if len(curText) > 3: # Makes sure a coded entry needs more than 3 Characters
                                    curEntryObj.assignText(curText)
                                    Entries.CodedEntries.CodedEntryLst.append(curEntryObj)
                        curEntryObj.assignText(curText)
                    curEntryObj = None
                    i = i + 1 
                    #Next para
