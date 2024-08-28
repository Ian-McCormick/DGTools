import tkinter as tk

import os
import json
import copy
import re

from enum import Enum

from MobCreator import *
from WeaponCreator import *
from mainViews import *
from Player import *

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__)) + "\\"
DEFAULT_IMAGE_PATH = CURRENT_DIRECTORY + "Photos\\default.png"
SAMPLE = CURRENT_DIRECTORY + "Copy of Arnoux, Zachary S..pdf"
FONT = ("Arial", 10)

class MobType(Enum):
    FRIENDLY = 1
    ENEMY = 2

class Main:
    def __init__(self):
        self.setupWindow = tk.Tk()
        columnLabels = ["All Enemies", "Added Enemies", "Added Friendlies", "All Friendlies", "All Weapons"]
        self.currentWeaponFrame = None

        self.allEnemies = self.loadPlayerObjectJson(CURRENT_DIRECTORY + "AllEnemies.json")
        self.allFriendlies = self.loadPlayerObjectJson(CURRENT_DIRECTORY + "AllFriendlies.json")
        self.allWeapons = MobCreator.MobCreator.loadWeapons(None)

        #create labels for entries
        for i in range(len(columnLabels)):
            label = tk.Label(self.setupWindow, text=columnLabels[i], font=FONT, padx=10, pady=5)
            label.grid(row=0, column=i)
        
        #Create menus for mobs
        self.mobMenus = []
        for i in range(len(columnLabels)):
            self.mobMenus.append(tk.Listbox(self.setupWindow))
            self.mobMenus[i].grid(row = 1, column = i)
        
        #add mobs
        
        for i in list(self.allEnemies.keys()):
            self.mobMenus[0].insert(tk.END, i)
        
        for i in list(self.allFriendlies.keys()):
            self.mobMenus[3].insert(tk.END, i)

        #add WEAPONS, part of self.mobMenus since same system
        for i in range(len(self.allWeapons)):
            self.mobMenus[4].insert(tk.END, self.allWeapons[i].name)
        
        #create buttons to add mobs to current scenario
        addEnemies = tk.Button(self.setupWindow, text="Add Enemy", font=FONT, command = lambda: self.addMob(0, 1))
        addEnemies.grid(row=2, column=0)

        addFriendlies = tk.Button(self.setupWindow, text="Add Friendly", font=FONT, command = lambda: self.addMob(3, 2))
        addFriendlies.grid(row=2, column=3)

        #create buttons to remove selected enemies
        removeEnemies = tk.Button(self.setupWindow, text="Remove Enemy", font=FONT, command = lambda: self.removeMob(1, 0))
        removeEnemies.grid(row=2, column=1)

        removeFriendlies = tk.Button(self.setupWindow, text="Remove Friendly", font=FONT, command = lambda: self.removeMob(2, 3))
        removeFriendlies.grid(row=2, column=2)
        
        #add buttons to create new enemies
        createEnemy = tk.Button(self.setupWindow, text="Create Enemy", font=FONT, command=lambda: self.createMob(0))
        createEnemy.grid(row=3, column=0)

        createEnemy = tk.Button(self.setupWindow, text="Create Friendly", font=FONT, command=lambda: self.createMob(3))
        createEnemy.grid(row=3, column=3)

        #Add buttons for editing particular mob
        editEnemy = tk.Button(self.setupWindow, text="Edit Enemy", font=FONT, command=lambda: self.createMob(0, True))
        editEnemy.grid(row=4, column=0)

        editfriendly = tk.Button(self.setupWindow, text="Edit Friendly", font=FONT, command=lambda: self.createMob(3, True))
        editfriendly.grid(row=4, column=3)

        #add buttons to duplicate mobs
        duplicateEnemy = tk.Button(self.setupWindow, text="Duplicate Enemy", font=FONT, command=lambda: self.duplicateMob(0))
        duplicateEnemy.grid(row = 5, column=0)

        duplicateFriendly = tk.Button(self.setupWindow, text="Duplicate Friendly", font=FONT, command=lambda: self.duplicateMob(3))
        duplicateFriendly.grid(row = 5, column=3)

        #Permenantly delete players
        deleteEnemy = tk.Button(self.setupWindow, text = "Delete Enemy", bg="red", font=FONT, command = lambda: self.deleteMob(0))
        deleteEnemy.grid(row = 6, column=0)

        deleteFriendly = tk.Button(self.setupWindow, text = "Delete Friendly", bg="red", font=FONT, command = lambda: self.deleteMob(3))
        deleteFriendly.grid(row = 6, column=3)

        #Weapon Controls
        createWeapon = tk.Button(self.setupWindow, text="Create Weapon", font=FONT, command= self.createWeapon)
        createWeapon.grid(row = 2, column=4)

        editWeapon = tk.Button(self.setupWindow, text="Edit Weapon", font=FONT, command=lambda: self.createWeapon(True))
        editWeapon.grid(row=3, column=4)

        #Main view Buttons
        roleplayView = tk.Button(self.setupWindow, text="Normal Play", font=FONT, command=lambda: self.roleplayView())
        roleplayView.grid(row=3, column=1)

        battleView = tk.Button(self.setupWindow, text="Battle View", font=FONT, command=lambda: self.battleView())
        battleView.grid(row=3, column=2)

        self.mobMenus[4].bind("<<ListboxSelect>>", self.updateWeaponView)

        self.setupWindow.mainloop()

    def deleteMob(self, selectedMenu):
        mobIndecies = self.mobMenus[selectedMenu].curselection()
        #no mob is selected
        if mobIndecies == ():
            return
        
        mobName = self.mobMenus[selectedMenu].get(mobIndecies[0])
        if selectedMenu == 0:
            del self.allEnemies[mobName]
            self.mobMenus[selectedMenu].delete(mobIndecies[0])
            self.writeMobsToFile(MobType.ENEMY)
            
        elif selectedMenu == 3:
            del self.allFriendlies[mobName]
            self.mobMenus[selectedMenu].delete(mobIndecies[0])
            self.writeMobsToFile(MobType.FRIENDLY)

    def roleplayView(self):
        #get just the selected player objects
        loadedObjects = {}
        playerNames = self.mobMenus[2].get(0, tk.END)
        for nameIndex in range(len(playerNames)):
            name = playerNames[nameIndex]
            #this makes copies of template objects
            if "[TEMP]" in name:
                #make copy of object
                templateCopy:Player = self.deepCopyPlayer(self.allFriendlies[name], self.allFriendlies)
                self.allFriendlies[templateCopy.name] = templateCopy
                loadedObjects[templateCopy.name] = templateCopy
                self.mobMenus[2].delete(nameIndex)
                self.mobMenus[2].insert(nameIndex, templateCopy.name)
            else:
                loadedObjects[name] = self.allFriendlies[name]
        
        #pass objects to display Window
        roleplayView(self.setupWindow, loadedObjects)

        for modifiedPlayerName in list(loadedObjects.keys()):
            try:
                self.allFriendlies[modifiedPlayerName] = loadedObjects[modifiedPlayerName]
            except:
                continue

        self.writeMobsToFile(MobType.FRIENDLY)
    
    def battleView(self):
        #get just the selected player objects
        loadedObjects = {}
        friendlyNames = self.mobMenus[2].get(0, tk.END)
        enemyNames = self.mobMenus[1].get(0, tk.END)

        for nameIndex in range(len(friendlyNames)):
            name = friendlyNames[nameIndex]
            #this makes copies of template objects
            if "[TEMP]" in name:
                #make copy of object
                templateCopy:Player = self.deepCopyPlayer(self.allFriendlies[name], self.allFriendlies)
                self.allFriendlies[templateCopy.name] = templateCopy
                loadedObjects[templateCopy.name] = templateCopy
                self.mobMenus[2].delete(nameIndex)
                self.mobMenus[2].insert(nameIndex, templateCopy.name)
            else:
                loadedObjects[name] = self.allFriendlies[name]

        for nameIndex in range(len(enemyNames)):
            name = enemyNames[nameIndex]
            #this makes copies of template objects
            if "[TEMP]" in name:
                #make copy of object
                templateCopy:Player = self.deepCopyPlayer(self.allEnemies[name], self.allEnemies)
                self.allEnemies[templateCopy.name] = templateCopy
                loadedObjects[templateCopy.name] = templateCopy
                self.mobMenus[1].delete(nameIndex)
                self.mobMenus[1].insert(nameIndex, templateCopy.name)
            else:
                loadedObjects[name] = self.allEnemies[name]
        
        #pass objects to display Window
        battleResults = battleView(self.setupWindow, loadedObjects)
        self.setupWindow.wait_window(battleResults.battleView)
        
        #update objects in memory
        friendlyNames = list(self.allFriendlies.keys())
        enemyNames = list(self.allEnemies.keys())
        for player in list(battleResults.loadedPlayers.keys()):
            if player in friendlyNames:
                self.allFriendlies[player] = battleResults.loadedPlayers[player].playerSheet
            elif player in enemyNames:
                self.allEnemies[player] = battleResults.loadedPlayers[player].playerSheet
            else:
                print(player + " NOT FOUND")
            
        #save stats to file
        self.writeMobsToFile(MobType.ENEMY)
        self.writeMobsToFile(MobType.FRIENDLY)
    
    def deepCopyPlayer(self, originalObject, objectList):
        templateCopy = copy.deepcopy(originalObject)
        tempName = templateCopy.name.replace("[TEMP]", "")

        #remove other iteration markers
        pattern = re.compile(r'\[\d+\]')
        tempName = pattern.sub("", tempName)

        #add number to copy to prevent duplicates
        count = 0
        found = True
        while found:
            #try next number
            found = False
            iterator = str("[{}]".format(count))
            tempName = tempName.replace(iterator, "")
            tempName += "[{}]".format(count+1)
            count += 1
            #check if name exists
            for i in objectList:
                if i == tempName:
                    found = True
                    break
            
            #we looked through all objects, and didn't find an object with that iteration
            #so make a whole new object
            if not found:
                templateCopy.name = tempName
                return templateCopy

    def updateWeaponView(self, event):
        #make sure a weeapon is selected
        wepSelectionIndex = self.mobMenus[4].curselection()
        if wepSelectionIndex == ():
            return
        
        #grab the weapon from the list
        weaponName = self.mobMenus[4].get(wepSelectionIndex[0])
        wepObject = None
        for wep in self.allWeapons:
            if weaponName == wep.name:
                wepObject = wep
        
        if wepObject is None:
            print("No Wep Found")
            return
        
        #prime the Frame
        if self.currentWeaponFrame is not None:
            for widget in self.currentWeaponFrame.winfo_children():
                widget.destroy()
        
        else:
            self.currentWeaponFrame = tk.Frame(self.setupWindow)
            self.currentWeaponFrame.grid(row=0, column=5, rowspan=2)

        labels = ["Name:", "Skill:", "Damage:", "Lethality:", "Armor Piercing:", "Radius:", "Other Notes:"]
        index = 0
        for l in labels:
            lbl = tk.Label(self.currentWeaponFrame, text=l)
            lbl.grid(row=index, column=0, sticky="e")
            index += 1
        
        #add values to the view
        nameLabel = tk.Label(self.currentWeaponFrame, text=wepObject.name)
        skillLabel = tk.Label(self.currentWeaponFrame, text=wepObject.skill)
        dmgText = wepObject.damage[0] +"d " + wepObject.damage[1]
        if wepObject.damage[2].strip() != "0":
            dmgText += " +" + wepObject.damage[2]

        damageLabel = tk.Label(self.currentWeaponFrame, text=dmgText)
        lethalityLabel = tk.Label(self.currentWeaponFrame, text=wepObject.lethality)
        APLabel = tk.Label(self.currentWeaponFrame, text=wepObject.armorPiercing)
        radiusLabel = tk.Label(self.currentWeaponFrame, text=wepObject.radius)
        notesLabel = tk.Label(self.currentWeaponFrame, text=wepObject.notes)

        nameLabel.grid(row=0, column=1, sticky="w")
        skillLabel.grid(row=1, column=1, sticky="w")
        damageLabel.grid(row=2, column=1, sticky="w")
        lethalityLabel.grid(row=3, column=1, sticky="w")
        APLabel.grid(row = 4, column=1, sticky="w")
        radiusLabel.grid(row = 5, column=1, sticky="w")
        notesLabel.grid(row=6, column=1, sticky="NESW")

        self.setupWindow.update()

    #Load existing mobs from Json files
    def loadPlayerObjectJson(self, path):
        try:
            with open(path, "r") as f:
                playerDicts = json.load(f)
            
            mobs = {}
            for d in playerDicts:
                playerObject = Player.playerFromDict(d)
                mobs[playerObject.name] = playerObject
            return mobs
        except Exception as e:
            logging.error(traceback.format_exc())
            return {}

    #Add mob from complete list to current selection
    def addMob(self, completeMenu, selectedMenu):
        for i in self.mobMenus[completeMenu].curselection():
            #add mob to selection list
            mob = self.mobMenus[completeMenu].get(i)
            self.mobMenus[selectedMenu].insert(tk.END, mob)

            #if mob is not a template, remove it from selection
            if "[TEMP]" not in mob:
                self.mobMenus[completeMenu].delete(i)
        return
    
    #remove a mob from selection
    def removeMob(self, selectedMenu, completeMenu):
        for i in self.mobMenus[selectedMenu].curselection():
            mob = self.mobMenus[selectedMenu].get(i)
            if "[TEMP]" not in mob:
                self.mobMenus[completeMenu].insert(tk.END, mob)

            self.mobMenus[selectedMenu].delete(i)
        return
    
    def duplicateMob(self, selectedMenu):
        for i in self.mobMenus[selectedMenu].curselection():
            #get mob name
            mobName = self.mobMenus[selectedMenu].get(i)

            #copy mob object
            mobObject = None
            if selectedMenu == 0:
                mobObject = self.deepCopyPlayer(self.allEnemies[mobName], self.allEnemies)
            elif selectedMenu == 3:
                mobObject = self.deepCopyPlayer(self.allFriendlies[mobName], self.allFriendlies)
            
            #for some reason, the mob doesn't exist, therefore we exit
            if mobObject == None:
                return
            mobName = mobObject.name
            #remove any previous iteration markers
            if selectedMenu == 0:
                self.allEnemies[mobName] = mobObject
                self.writeMobsToFile(MobType.ENEMY)
            elif selectedMenu == 3:
                self.allFriendlies[mobName] = mobObject
                self.writeMobsToFile(MobType.FRIENDLY)
            
            self.mobMenus[selectedMenu].insert(tk.END, mobName)
                
    #need to make a "factory" since there are a lot of variables to mess around with
    def createMob(self, completeMenu, edit = False):
        player = None
        #get DM values for the new Mob
        if edit:
            index = self.mobMenus[completeMenu].curselection()
            playerName = self.mobMenus[completeMenu].get(index)
            if completeMenu == 0:
                compareObects = self.allEnemies
            elif completeMenu == 3:
                compareObects = self.allFriendlies
            else:
                compareObects = {}

            try:
                player = compareObects[playerName]
            except:
                player = None
        
        factory = MobCreator.MobCreator(self.setupWindow)
        factory.creationWindow(player)
        try:
            name = factory.finalMob.name
        except:
            return

        #update list depending on list, and write to json
        if(completeMenu == 0):
            if edit:
                del self.allEnemies[playerName]
                self.allEnemies[name] = factory.finalMob
                self.mobMenus[completeMenu].delete(index)
                self.mobMenus[completeMenu].insert(index, name)
            else:
                if name in self.allEnemies:
                    return
                
                self.allEnemies[name] = factory.finalMob
                self.mobMenus[completeMenu].insert(tk.END, name)

            self.writeMobsToFile(MobType.ENEMY)
            
        #update Friendlies list
        elif(completeMenu == 3):
            if edit:
                del self.allFriendlies[playerName]
                self.allFriendlies[name] = factory.finalMob
                self.mobMenus[completeMenu].delete(index)
                self.mobMenus[completeMenu].insert(index, factory.finalMob.name)
            else:
                if name in self.allFriendlies:
                        return
                self.allFriendlies.append(factory.finalMob)
                self.mobMenus[completeMenu].insert(tk.END, name)
            self.writeMobsToFile(MobType.FRIENDLY)

    def createWeapon(self, edit = False):
        factory = WeaponFactory()
        if edit:
            menuIndex = self.mobMenus[4].curselection()
            weaponName = self.mobMenus[4].get(menuIndex)
            for i in range(len(self.allWeapons)):
                if self.allWeapons[i].name == weaponName:
                    objectIndex = i
                    factory.finalWeapon = self.allWeapons[i]
                    break

        factory.weaponCreation(self.setupWindow, edit)

        if edit:
            self.allWeapons[objectIndex] = factory.finalWeapon
            self.mobMenus[4].delete(menuIndex)
            self.mobMenus[4].insert(menuIndex, factory.finalWeapon.name)
        else:
            exists = False
            for m in self.allWeapons:
                if m.name == factory.finalWeapon.name:
                    exists = True
                    break
            
            if exists:
                return
            self.allWeapons.append(factory.finalWeapon)
            self.mobMenus[4].insert(tk.END, factory.finalWeapon.name)
        
        weaponDicts = [w.weaponToDict() for w in self.allWeapons]
        with open(CURRENT_DIRECTORY + "AllWeapons.json", "w+") as f:
            json.dump(weaponDicts, f, indent=4)
        
    def writeMobsToFile(self, signal):
        if signal == MobType.ENEMY:
            mobDicts = [player.playertoDict() for player in list(self.allEnemies.values())]
            with open(CURRENT_DIRECTORY + "AllEnemies.json", "w+") as f:
                json.dump(mobDicts, f, indent = 4)
        
        elif signal == MobType.FRIENDLY:
            mobDicts = [player.playertoDict() for player in list(self.allFriendlies.values())]
            with open(CURRENT_DIRECTORY + "AllFriendlies.json", "w+") as f:
                json.dump(mobDicts, f, indent = 4)

Main()