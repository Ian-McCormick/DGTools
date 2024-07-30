import tkinter as tk
import os
from tkinter import filedialog
from PIL import Image, ImageTk

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class DMwindow:
    def __init__(self, parent, SBM):
        print(SBM)
        if SBM == None:
            return
        DMwindow = tk.Toplevel(parent)
        playerWindow = tk.Toplevel(parent)
        DMwindow.title("GAME MASTER WINDOW")
        playerWindow.title("Player Window")

        #create canvas and background
        mapImage = Image.open(SBM)
        self.backgroundImage = ImageTk.PhotoImage(mapImage)

        #calculate whats needed for resizing
        rawWidth = self.backgroundImage.width()
        rawHeight = self.backgroundImage.height()

        ratio = rawWidth/rawHeight

        imageHeight = 900
        imageWidth = int(900*ratio)

        mapImage = mapImage.resize((imageWidth, imageHeight))
        self.backgroundImage = ImageTk.PhotoImage(mapImage)
        #
        self.DMcanvas = tk.Canvas(DMwindow, bg = 'white', width = imageWidth, height = imageHeight)
        self.DMcanvas.grid(row=1, column=0)
        self.DMcanvas.create_image(imageWidth/2, imageHeight/2, image = self.backgroundImage)

        #create player canvas
        self.PlayerCanvas = tk.Canvas(playerWindow, bg = 'white', width = imageWidth, height = imageHeight)
        self.PlayerCanvas.grid(row=0, column=0)
        self.PlayerCanvas.create_image(imageWidth/2, imageHeight/2, image = self.backgroundImage)

        #create tools
        self.toolCommands = {"Select": None, "Move": None, "Rectangle": self.create_rectangle, "Oval": self.create_oval}
        self.currentTool = "Select"
        self.toolCommand = None

        self.toolsFrame = tk.Frame(DMwindow)
        self.toolsFrame.grid(row=0, column=0, padx=5, pady=5)
        curColumn = 0
        for tool in self.toolCommands:
            btn = tk.Button(self.toolsFrame, text=tool, command=lambda t=tool: self.selectTool(t))
            btn.grid(row=0, column = curColumn)
            curColumn += 1

        #create area for tokens to live
        self.token_frame = tk.Frame(DMwindow)
        self.token_frame.grid(row=1, column=1, sticky="NESW")
        self.token_path = CURRENT_DIRECTORY + "\\Tokens"

        #load buttons for all the tokens
        location = 0
        for token in os.listdir(self.token_path):
            image = Image.open(self.token_path + "\\" + token)
            image = image.resize((50,50))
            photo = ImageTk.PhotoImage(image)
            tokenButton = tk.Button(self.token_frame, image = photo, command =lambda p=photo: self.add_token_to_canvas(p))
            tokenButton.photo = photo
            tokenButton.grid(row= location//4, column=location%4)
            location += 1

        self.DMcanvas.bind("<ButtonPress-1>", self.on_press)
        self.DMcanvas.bind("<B1-Motion>", self.on_drag)
        self.DMcanvas.bind("<ButtonRelease-1>", self.on_release)
        self.DMcanvas.bind("<ButtonPress-3>", self.delete_shape)

        self.start_x = None
        self.start_y = None
        self.current_item = None
        self.current_action = None  # This is for moving shapes

        #DMwindow.mainloop()

    #change which tool is being used
    def selectTool(self, tool):
        self.toolCommand = self.toolCommands[tool]
        if tool == "Select":
            self.current_action = tool
        elif tool == "Move":
            self.current_action = tool
        else:
            self.current_action = "Create"

    def add_token_to_canvas(self, photo):
        id = self.DMcanvas.create_image(50, 50, image=photo)
        tag = generateOutlineTag(id)

        TLx = 50-photo.width()//2
        TLy = 50-photo.height()//2
        BRx = 50+photo.width()//2
        BRy = 50+photo.height()//2

        self.DMcanvas.create_rectangle(TLx, TLy, BRx, BRy, 
                                       outline="magenta", fill="", width=5, tags=(tag))
        self.updatePlayerWindow()
        return

    #prevent us 
    def filterClosest(self, event):
        self.current_item = self.DMcanvas.find_closest(event.x, event.y)

        #prevent trying to grab a null object
        if self.current_item == ():
            self.current_item = None
            return False
        
        #prevent us from moving certain objects, 1 is background image
        if self.current_item[0] == 1:
            self.current_item = None
            return False
        return True
    
    def on_press(self, event):
        #create a new shape
        if self.current_action == "Create":
            self.start_x = event.x
            self.start_y = event.y
            self.current_item = self.toolCommand(self.start_x, self.start_y, event.x, event.y)
        
        elif self.current_action == "Move":
            if self.filterClosest(event):
                self.start_x = event.x
                self.start_y = event.y
    
    def on_drag(self, event):
        if self.current_item is None:
            return
        
        iTags = self.DMcanvas.itemcget(self.current_item[0], "tags")
        if "outline" in iTags:
            return

        if self.current_action == "Create":
            self.DMcanvas.coords(self.current_item, self.start_x, self.start_y, event.x, event.y)

        elif self.current_action == 'Move' and self.current_item:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            self.DMcanvas.move(self.current_item, dx, dy)
            #move outline rectangle
            if self.DMcanvas.type(self.current_item) == "image":
                tag = generateOutlineTag(self.current_item[0])
                possibleOutlines = self.DMcanvas.find_withtag(tag)
                if len(possibleOutlines) > 0:
                    self.DMcanvas.move(possibleOutlines[0], dx, dy)
            
            self.start_x = event.x
            self.start_y = event.y
        
        self.updatePlayerWindow()
    
    def on_release(self, event):
        if self.current_action == 'create':
            self.DMcanvas.coords(self.current_item, self.start_x, self.start_y, event.x, event.y)

        elif self.current_action == 'Select':
            if self.filterClosest(event) and self.DMcanvas.type(self.current_item) != "image":
                current_color = self.DMcanvas.itemcget(self.current_item, "outline")
                new_color = "red" if current_color != "red" else "green"
                self.DMcanvas.itemconfig(self.current_item, outline = new_color)
        self.current_item = None
        self.updatePlayerWindow()
    
    def create_rectangle(self, x1, y1, x2, y2):
        return self.DMcanvas.create_rectangle(x1, y1, x2, y2, outline="green", fill="", width=10)
    
    def create_oval(self, x1, y1, x2, y2):
        return self.DMcanvas.create_oval(x1, y1, x2, y2, outline="green", fill="", width=10)
    
    def delete_shape(self, event):
        if self.current_action == "Select":
            if self.filterClosest(event):
                if self.DMcanvas.type(self.current_item[0]) == "image":
                    tag = generateOutlineTag(self.current_item[0])
                    possibleOutlines = self.DMcanvas.find_withtag(tag)
                    if len(possibleOutlines) > 0:
                        self.DMcanvas.delete(possibleOutlines[0])

                self.DMcanvas.delete(self.current_item)
                self.current_item = None
        self.updatePlayerWindow()

    def updatePlayerWindow(self):
        self.PlayerCanvas.delete("all")
        items = self.DMcanvas.find_all()
        #add all the items into the player scene
        for item in items:
            itemType = self.DMcanvas.type(item)
            coords = self.DMcanvas.coords(item)
            options = self.DMcanvas.itemconfig(item)

            if itemType == 'rectangle':
                if options['outline'][4] == 'green':
                    self.PlayerCanvas.create_rectangle(*coords, fill="black", outline='')

                if options['outline'][4] == "magenta":
                    self.PlayerCanvas.create_rectangle(*coords, fill="", outline="magenta", width=5)

            if itemType == "oval":
                if options['outline'][4] == 'green':
                    self.PlayerCanvas.create_oval(*coords, fill="black", outline='')
            elif itemType == 'image':
                image = self.DMcanvas.itemcget(item, 'image')
                self.PlayerCanvas.create_image(*coords, image = image)
        
        return

def browse_files(SBM):
    global SBM_full_text

    filename = filedialog.askopenfilename(initialdir=CURRENT_DIRECTORY,
                    title="Select Battle Map")
    SBM.config(text = filename.split("/")[-1])
    SBM_full_text = filename

def generateOutlineTag(id):
    return str(id) + "outline"
def main():
    global SBM_full_text
    SBM_full_text = None
    root = tk.Tk()
    selectedBattleMap = tk.Label(root, text=None)
    selectedBattleMap.grid(row=0, column=1)

    tk.Label(root, text=("Selected Battle Map: ")).grid(row=0, column=0)
    tk.Button(root, text="Browse Files", command= lambda: browse_files(selectedBattleMap)).grid(row=0, column=2)
    tk.Button(root, text="Open Battle Map Tool", command=lambda: DMwindow(root, SBM_full_text)).grid(row=0, column=3)
    #app = DrawShapeApp(root)
    root.title("TTRPG Map Tool")
    root.mainloop()

main()