import os
import fitz

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__)) + "\\"
SAMPLE = CURRENT_DIRECTORY + "Copy of Arnoux, Zachary S..pdf"
SAMPLE2 = CURRENT_DIRECTORY + "Blaine, Lucas Redux.pdf"

class Statistics:
    def __init__(self):
        self.strength = 0
        self.constitution = 0
        self.dexterity = 0
        self.intelligence = 0
        self.power = 0
        self.charmisa = 0

    def loadFromArray(self, array):
        self.strength = array[0]
        self.constitution = array[1]
        self.dexterity = array[2]
        self.intelligence = array[3]
        self.power = array[4]
        self.charmisa = array[5]

    def to_dict(self):
        return vars(self)
    
    def fromDict(self, d):
        for key, value in d.items():
            setattr(self, key, value)

class DerivedStats:
    def __init__(self):
        self.maxHitPoints = 0
        self.hitpoints = 0
        self.maxWillPower = 0 
        self.willpower = 0
        self.maxSanity = 0
        self.sanity = 0
        self.breakingpoint = 0
    
    def loadFromArray(self, array):
        self.maxHitPoints = array[0]
        self.hitpoints = array[1]
        self.maxWillPower = array[2]
        self.willpower = array[3]
        self.maxSanity = array[4]
        self.sanity = array[5]
        self.breakingpoint = array[6]

    def to_dict(self):
        return vars(self)
    
    def fromDict(self, d):
        for key, value in d.items():
            setattr(self, key, value)

class Skills(object):
    def __init__(self):
        self.accounting = 0
        self.alertness = 0
        self.anthropology = 0
        self.archeology = 0
        self.art = 0
        self.artillery = 0
        self.athletics = 0
        self.bureaucracy = 0
        self.computerScience = 0
        self.craft = 0
        self.criminology = 0
        self.demolitions = 0
        self.disguise = 0
        self.dodge = 0
        self.drive = 0
        self.firearms = 0
        self.firstAid = 0
        self.forensics = 0
        self.heavyMachinery = 0
        self.heavyWeapons = 0
        self.history = 0
        self.humint = 0
        self.law = 0
        self.medicine = 0
        self.meleeWeapons = 0
        self.militaryScience = 0
        self.navigate = 0
        self.occult = 0
        self.persuade = 0
        self.pharmacy = 0
        self.pilot = 0
        self.psychotherapy = 0
        self.ride = 0
        self.science = 0
        self.search = 0
        self.sigint = 0
        self.stealth = 0
        self.surgery = 0
        self.survival = 0
        self.swim = 0
        self.unarmedCombat = 0
        self.unnatural = 0

    def loadFromArray(self, array):
        if len(array) < len(vars(self)):
            print("error: not enough skills")
            return
        
        index = 0
        for atr in vars(self):
            setattr(self, atr, array[index])
            index += 1
        
    def printAttrs(self):
        for atr in vars(self):
            print(atr + ": {}".format(getattr(self, atr)))

    def to_dict(self):
        return vars(self)
    
    def fromDict(self, d):
        for key, value in d.items():
            setattr(self, key, value)

class Player:
    def __init__(self, name, iconPath, armor, weapons, stats, derStats, skills):
        self.name = name
        self.iconPath = iconPath
        self.armor = armor
        self.weaponInventory = weapons
        self.statistics = stats
        self.derived = derStats
        self.skills = skills

    @classmethod
    def emptyPlayer(self):
        self.name: str
        self.iconPath: str
        self.armor: str
        self.weaponInventory: list[str]
        self.statistics: Statistics
        self.derived: DerivedStats
        self.skills: Skills

    def loadFromPDF(self, filePath, numBonds):

        #for i in range(len(nums)):
        #    print("{}: {}".format(i, nums[i]))

        #get the data from PDF
        doc = fitz.open(filePath)
        text = ""
        for page in doc:
            text += page.get_text()

        lines = text.split("\n")
        name = lines[130]
        nums = []
        #infex = 0
        for line in lines:
            #print(str(infex) + ": " + line)
            #infex += 1
            try:
                nums.append(int(line))
            except:
                continue

        #pull out the raw base stats
        rawStats = nums[1:13:2]
        #remove base stats 
        nums = nums[13:-1]
        #remove bond values
        nums = nums[numBonds:-1]

        #pull out derived stats
        rawDerivedStats = nums[0:7]
        #remove derived stats
        nums = nums[7:-1]
        #remove adaptations
        while nums[0] == 4:
            nums.pop(0)

        #find end of skills, 112382 is the next number shown on page
        index_112382 = 0
        while nums[index_112382] != 112382:
            index_112382 += 1#

        #pull out raw skills
        rawSkills = nums[0:index_112382]

        baseStats = Statistics()
        baseStats.loadFromArray(rawStats)
        derivedStats = DerivedStats()
        derivedStats.loadFromArray(rawDerivedStats)
        skills = Skills()
        skills.loadFromArray(rawSkills)

        return Player(name, "" , "0", [], baseStats, derivedStats, skills)

    def printStats(self):
        print(self.name)
        print("-" *10)

        for key in vars(self.statistics):
            print(key + ": {}".format(getattr(self.statistics, key)))
        
        print("-" *10)

        for key in vars(self.derived):
            print(key + ": {}".format(getattr(self.derived, key)))

        print("-" *10)
        self.skills.printAttrs()
        #for key in vars(self.skills):
        #    print(key + ": {}".format(getattr(self.skills, key)))

    def playertoDict(self):
        return{
            "name": self.name,
            "iconPath": self.iconPath,
            "armor": self.armor,
            "weapons": self.weaponInventory,
            "statistics": self.statistics.to_dict(),
            "derived": self.derived.to_dict(),
            "skills": self.skills.to_dict()

        }
    
    def playerFromDict(d):
        name = d["name"]
        iconPath = d["iconPath"]
        armor = d["armor"]
        weapons = d["weapons"]
        statistics = Statistics()
        statistics.fromDict(d["statistics"])

        derived = DerivedStats()
        derived.fromDict(d["derived"])

        skills = Skills()
        skills.fromDict(d["skills"])
        return Player(name, iconPath, armor, weapons, statistics, derived, skills)

#Arnoux = Player.loadFromPDF(None, SAMPLE, 3)

#Arnoux.printStats()