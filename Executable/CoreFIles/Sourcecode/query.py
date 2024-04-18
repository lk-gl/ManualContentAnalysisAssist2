import sys

#TargetDir = sys.argv[1]


results = []
print("Welcome to FluffySearch!")
print("Here you can look for Entries you coded, Files, as well as even Phrases [be careful with the last Feature]")
print()
print("Query as follows:")
print("> 1-T/1-P/1-N: Returns files with all specified Entries of Category 1(T: both positive and negative, P: Positive, N: Negative ")
print("> F-U/F-P/F-H: Returns files which are in Unprocessed/Processed/Highlighted. You can combine (e.g. F-PH), which will return all Highlighted and Processed Files")
print(">W-<query>: This will return all files which contain the Phrase/Word <query>. Using with trivial statements might cause weird effects. Useful e.g. to search by author")
print("What are you searching for?")

query = input("Please enter:")
mode = query.split("-")[0]
if mode.isdigit() == True:
    submode = query.split("-")[1]
    if submode == "T":
        'search all files for both rbg' 
    elif submode == "P":
        'search all files for pos rbg'
    elif submode == "N":
        'search all files for neg rbg'
if mode == "F":
    if "U" in submode: 
        'search unhandled'
    if "P" in submode: 
        'search handled'
    if "H" in submode:
        'search highlighted'
if mode == "W": 
    'search all files for <query>'

print("Your query resulted in the following results:")
for res in results: 
    print(res)