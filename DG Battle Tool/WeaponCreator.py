import tkinter as tk

from Player import Skills
#ROW SPAN 6
class Weapon:
    def __init__(self):
        self.name:str
        self.skill:str
        self.damage:tuple[str, str, str]
        self.lethality:str
        self.armorPiercing:str
        self.radius:str
        self.notes:str

    def weaponToDict(self):
        return{
            "name": self.name,
            "skill": self.skill,
            "damage": self.damage,
            "lethality": self.lethality,
            "armorPiercing": self.armorPiercing,
            "radius": self.radius,
            "notes": self.notes
        }
    
    def weaponFromDict(d):
        weapon = Weapon()
        weapon.name =  d["name"]
        weapon.skill = d["skill"]
        weapon.damage = d["damage"]
        weapon.lethality = d["lethality"]
        weapon.armorPiercing = d["armorPiercing"]
        weapon.radius = d["radius"]
        weapon.notes = d["notes"]
        return weapon

class WeaponFactory:
    def __init__(self):
        self.finalWeapon = Weapon()

    def weaponCreation(self, parent, edit):
        self.weaponWindow = tk.Toplevel(parent)

        #create entry field labels
        labels = ["Name:", "Skill:", "Damage:", "Lethality:", "Armor Piecing:", "Radius:", "Other Notes:"]
        index = 0
        for l in labels:
            lbl = tk.Label(self.weaponWindow, text=l)
            lbl.grid(row=index, column=0, sticky="e")
            index += 1

        #name entry field
        self.nameEntry = tk.Entry(self.weaponWindow, textvariable=tk.StringVar())
        self.nameEntry.grid(row=0, column=1, sticky = "w")

        #skill selection
        Options = list(vars(Skills()).keys())
        self.selectedSkill = tk.StringVar(value="firearms")
        skillMenu = tk.OptionMenu(self.weaponWindow, self.selectedSkill, *Options)
        skillMenu.grid(row=1, column=1, sticky="nesw")

        #damage field, a little complex so formatting looks nice
        damageFrame = tk.Frame(self.weaponWindow)
        damageFrame.grid(row=2, column=1, sticky = "w")
        defaultNum = tk.StringVar()
        defaultSide = tk.StringVar()
        defaultAddition = tk.StringVar()
        defaultNum.set("1")
        defaultSide.set("4")
        defaultAddition.set("0")

        dmgWdith = 5
        self.numDice = tk.Entry(damageFrame, textvariable= defaultNum, width=dmgWdith)
        self.dieSides = tk.Entry(damageFrame, textvariable= defaultSide, width=dmgWdith)
        self.dmgAddition = tk.Entry(damageFrame, textvariable= defaultAddition, width=dmgWdith)

        self.numDice.grid(row=0, column=0)
        tk.Label(damageFrame, text="d",font=("Arial", 10), width=1).grid(row=0, column=1)
        self.dieSides.grid(row=0, column=2)
        tk.Label(damageFrame, text="+", width=1).grid(row=0, column=3)
        self.dmgAddition.grid(row=0, column=4)

        #Lethality
        lethal = tk.StringVar()
        lethal.set("0")
        self.lethalEntry = tk.Entry(self.weaponWindow,textvariable= lethal)
        self.lethalEntry.grid(row=3, column=1, sticky = "w")

        #armor Piercing
        APvar = tk.StringVar()
        APvar.set("0")
        self.APEntry = tk.Entry(self.weaponWindow, textvariable=APvar)
        self.APEntry.grid(row=4, column=1, sticky="w")

        #radius
        r = tk.StringVar()
        r.set("0")
        self.radiusEntry = tk.Entry(self.weaponWindow,textvariable= r)
        self.radiusEntry.grid(row=5, column=1, sticky = "w")

        #other notes
        self.notesEntry = tk.Text(self.weaponWindow, height = 5, width = 25)
        self.notesEntry.grid(row=6, column =1, columnspan = 2)

        #submit
        submitButton = tk.Button(self.weaponWindow, text="SUBMIT", command=self.submit)
        submitButton.grid(row=7, column=0)

        if edit:
            #load name
            self.nameEntry.delete(0, tk.END)
            self.nameEntry.insert(0, self.finalWeapon.name)
            #load skill
            self.selectedSkill.set(self.finalWeapon.skill)
            #load damage
            self.numDice.delete(0, tk.END)
            self.dieSides.delete(0, tk.END)
            self.dmgAddition.delete(0, tk.END)

            self.numDice.insert(0, self.finalWeapon.damage[0])
            self.dieSides.insert(0, self.finalWeapon.damage[1])
            self.dmgAddition.insert(0, self.finalWeapon.damage[2])
            #load lethality
            self.lethalEntry.delete(0, tk.END)
            self.lethalEntry.insert(0, self.finalWeapon.lethality)

            #load AP
            self.APEntry.delete(0, tk.END)
            self.APEntry.insert(0, self.finalWeapon.armorPiercing)

            #load radius
            self.radiusEntry.delete(0, tk.END)
            self.radiusEntry.insert(0, self.finalWeapon.radius)
            #load notes
            self.notesEntry.delete("1.0", tk.END)
            self.notesEntry.insert(tk.END, self.finalWeapon.notes)

        
        parent.wait_window(self.weaponWindow)

    def submit(self):
        self.finalWeapon.name = self.nameEntry.get()
        self.finalWeapon.skill = self.selectedSkill.get()
        self.finalWeapon.damage = (self.numDice.get(), self.dieSides.get(), self.dmgAddition.get())
        self.finalWeapon.lethality = self.lethalEntry.get()
        self.finalWeapon.armorPiercing = self.APEntry.get()
        self.finalWeapon.radius = self.radiusEntry.get()
        self.finalWeapon.notes = self.notesEntry.get("1.0", tk.END)
        self.weaponWindow.destroy()
        return
