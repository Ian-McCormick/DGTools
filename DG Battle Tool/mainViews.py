import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time

import Player
import MobCreator
from WeaponCreator import Weapon
import BattleStats

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__)) + "\\"

class roleplayView:
    def __init__(self, parent, players):
        if len(players) == 0:
            return
        #attach Players and entry fields
        self.loadedPlayers = players
        self.playerPhotos = {}
        self.entryFields = {}
        self.roleplayWindow = tk.Toplevel(parent)
        columnIndex = 0
        for p in self.loadedPlayers:
            self.entryFields[p.name] = {}
            self.displayPlayer(p, columnIndex)
            columnIndex += 2
        
        submitButton = tk.Button(self.roleplayWindow, text="SUBMIT", command=self.submit)
        submitButton.grid(row=3, column=0)

        parent.wait_window(self.roleplayWindow)

    def displayPlayer(self, player:Player, columnIndex):
        #we save player name as it'll be used to reference dictionaries
        name = player.name

        #add player photo
        image = Image.open(player.iconPath).resize((100, 100))
        self.playerPhotos[name] = ImageTk.PhotoImage(image)
        photoLabel = tk.Label(self.roleplayWindow, image=self.playerPhotos[name])
        photoLabel.grid(row=0, column=columnIndex)

        #add name
        #we save player name as it'll be used to reference the entries dictionary
        nameLabel = tk.Label(self.roleplayWindow, text=name)
        nameLabel.grid(row=1, column=columnIndex)

        #create canvas for stats/skills
        canvas = tk.Canvas(self.roleplayWindow, width=250)
        scrollBar = ttk.Scrollbar(self.roleplayWindow, orient="vertical", command=canvas.yview)

        canvas.grid(row=2, column=columnIndex, columnspan=2, sticky="nsw")
        scrollBar.grid(row=2, column=columnIndex+1, sticky="nes")

        canvas.configure(yscrollcommand=scrollBar.set)

        frame = tk.Frame(canvas, width=100)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_window, width = e.width))

        frame_window = canvas.create_window((0,0), window=frame, anchor="nw")

        #populate frame with stats and skills
        frameRowIndex = 0
        tk.Label(frame, text="BASE STATS", font=("Arial", 10, "bold")).grid(row=frameRowIndex, column=0)
        tk.Label(frame, bg="black", fg="black").grid(row=frameRowIndex, column=1, sticky="nsew")
        frameRowIndex += 1

        for atr in vars(player.statistics):
            tk.Label(frame, text=atr).grid(row=frameRowIndex, column=0)

            value = tk.StringVar()
            try:
                value.set(getattr(player.statistics, atr))
            except:
                value.set("0")

            self.entryFields[name][atr] = tk.Entry(frame, textvariable=value)
            self.entryFields[name][atr].grid(row=frameRowIndex, column=1)

            frameRowIndex += 1

        tk.Label(frame, text="DERIVED STATS", font=("Arial", 10, "bold")).grid(row=frameRowIndex, column=0)
        tk.Label(frame, bg="black", fg="black").grid(row=frameRowIndex, column=1, sticky="nsew")
        frameRowIndex += 1

        for atr in vars(player.derived):
            tk.Label(frame, text=atr).grid(row=frameRowIndex, column=0)

            value = tk.StringVar()
            try:
                value.set(getattr(player.derived, atr))
            except:
                value.set("0")

            self.entryFields[name][atr] = tk.Entry(frame, textvariable=value)
            self.entryFields[name][atr].grid(row=frameRowIndex, column=1)

            frameRowIndex += 1

        tk.Label(frame, text="SKILLS", font=("Arial", 10, "bold")).grid(row=frameRowIndex, column=0)
        tk.Label(frame, bg="black", fg="black").grid(row=frameRowIndex, column=1, sticky="nsew")
        frameRowIndex += 1

        for atr in vars(player.skills):
            tk.Label(frame, text=atr).grid(row=frameRowIndex, column=0)

            value = tk.StringVar()
            try:
                value.set(getattr(player.skills, atr))
            except:
                value.set("0")

            self.entryFields[name][atr] = tk.Entry(frame, textvariable=value)
            self.entryFields[name][atr].grid(row=frameRowIndex, column=1)

            frameRowIndex += 1
     
    def submit(self):
        print(list(self.entryFields.keys()))
        for i in range(len(self.loadedPlayers)):
            player = self.loadedPlayers[i]
            print(list(self.entryFields[player.name].keys()))
            print(self.entryFields[player.name][list(self.entryFields[player.name].keys())[0]])

            for atr in vars(player.statistics):
                entryField = self.entryFields[player.name][atr]
                value = entryField.get()
                setattr(self.loadedPlayers[i].statistics, atr, value)

            for atr in vars(player.derived):
                setattr(self.loadedPlayers[i].derived, atr, self.entryFields[player.name][atr].get())

            for atr in vars(player.skills):
                setattr(self.loadedPlayers[i].skills, atr, self.entryFields[player.name][atr].get())

        self.roleplayWindow.destroy()
        return

class playerBattleInfo:
    def __init__(self, player):
        self.playerSheet:Player = player
        self.takenAction:bool = False
        self.previewFrame:tk.Frame = None
        self.previewPhoto: ImageTk.PhotoImage = None
        self.bigPhoto: ImageTk.PhotoImage = None

class actionFlowInformation:
    def __init__(self, player):
        self.executor: playerBattleInfo =  player
        self.target: playerBattleInfo = None
        self.weapon: Weapon = None
        self.didTargetDodge:bool = False
        self.complete: bool = False

    def getExecutorName(self):
        if self.executor == None:
            return None
        return self.executor.playerSheet.name
    
    def getTargetName(self):
        if self.target == None:
            return None
        return self.target.playerSheet.name
    
    def getWeaponName(self):
        if self.weapon == None:
            return "Unarmed"
        return self.weapon.name
    
    def getWeaponSkill(self):
        try:
            return self.weapon.skill
        except:
            return "N/A"
        
    def getSkillStat(self):
        try:
            wepSkill = self.weapon.skill
            return getattr(self.executor.playerSheet.skills, wepSkill)
        except:
            return "N/A"
        
    def getWeaponDamage(self):
        try:
            rawDamage = self.weapon.damage
            text = rawDamage[0] + "d" + rawDamage[1]
            if rawDamage[2] != "0":
                text += " + " + rawDamage[2]
            return text
        except:
            return "N/A"
        
    def getTargetArmor(self):
        try:
            return self.target.playerSheet.armor
        except:
            return "N/A"
        
    def getTargetHealth(self):
        try:
            return self.target.playerSheet.derived.hitpoints
        except:
            return "N/A"
    
    def getWeaponList(self):
        return ["Unarmed"] + self.executor.playerSheet.weaponInventory

class battleView:
    def __init__(self, parent, players):
        if len(players) == 0:
            return
        self.loadedPlayers = {}

        self.offensiveActions = ["Aim", "Attack", "Called Shot", "Disarm", "Pin"]
        self.defensiveActions = ["Dodge", "Escape", "Fight Back", "Move", "Wait", "Other"]
        self.actionSeperators = ["-OFFENSIVE ACTIONS-", "-DEFENSIVE ACTIONS-"]
        self.combinedActions = [self.actionSeperators[0]] + self.offensiveActions + [self.actionSeperators[1]] + self.defensiveActions

        weapons = MobCreator.MobCreator.loadWeapons(None)
        self.allWeapons = {}
        for w in weapons:
            self.allWeapons[w.name] = w

        self.battleView = tk.Toplevel(parent)
        self.battleView.geometry("1000x1000")

        #create frame/canvas to place all player canvases
        self.previewCanvas = tk.Canvas(self.battleView)
        scrollbar = ttk.Scrollbar(self.battleView, orient="vertical", command=self.previewCanvas.yview)

        self.previewCanvas.grid(row=0, column=0, sticky="NSEW", padx=0)
        scrollbar.grid(row=0, column=1, sticky="NS")
        self.previewCanvas.configure(yscrollcommand=scrollbar.set)

        self.previewFrame = tk.Frame(self.previewCanvas)
        self.previewFrame.bind("<Configure>", lambda e: self.previewCanvas.configure(scrollregion=self.previewCanvas.bbox("all")))
        self.previewCanvas.bind("<Configure>", lambda e: self.previewCanvas.itemconfig(frame_window, width = e.width))

        frame_window = self.previewCanvas.create_window((0,0), window=self.previewFrame, anchor="nw")

        row = 0
        #populate player previews
        for p in players:
            battlePlayer = playerBattleInfo(p)
            battlePlayer.previewFrame = self.displayPlayerPreview(battlePlayer)
            battlePlayer.previewFrame.grid(row=row, column=0, sticky="NESW")
            self.loadedPlayers[battlePlayer.playerSheet.name] = battlePlayer
            row += 1
        
        #bind canvas width to frame size
        self.previewCanvas.bind("<Configure>", lambda event: self.previewCanvas.configure(width=self.previewFrame.winfo_width()))

        self.detailedPlayerFrame = tk.Frame(self.battleView)
        self.detailedPlayerFrame.grid(row=0, column=2, rowspan=2)

    def displayPlayerPreview(self, player:playerBattleInfo) -> tk.Frame:
        frame = tk.Frame(self.previewFrame, highlightbackground="black", highlightthickness=1)

        #make photo for player
        image = Image.open(player.playerSheet.iconPath).resize((75, 75))
        player.previewPhoto = ImageTk.PhotoImage(image)
        photoLabel = tk.Label(frame, image=player.previewPhoto)
        photoLabel.grid(row=0, column=0, rowspan=4, sticky="W")

        #display stat labels
        nameTag = tk.Label(frame, text="Name:")
        hpTag = tk.Label(frame, text="HP:")
        sanTag = tk.Label(frame, text="SAN:")
        actionTakenTag = tk.Label(frame, text="Action Taken: ")

        nameTag.grid(row=0, column=1, sticky="W")
        hpTag.grid(row=1, column=1, sticky="W")
        sanTag.grid(row=2, column=1, sticky="W")
        actionTakenTag.grid(row=3, column=1, sticky="w")

        #display stat number
        nameStat = tk.Label(frame, text=player.playerSheet.name, name="nameValue")
        hpStat = tk.Label(frame, text=player.playerSheet.derived.hitpoints, name="hpValue")
        sanStat = tk.Label(frame, text=player.playerSheet.derived.sanity, name="sanStat")
        color = "red" if player.takenAction else "green"
        actionTakenStat = tk.Label(frame, text=str(player.takenAction), fg = color, name="actionTaken")

        nameStat.grid(row=0, column=2, sticky="W")
        hpStat.grid(row=1, column=2, sticky="W")
        sanStat.grid(row=2, column=2, sticky="W")
        actionTakenStat.grid(row=3, column=2, sticky="w")

        #bind deltailed view to clicking anywhere in preview
        for w in frame.winfo_children():
            w.bind("<Button-1>", lambda e: self.displaySelectedPlayer(player.playerSheet.name, frame))
        frame.bind("<Button-1>", lambda e: self.displaySelectedPlayer(player.playerSheet.name, frame))

        return frame

    def displaySelectedPlayer(self, playerName:str, newPreviewFrame:tk.Frame):
        player:playerBattleInfo = self.loadedPlayers[playerName]
        player.takenAction = True

        for w in player.previewFrame.winfo_children():
            if str(w).split(".")[-1] == "actionTaken":
                color = "red" if player.takenAction else "green"
                w.configure(text = str(player.takenAction), fg = color)

        startTime = time.time()
        name_label_tag_value = "nameValue"
        selectedStats = ["hitpoints", "willpower", "sanity", "breakingpoint"]
        imageRowHeight = len(selectedStats) + 2

        #clear all previous widgets
        for w in self.detailedPlayerFrame.winfo_children():
            #just in case we need to do something with previous preview Window
            widgetName = str(w).split(".")[-1]
            if str(w).split(".")[-1] == name_label_tag_value:
                prevName = w.cget("text")
                print(self.loadedPlayers[prevName].takenAction)
                self.loadedPlayers[prevName].previewFrame.update()
                self.loadedPlayers[prevName].takenAction = False

            w.destroy()
        
        #populate with new player info
        name = player.playerSheet.name

        #draw image
        if player.bigPhoto == None:
            image = Image.open(player.playerSheet.iconPath).resize((200, 200))
            player.bigPhoto = ImageTk.PhotoImage(image)
        photoLabel = tk.Label(self.detailedPlayerFrame, image=player.bigPhoto)
        photoLabel.grid(row=0, column=0, columnspan=4, rowspan=imageRowHeight, sticky="W")

        #draw name and big stats
        nameLabel = tk.Label(self.detailedPlayerFrame, text=player.playerSheet.name, font=("Arial", 16), name=name_label_tag_value)
        nameLabel.grid(row=0, column=3, sticky="NW")

        #draw selected derived stats
        row = 1
        for atr in vars(player.playerSheet.derived):
            if atr in selectedStats:
                labelText = atr + ": " + getattr(player.playerSheet.derived, atr)
                label = tk.Label(self.detailedPlayerFrame, text=labelText)
                label.grid(row=row, column=3, sticky="w")
                row += 1

        #draw armor stat
        labelText = "Armor: " + player.playerSheet.armor
        label = tk.Label(self.detailedPlayerFrame, text=labelText)
        label.grid(row=row, column=3, sticky="w")

        #draw stats and skills
        self.drawSkillsStats(player, imageRowHeight+1)
        self.drawWeaponTable(player, imageRowHeight+2)
        self.drawActionOptions(player, imageRowHeight+3)
        #print(player.takenAction)

        endTime = time.time()
        #print(endTime-startTime)

        #add weapons
    
    def drawSkillsStats(self, player:playerBattleInfo, mainRow, startColumn = 0):
        #define how tall and wide we want the table
        rowsOfSkills = len(vars(player.playerSheet.statistics))
        skillsWidth = ((len(vars(player.playerSheet.skills))+1) // rowsOfSkills) + 3

        #make the Frame
        skillsFrame = tk.Frame(self.detailedPlayerFrame, highlightbackground="black", highlightthickness=1)
        skillsFrame.grid(row=mainRow, column=0, columnspan=skillsWidth)

        tk.Label(skillsFrame, text="STATISTICS", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="W")
        tk.Label(skillsFrame, text="SKILLS", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky="W")

        startRow = 1
        offset = 0
        
        #draw all of the stats
        for atr in vars(player.playerSheet.statistics):
            labelText = atr + ": " + getattr(player.playerSheet.statistics, atr)
            label = tk.Label(skillsFrame, text=labelText, padx=5)
            label.grid(row=startRow + (offset % rowsOfSkills), column=offset // rowsOfSkills, sticky="w")
            offset += 1
        
        #draw all the skills
        for atr in vars(player.playerSheet.skills):
            labelText = atr + ": " + getattr(player.playerSheet.skills, atr)
            label = tk.Label(skillsFrame, text=labelText, padx=5)
            label.grid(row=startRow + (offset % rowsOfSkills), column=offset // rowsOfSkills, sticky="w")
            offset += 1
        return

    def drawWeaponTable(self, player: playerBattleInfo, startRow, startColumn = 0):
        #initialize variables and frame
        columnLabels = {"Name":"name", "Skill":"skill", "Damage":"damage", "Lethality":"lethality", "Armor Piercing":"armorPiercing", "Radius":"radius", "Notes":"notes"}
        columnKeys = list(columnLabels.keys())
        weaponList = tk.Frame(self.detailedPlayerFrame, pady=5)
        weaponList.grid(row=startRow, column=startColumn, columnspan=len(columnLabels), sticky="w")

        #draw column labels
        curCol = 0
        for labelText in columnKeys:
            tk.Label(weaponList, text=labelText, highlightbackground="black", highlightthickness=1).grid(row=0, column=curCol, sticky="NESW")
            curCol += 1

        #draw the weapons
        curRow = 1
        for w in player.playerSheet.weaponInventory:
            try:
                weapon = self.allWeapons[w]
                curCol = 0
                for key in columnKeys:
                    if key == "Damage":
                        dmgNumbers = getattr(weapon, columnLabels[key])
                        labelText = dmgNumbers[0] + "d" + dmgNumbers[1]
                        if dmgNumbers[2] != "0":
                            labelText += " + " + dmgNumbers[2]
                    else:
                        labelText = getattr(weapon, columnLabels[key])
                
                    tk.Label(weaponList, text=labelText, highlightbackground="black", highlightthickness=1).grid(row=curRow, column=curCol, sticky="NESW")
                    curCol += 1
                curRow += 1
            except:
                continue
        return
        
    def drawActionOptions(self, player, startRow, startColumn = 0):
        actionLabel = tk.Label(self.detailedPlayerFrame, text="Action Choice: ")
        actionLabel.grid(row=startRow, column=0, sticky="w")

        actionOption = tk.StringVar()
        actionOption.set(self.combinedActions[2])   #default to Attack

        actionMenu = tk.OptionMenu(self.detailedPlayerFrame, actionOption, *self.combinedActions)
        actionMenu.grid(row=startRow, column = 1, sticky="w")

        actionButton = tk.Button(self.detailedPlayerFrame, text="Execute", command=lambda:self.executeAction(player, actionOption.get()))
        actionButton.grid(row=startRow, column=2, sticky="w")

    def executeAction(self, player, actionChoice):
        if actionChoice in self.actionSeperators:
            return
        
        self.actionInformation = actionFlowInformation(player)
        self.actionWalkthrough = tk.Toplevel(self.battleView)

        if actionChoice in self.offensiveActions:
            self.targetSelection()
        else:
            print(actionChoice)

        self.battleView.wait_window(self.actionWalkthrough)

    def targetSelection(self):
        self.clearWalkthrough()
        #draw target selection
        targetLabel = tk.Label(self.actionWalkthrough, text="Select Target: ")
        targetLabel.grid(row=0, column=0)

        mobs = list(self.loadedPlayers.keys())
        mobs.remove(self.actionInformation.getExecutorName())
        targetString = tk.StringVar()
        if self.actionInformation.target == None:
            targetString.set(mobs[0])
        else:
            targetString.set(self.actionInformation.getTargetName())

        targetMenu = tk.OptionMenu(self.actionWalkthrough, targetString, *mobs)
        targetMenu.grid(row=0, column=1)

        #Draw Weapon Options
        weaponLabel = tk.Label(self.actionWalkthrough, text="Select Weapon: ")
        weaponLabel.grid(row=1, column=0)

        weaponString = tk.StringVar()
        weaponString.set(self.actionInformation.getWeaponName())
        weaponList = self.actionInformation.getWeaponList()
        
        weaponMenu = tk.OptionMenu(self.actionWalkthrough, weaponString, *weaponList)
        weaponMenu.grid(row=1, column=1)

        #next step button
        nextButton = tk.Button(self.actionWalkthrough, text="Next (Target Dodge)", command=lambda:self.saveTarget(targetString.get(), weaponString.get()))
        nextButton.grid(row=2, column=1)

    #store selections in memory
    #seperate function as so with the "go Back" button we skip over this
    def saveTarget(self, targetName, weaponName):
        try:
            self.actionInformation.weapon = self.allWeapons[weaponName]
        except:
            self.actionInformation.weapon = None
        
        try:
            self.actionInformation.target = self.loadedPlayers[targetName]
            print("Taken Action: " + str(self.actionInformation.target.takenAction))
        except:
            self.actionInformation.target = None
        self.dodgeSelection()

    def dodgeSelection(self):
        self.clearWalkthrough()
        self.actionInformation.didTargetDodge = False
        questionLabel = tk.Label(self.actionWalkthrough, text="Does the target attempt to dodge?", font="helvetica 10 bold")
        questionLabel.grid(row=0, column=0, columnspan=2)

        if self.actionInformation.target.takenAction == True:
            warningLabel = tk.Label(self.actionWalkthrough, text="Target has already taken action\n RaW they cannot dodge", fg="red")
            warningLabel.grid(row=1, column=0, columnspan=2)

        yesButton = tk.Button(self.actionWalkthrough, text="Yes", pady=5, command=lambda: self.executeDodgeRoll())
        yesButton.grid(row = 2, column=0, sticky="EW")
        noButton = tk.Button(self.actionWalkthrough, text="No", pady=5, command=lambda:self.attackRoll())
        noButton.grid(row=2, column=1, sticky="EW")

        tk.Label(self.actionWalkthrough, pady=10).grid(row=3, column=0)
        backButton = tk.Button(self.actionWalkthrough, text="Go Back (Target Selection)", command=self.targetSelection)
        backButton.grid(row=4, column=0, columnspan=2)

    def executeDodgeRoll(self):
        self.clearWalkthrough()
        questionLabel = tk.Label(self.actionWalkthrough, text="Did the target succeed their dodge roll?", font="helvetica 10 bold")
        questionLabel.grid(row=0, column=0, columnspan=2)

        yesButton = tk.Button(self.actionWalkthrough, text="Yes", pady=5, command=lambda:self.saveDodge(True))
        yesButton.grid(row = 2, column=0, sticky="EW")
        noButton = tk.Button(self.actionWalkthrough, text="No", pady=5, command=lambda:self.attackRoll())
        noButton.grid(row=2, column=1, sticky="EW")

        tk.Label(self.actionWalkthrough, pady=10).grid(row=3, column=0)
        backButton = tk.Button(self.actionWalkthrough, text="Go Back (Target Dodge)", command=self.dodgeSelection)
        backButton.grid(row=4, column=0, columnspan=2)

    def saveDodge(self, dodgeSuccess):
        self.actionInformation.didTargetDodge = True
        if dodgeSuccess:
            self.finalizeAction()
        else:
            self.attackRoll()

    def attackRoll(self):
        self.clearWalkthrough()
        weaponNameLabel = tk.Label(self.actionWalkthrough, text="Selected Weapon: " + self.actionInformation.getWeaponName())
        weaponNameLabel.grid(row=0, column=0, columnspan=2)

        skillLabel = tk.Label(self.actionWalkthrough, text="Nominal Skill: " + self.actionInformation.getWeaponSkill())
        skillLabel.grid(row=1, column=0,columnspan=2)

        skillStat = tk.Label(self.actionWalkthrough, text = "Skill Stat: " + self.actionInformation.getSkillStat())
        skillStat.grid(row=2, column=0, columnspan=2)

        questionLabel = tk.Label(self.actionWalkthrough, text="Does the Player's attack succeed?", font="helvetica 10 bold")
        questionLabel.grid(row=3, column=0, columnspan=2)

        yesButton = tk.Button(self.actionWalkthrough, text="Yes", pady=5, command=self.rollDamage)
        yesButton.grid(row = 4, column=0, sticky="EW")
        noButton = tk.Button(self.actionWalkthrough, text="No (FINAL)", pady=5, command=self.finalizeAction)
        noButton.grid(row=4, column=1, sticky="EW")

        tk.Label(self.actionWalkthrough, pady=10).grid(row=5, column=0)
        if self.actionInformation.didTargetDodge:
            backCommand = self.executeDodgeRoll
            backText = "(Dodge Roll)"
        else:
            backCommand = self.dodgeSelection
            backText = "(Dodge Choice)"

        backButton = tk.Button(self.actionWalkthrough, text="Go Back " + backText, command=backCommand)
        backButton.grid(row=6, column=0, columnspan=2)

    def rollDamage(self):
        self.clearWalkthrough()

        titleLabel = tk.Label(self.actionWalkthrough, text="Calculate Damage", font="helvetica 10 bold")
        titleLabel.grid(row=0, column=0, columnspan=2)

        damageLabel = tk.Label(self.actionWalkthrough, text="Nominal Damage: " + self.actionInformation.getWeaponDamage())
        damageLabel.grid(row=1, column=0, columnspan=2)

        armorLabel = tk.Label(self.actionWalkthrough, text="Target Armor: " + self.actionInformation.getTargetArmor())
        armorLabel.grid(row=2, column=0, columnspan=2)

        damageRollLabel = tk.Label(self.actionWalkthrough, text="Target New Health: ")
        damageRollLabel.grid(row=3, column=0)

        damageEntry = tk.Entry(self.actionWalkthrough)
        damageEntry.insert(0, self.actionInformation.getTargetHealth())
        damageEntry.grid(row=3, column=1)

        finalizeButton = tk.Button(self.actionWalkthrough, text="FINALIZE", fg="red", command=self.finalizeAction)
        finalizeButton.grid(row=4, column=0, columnspan=2)

        tk.Label(self.actionWalkthrough, pady=10).grid(row=3, column=0)
        backButton = tk.Button(self.actionWalkthrough, text="Go Back (Attack Roll)", command=lambda:self.attackRoll())
        backButton.grid(row=5, column=0, columnspan=2)

        return
    
    def finalizeAction(self):
        print("Finalize")
        return

    def clearWalkthrough(self):
        for w in self.actionWalkthrough.winfo_children():
            w.destroy()

    


root = tk.Tk()
root.wm_state('iconic')
players = BattleStats.Main.loadPlayerObjectJson(None, CURRENT_DIRECTORY +"AllFriendlies.json")
battleView(root, players)
root.mainloop()