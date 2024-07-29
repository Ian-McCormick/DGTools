import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import Player

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
