import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import traceback
import logging
import json

from PIL import Image, ImageTk
import os

from Player import *
from WeaponCreator import Weapon

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__)) + "\\"
DEFAULT_IMAGE_PATH = CURRENT_DIRECTORY + "Photos\\default.png"
SAMPLE = CURRENT_DIRECTORY + "Copy of Arnoux, Zachary S..pdf"

class MobCreator:
    #initialize most the the variables we'll need
    def __init__(self, parent):
        self.parentWindow = parent
        self.attributeRowIndex = 1

        self.name = "Mob"
        self.mobPhotoPath = DEFAULT_IMAGE_PATH
        self.statEntries = []
        self.derivedEntries = []
        self.skillEntries = []

    #set up the actial creation window
    def creationWindow(self, player = None):
        #create window
        self.createWindow = tk.Toplevel(self.parentWindow)
        self.createWindow.grab_set()

        #setup photo window
        if (player is None):
            image = Image.open(self.mobPhotoPath).resize((100,100))
        else:
            self.mobPhotoPath = player.iconPath
            image = Image.open(player.iconPath).resize((100,100))

        self.photo = ImageTk.PhotoImage(image)
        self.photoLabel = tk.Label(self.createWindow, image= self.photo)
        self.photoLabel.grid(row=0, column=0, sticky="w")

        #button to change photo
        photoSelect = tk.Button(self.createWindow, text="Select Photo", command=lambda:self.selectPhoto())
        photoSelect.grid(row=0, column=1, sticky="w")

        #create template checkbox
        #Crate name fields
        nameLabel = tk.Label(self.createWindow, text="Name:")
        nameLabel.grid(row=1, column=0, sticky="W")

        armorLabel = tk.Label(self.createWindow, text="Armor: ")
        armorLabel.grid(row=2, column=0, sticky="W")

        self.templateValue = tk.IntVar()
        templateCheckbox = tk.Checkbutton(self.createWindow, text = "Template", variable=self.templateValue, onvalue=1, offvalue=0)
        templateCheckbox.grid(row= 2, column=3)

        self.nameEntry = tk.Entry(self.createWindow, textvariable=tk.StringVar())
        self.armorEntry = tk.Entry(self.createWindow, textvariable=tk.StringVar())
        if player is None:
            self.nameEntry.insert(0, self.name)
            self.armorEntry.insert(0, "0")
        else:
            self.nameEntry.insert(0, player.name)
            self.armorEntry.insert(0, player.armor)
            if "[TEMP]" in player.name:
                self.templateValue.set(1)

        self.nameEntry.grid(row=1, column=1, sticky="nw")
        self.armorEntry.grid(row=2, column=1)

        #create canvas for scrollbar to scroll
        canvas = tk.Canvas(self.createWindow, width=50)
        scrollBar = ttk.Scrollbar(self.createWindow, orient="vertical", command=canvas.yview)

        canvas.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        scrollBar.grid(row=3, column=1, sticky="nse")

        canvas.configure(yscrollcommand=scrollBar.set)

        #create frame for canvas/entries to live
        self.frame = tk.Frame(canvas, width=100)
        self.frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_window, width = e.width))

        frame_window = canvas.create_window((0,0), window=self.frame, anchor="nw")

        if (player is not None):
            self.populateCanvas("BASE STATS", Statistics(), self.statEntries, player.statistics)
            self.populateCanvas("DERIVED STATS", DerivedStats(), self.derivedEntries, player.derived)
            self.populateCanvas("SKILLS", Skills(), self.skillEntries, player.skills)
        else:
            self.populateCanvas("BASE STATS", Statistics(), self.statEntries)
            self.populateCanvas("DERIVED STATS", DerivedStats(), self.derivedEntries)
            self.populateCanvas("SKILLS", Skills(), self.skillEntries)

        #create Weapon options
        allWeapons = self.loadWeapons()
        self.weaponList = tk.Listbox(self.createWindow)
        self.weaponInventory = tk.Listbox(self.createWindow)
        if player is None:
            for i in range(len(allWeapons)):
                self.weaponList.insert(i, allWeapons[i].name)
        else:
            for i in range(len(allWeapons)):
                if allWeapons[i].name in player.weaponInventory:
                    self.weaponInventory.insert(tk.END, allWeapons[i].name)
                else:
                    self.weaponList.insert(tk.END, allWeapons[i].name)

        self.weaponList.grid(row=3, column=3, sticky="NESW")
        self.weaponInventory.grid(row=3, column=4, sticky="NESW")
        
        addWeapon = tk.Button(self.createWindow, text="Add Weapon", command= self.addWeapon)
        addWeapon.grid(row=4, column=3)

        removeWeapon = tk.Button(self.createWindow, text="Remove Weapon", command=self.removeWeapon)
        removeWeapon.grid(row=4, column=4)
        #Submission Buttons and load stats from PDF
        submitButton = tk.Button(self.createWindow, text="SUBMIT", command=self.submit)
        submitButton.grid(row=4, column=0, sticky="w")

        loadButton = tk.Button(self.createWindow, text="load from PDF", command=self.loadFromPDF)
        loadButton.grid(row=4, column=1, sticky="w")

        self.parentWindow.wait_window(self.createWindow)

    def loadFromPDF(self):
        filePath = filedialog.askopenfilename(initialdir=CURRENT_DIRECTORY,
                                   title="Select PDF")
        #get number of bonds
        bondsWindow = tk.Toplevel(self.createWindow)
        label = tk.Label(bondsWindow, text="Number of bonds:")
        label.grid(row=0, column=0)

        entry = tk.Entry(bondsWindow, textvariable=tk.StringVar())
        entry.insert(0, "3")
        entry.grid(row=1, column=0)
        button = tk.Button(bondsWindow, text="Submit", command=lambda:self.checkNumberOfBonds(entry.get(), bondsWindow))
        button.grid(row=2, column=0)

        self.createWindow.wait_window(bondsWindow)

        #load the data
        try:
            player = Player.loadFromPDF(None, filePath, self.numBonds)
            self.loadFromPlayerObject(player)

        except Exception as e:
            logging.error(traceback.format_exc())
            return

        return
    
    def loadFromPlayerObject(self, player):
        self.nameEntry.delete(0, tk.END)
        self.nameEntry.insert(0, player.name)
        index = 0
        for atr in vars(player.statistics):
            self.statEntries[index].delete(0, tk.END)
            self.statEntries[index].insert(0, getattr(player.statistics, atr))
            index += 1

        index = 0
        for atr in vars(player.derived):
            self.derivedEntries[index].delete(0, tk.END)
            self.derivedEntries[index].insert(0, getattr(player.derived, atr))
            index += 1

        index = 0
        for atr in vars(player.skills):
            self.skillEntries[index].delete(0, tk.END)
            self.skillEntries[index].insert(0, getattr(player.skills, atr))
            index += 1
    
    def checkNumberOfBonds(self, value, window):
        try:
            self.numBonds = int(value)
            window.destroy()
        except:
            errorLabel = tk.Label(window, text="Error: invalid input")
            errorLabel.grid(row=3, column=0)

    def loadWeapons(self) -> list[Weapon]:
        try:
            with open(CURRENT_DIRECTORY + "AllWeapons.json", "r") as f:
                weaponDicts = json.load(f)
            weapons = []
            for d in weaponDicts:
                weapons.append(Weapon.weaponFromDict(d))
            return weapons
        except Exception as e:
            #logging.error(traceback.format_exc())
            return []
    
    def addWeapon(self):
        for i in self.weaponList.curselection():
            wep = self.weaponList.get(i)
            self.weaponList.delete(i)

            self.weaponInventory.insert(tk.END, wep)

    def removeWeapon(self):
        for i in self.weaponInventory.curselection():
            wep = self.weaponInventory.get(i)
            self.weaponInventory.delete(i)

            self.weaponList.insert(tk.END, wep)

    #for addding each section of attributes we need
    def populateCanvas(self, category, dataSet, atrArray, player = None):
        tk.Label(self.frame, text=category, font=("Arial", 10, "bold")).grid(row=self.attributeRowIndex, column=0)
        tk.Label(self.frame, bg="black", fg="black").grid(row=self.attributeRowIndex, column=1, sticky="nsew")
        self.attributeRowIndex += 1

        for atr in vars(dataSet):
            label = tk.Label(self.frame, text=atr)
            label.grid(row=self.attributeRowIndex, column=0)

            defaultValue = tk.StringVar()
            if player is None:
                defaultValue.set("0")
            else:
                defaultValue.set(getattr(player, atr))

            entry = tk.Entry(self.frame, textvariable=defaultValue)
            entry.grid(row=self.attributeRowIndex, column=1)
            atrArray.append(entry)

            self.attributeRowIndex += 1
        
    #update the photo for created mob
    def selectPhoto(self):
        #select new photo
        filePath = filedialog.askopenfilename(initialdir=CURRENT_DIRECTORY + "Photos",
                                   title="Select Profile Photo")
        #attempt to update photo
        try:
            image = Image.open(filePath).resize((100,100))
            self.photo = ImageTk.PhotoImage(image)
            self.photoLabel.configure(image = self.photo)
            self.mobPhotoPath = filePath
        
        #for whatever reason, revert to default
        except:
            image = Image.open(self.mobPhotoPath).resize((100,100))
            self.photo = ImageTk.PhotoImage(image)
            self.photoLabel.config(image = self.photo)
            self.mobPhotoPath = DEFAULT_IMAGE_PATH
        return
    
    def submit(self):
        name = self.nameEntry.get()

        if self.templateValue.get() == 1:
            if "[TEMP]" not in name:
                name += " [TEMP]"
            
        statsArray = []
        for e in self.statEntries:
            statsArray.append(e.get())
        stats = Statistics()
        stats.loadFromArray(statsArray)

        derivedArray = []
        for e in self.derivedEntries:
            derivedArray.append(e.get())
        derived = DerivedStats()
        derived.loadFromArray(derivedArray)

        skillsArray = []
        for e in self.skillEntries:
            skillsArray.append(e.get())
        skills = Skills()
        skills.loadFromArray(skillsArray)

        self.finalMob = Player(name, self.mobPhotoPath, self.armorEntry.get(), self.weaponInventory.get(0, tk.END), stats, derived, skills)
        self.createWindow.destroy()