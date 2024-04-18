
from docx.shared import RGBColor


######## Initializer############
def initCats():
    C1 = CatGlobal(1)
    C2 = CatGlobal(2)
    C3 = CatGlobal(3)
    C4 = CatGlobal(4)
    C5 = CatGlobal(5)
    C6 = CatGlobal(6)
    C7 = CatGlobal(7)
    C8 = CatGlobal(8)
    C9 = CatGlobal(9)
    C10 = CatGlobal(10)
    return [C1,C2,C3,C4,C5,C6,C7,C8,C9,C10]

def getRGB(colLst):
        return RGBColor(int(colLst[0]),int(colLst[1]),int(colLst[2]))

#############Class#############

class CatGlobal: 
    CatLst = []
    def __init__(self,enum):
        self.enum = enum
        self.name = None
        self.act = None
        self.colP = None
        self.colN = None 
        self.dict = None
        CatGlobal.CatLst.append(self)

    def decodeProp(self, prop, val):
        dctProps = {"name": "name", "act":"act", "rgbP":"colP", "rgbN": "colN"}
        setattr(self, dctProps[prop], val)
            
    def showParam():
        for c in CatGlobal.CatLst:
            print(c.enum, c.name, c.dict)

    def getProperties(self, props):
        for p in props:
            prop = p.split("=")[0]
            print(p)
            val = p.split("=")[1]
            if prop != "rgb":
                self.decodeProp(prop,val)
            if prop == "rgb":
                cols = val.split(";")
                pos = getRGB(cols[0].split("-")); neg = getRGB(cols[1].split("-"))
                self.decodeProp ("rgbP", pos)
                self.decodeProp ("rgbN", neg)



