import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

import Player
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

class battleView:
    def __init__(self, parent, players):
        if len(players) == 0:
            return
        self.loadedPlayers = players
        self.playerPhotos = {}
        self.playerBigPhotos = {}
        self.battleView = tk.Toplevel(parent)

        #create frame/canvas to place all player canvases
        self.previewCanvas = tk.Canvas(self.battleView)
        scrollbar = ttk.Scrollbar(self.battleView, orient="vertical", command=self.previewCanvas.yview)

        self.previewCanvas.grid(row=0, column=0, rowspan=len(players), sticky="NSEW", padx=0)
        scrollbar.grid(row=0, column=1, sticky="NS", rowspan=len(players))
        self.previewCanvas.configure(yscrollcommand=scrollbar.set)

        self.previewFrame = tk.Frame(self.previewCanvas)
        self.previewFrame.bind("<Configure>", lambda e: self.previewCanvas.configure(scrollregion=self.previewCanvas.bbox("all")))
        self.previewCanvas.bind("<Configure>", lambda e: self.previewCanvas.itemconfig(frame_window, width = e.width))

        frame_window = self.previewCanvas.create_window((0,0), window=self.previewFrame, anchor="nw")

        row = 0
        #populate player previews
        for p in self.loadedPlayers:
            playerFrame = self.displayPlayerPreview(p)
            playerFrame.grid(row=row, column=0, sticky="NESW")
            row += 1
        
        #bind canvas width to frame size
        self.previewCanvas.bind("<Configure>", lambda event: self.previewCanvas.configure(width=self.previewFrame.winfo_width()))

        self.detailedPlayerFrame = tk.Frame(self.battleView)
        self.detailedPlayerFrame.grid(row=0, column=2)

    def displayPlayerPreview(self, player:Player) -> tk.Frame:
        frame = tk.Frame(self.previewFrame, highlightbackground="black", highlightthickness=1)
        name = player.name

        #make photo for player
        image = Image.open(player.iconPath).resize((75, 75))
        self.playerPhotos[name] = ImageTk.PhotoImage(image)
        photoLabel = tk.Label(frame, image=self.playerPhotos[name])
        photoLabel.grid(row=0, column=0, rowspan=3, sticky="W")

        #display stat labels
        nameTag = tk.Label(frame, text="Name:")
        hpTag = tk.Label(frame, text="HP:")
        sanTag = tk.Label(frame, text="SAN:")

        nameTag.grid(row=0, column=1, sticky="W")
        hpTag.grid(row=1, column=1, sticky="W")
        sanTag.grid(row=2, column=1, sticky="W")

        #display stat number
        nameStat = tk.Label(frame, text=player.name, name="nameValue")
        hpStat = tk.Label(frame, text=player.derived.hitpoints)
        sanStat = tk.Label(frame, text=player.derived.sanity)

        nameStat.grid(row=0, column=2, sticky="W")
        hpStat.grid(row=1, column=2, sticky="W")
        sanStat.grid(row=2, column=2, sticky="W")

        #bind deltailed view to clicking anywhere in preview
        for w in frame.winfo_children():
            w.bind("<Button-1>", lambda e: self.displaySelectedPlayer(player, frame))
        frame.bind("<Button-1>", lambda e: self.displaySelectedPlayer(player, frame))

        return frame

    def displaySelectedPlayer(self, player:Player, newPreviewFrame:tk.Frame):
        name_label_tag_value = "nameValue"
        selectedStats = ["hitpoints", "willpower", "sanity", "breakingpoint"]
        imageRowHeight = len(selectedStats) + 2
        #clear all previous widgets
        for w in self.detailedPlayerFrame.winfo_children():
            #just in case we need to do something with previous preview Window
            if str(w).split(".")[-1] == name_label_tag_value:
                print(end="")
            w.destroy()
        
        #populate with new player info
        name = player.name

        #draw image
        image = Image.open(player.iconPath).resize((200, 200))
        self.playerBigPhotos[name] = ImageTk.PhotoImage(image)
        photoLabel = tk.Label(self.detailedPlayerFrame, image=self.playerBigPhotos[name])
        photoLabel.grid(row=0, column=0, columnspan=3, rowspan=imageRowHeight, sticky="W")

        #draw name and big stats
        nameLabel = tk.Label(self.detailedPlayerFrame, text=player.name, font=("Arial", 16), name=name_label_tag_value)
        nameLabel.grid(row=0, column=4, sticky="NW")

        #draw selected derived stats
        row = 1
        for atr in vars(player.derived):
            if atr in selectedStats:
                labelText = atr + ": " + getattr(player.derived, atr)
                label = tk.Label(self.detailedPlayerFrame, text=labelText)
                label.grid(row=row, column=4, sticky="w")
                row += 1

        #draw armor stat
        labelText = "Armor: " + player.armor
        label = tk.Label(self.detailedPlayerFrame, text=labelText)
        label.grid(row=row, column=4, sticky="w")

        #draw stats and skills
        tk.Label(self.detailedPlayerFrame, text="STATISTICS", font=("Arial", 10, "bold")).grid(row=imageRowHeight+1, column=0, sticky="W")
        rowsOfSkills = len(vars(player.statistics))
        startRow = imageRowHeight + 2
        offset = 0
        for atr in vars(player.statistics):
            labelText = atr + ": " + getattr(player.statistics, atr)
            label = tk.Label(self.detailedPlayerFrame, text=labelText)
            label.grid(row=startRow + (offset % rowsOfSkills), column=offset // rowsOfSkills, sticky="w")
            offset += 1
        return

root = tk.Tk()
players = BattleStats.Main.loadPlayerObjectJson(None, CURRENT_DIRECTORY +"AllFriendlies.json")
battleView(root, players)
root.mainloop()
