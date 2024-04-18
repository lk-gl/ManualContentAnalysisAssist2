"""Main Program for Readfile Extraction """

def main():
    import os, docx, sys
    import ETL.ConfigHandler as con
    import ETL.ColorReader as cr
    import ETL.ToExcel as te
    import ETL.Files as Files
    import ETL.Output as ou
    import ETL.DateLogic as dl

        
        #Pandas Settings
    import pandas as pd
    pd.set_option('display.max_rows', 250)
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 2)
    ########
    import time
    start_time = time.time()
    ####
    config = con.cfgRead()
    TargetDir = config[0]; Interval = config[1]
    print("#####")
    print("Starting Analysis")
    print("Target Directory:", TargetDir)
    print(TargetDir)
    FileCount = 0
    print("Analyzing...")
    for fileObj in Files.TargetFiles.FileLst:
        FileCount += 1
        print("#####")
        print("Current File:",FileCount,"of", len(Files.TargetFiles.FileLst), " | Title:", fileObj.path)
        doc = docx.Document(fileObj.path)
        fileObj.getMetadata(doc)
        print("Publication:", fileObj.outlet, "| Date", fileObj.date)
        print("#####")
        cr.readColors(doc, fileObj)
        fileObj.buildDF()
    print("All Files analyzed")
    print("Creating Report. Please wait...")
    te.initDataFrames()
    dl.initDateSlices(Interval)
    te.ExcelWriter(TargetDir)
    ou.initTables(TargetDir)
    dl.buildChart(TargetDir, Interval.split("<x>")[1])


    input("Great Success! Report Created. Press Enter to Open")
    print("--- %s seconds ---" % (time.time() - start_time))

    os.system(TargetDir + "\\Results.xlsx")
 