
'''new_config'''
import re,sys, os
import ETL.Categories as Categories
import ETL.Files as Files
import ETL.DateLogic as dl
def cfgRead():
    testing = False
    if testing == False: 
        TargetDir =  os.path.dirname(sys.argv[1])
        ProjectName = TargetDir.split("\\")[-1]
        cfg = TargetDir + "\\" + ProjectName + "_config.txt"
        ReportIntervals = sys.argv[2] #[1-9<x>(M,Q,Y)], Whether to analyse by Months, Quarters, Years
        Files.initTgtFiles(TargetDir)
    else: 
        cfg = "C:\\Users\Anwender\\Desktop\\CaseStudy\\CaseStudy_config.txt"
        ReportIntervals = "4<x>Y"
    CatInstances = Categories.initCats()
    
    with open(cfg) as cfg:
            txt = cfg.readlines()
            for line in txt:
                if testing == True: 
                    if "ProjectPath" in line: 
                        TargetDir = line.split("=")[1].strip()
                        Files.initTgtFiles(TargetDir) 
                CatObj = re.match("C\d[\d|:]",line)
                if CatObj != None:          
                    arr = line.split(": ")
                    CatEnum = int(arr[0][1:]) - 1
                    CurCat = (CatInstances[CatEnum])
                    CurCat.getProperties(arr[1].split(", "))
    return TargetDir, ReportIntervals


