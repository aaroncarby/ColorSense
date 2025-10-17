import keyboard, time, webcolors, tkinter as tk, threading, pyperclip, colorsys
from PIL import Image, ImageGrab, ImageTk
from pynput.keyboard import Listener  as KeyboardListener
from pynput.mouse    import Listener  as MouseListener
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Key
from tkinter import *
from scipy.spatial import KDTree
from webcolors import (
    CSS3_HEX_TO_NAMES,
    CSS21_HEX_TO_NAMES,
    hex_to_rgb,
)
import pyautogui
import json
from PIL import Image
from pystray import MenuItem as item
import pystray




global colorName
global colorRange
global colorHex
global css3_db
global color_family
global hue
global huelist

global lbl_colorName
global lbl_colorHex
global lbl_hue
global lbl_colorHue


with open("./family.json", "r+", encoding="utf8") as f:
        huelist = json.load(f)
#df = pd.read_json('colornames.bestof.min.json')



def colorPicker(x, y):
    #print(x,y)
    im = ImageGrab.grab(bbox=(x, y, x+1, y+1),include_layered_windows=False, all_screens=True)
    #pyautogui.screenshot(region=(x, y, x+1, y+1))
    rgbim = im.convert('RGB')
    r,g,b = rgbim.getpixel((0,0))
    #print(rgb_to_hex(r, g, b))
    colorHex = rgb_to_hex(r, g, b)
    actual_name, closest_name = get_colour_name((r, g, b))
    colorName =closest_name
    colorRange =actual_name
    #print("Actual colour name:", actual_name, ", closest colour name:", closest_name)
    time.sleep(0.5)
    return colorName, colorHex, colorRange
    
def rgb_to_hex(r, g, b):
  return '#%02x%02x%02x' % (r, g, b)



def closest_colour(requested_colour):
    min_colours = {}
    
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)

        colorName =closest_name
    except ValueError:
        closest_name = closest_colour(requested_colour)
        colorName =closest_name
        #actual_name = df['name'].where(df['hex'] == webcolors.rgb_to_hex(requested_colour))
        #actual_name = None
        
        css3_range = CSS21_HEX_TO_NAMES
        css3_range.update(webcolors.CSS2_HEX_TO_NAMES)
        css3_range.update(webcolors.HTML4_HEX_TO_NAMES)
        #CSS21_HEX_TO_NAMES
        names = []
        rgb_values = []
        for color_hex, color_name in css3_range.items():    
            names.append(color_name)
            rgb_values.append(hex_to_rgb(color_hex))
        
        kdt_db = KDTree(rgb_values)
        distance, index = kdt_db.query(requested_colour)
        actual_name = names[index]
    
    return actual_name, closest_name



def hueFinder(hue):

    for key, value in huelist.items():
        if hue <= value["max"]:
            return key
        


def copy_hex(colorHex):
    pyperclip.copy(colorHex[1:])
        
def colorPickerApp():
    initialization()
    global colorHex
    global color_family
    global hue

    global lbl_colorName
    global lbl_colorHex
    global lbl_hue
    global lbl_colorHue
    

    global canvas
    global rectangle
    global root
    colorName ="Black"
    colorRange ="Black"
    hue="Hue: Shade"
    colorHex ="#000000"

    root = tk.Tk()
    root.title("Color Picker")

    photo = tk.PhotoImage(file = './Colorwheel.png')
    root.wm_iconphoto(False, photo)

    root.iconbitmap("./Colorwheel.ico")
    root.geometry("270x390")
    root.maxsize(350, 450)
    root.minsize(280, 420)
    root.configure(background='#35363a')
    #root.overrideredirect(1)


    canvas =tk.Canvas(root, width= 350, height=300, bg='#35363a', highlightthickness=1, highlightbackground='#35363a')
    canvas.pack()
 
    
    lbl_colorHex = tk.Label(root, text=colorHex, fg='#fff', bg='#35363a',font=("Arial", 13), cursor="plus")
    lbl_colorHex.place(relx=.5,y=20, anchor= CENTER)
    lbl_colorHue=tk.Label(root,text="Color Family: "+ colorRange, fg='#fff', bg='#35363a',font=("Arial", 13))
    lbl_colorHue.place(x=10,y=30)
    lbl_colorName=tk.Label(root,text=colorName, fg='#fff', bg='#35363a', font=("Roboto", 19))
    lbl_hue=tk.Label(root,text=hue, fg='#fff', bg='#35363a', font=("Roboto", 17) )
    lbl_colorName.place(x=20,y=30)
    lbl_colorHue.pack()
    lbl_colorName.pack()
    lbl_colorHex.pack()
    lbl_hue.pack()
    root.attributes('-topmost',True)
    

    
    rectangle = canvas.create_rectangle(0, 0, 350, 300, fill=colorName)
    canvas.itemconfig(rectangle,  fill=colorHex)
    
    
    

    def on_key(event):   
        SHIFT_KEYS = {"Shift_L", "Shift_R"} 
        global lbl_colorName
        global lbl_colorHex
        global lbl_hue
        global lbl_colorHue    

        if event.name == "shift" or event.name in SHIFT_KEYS or event.name == 'd'or event.name == 'D':
            mouse = MouseController()
            x = mouse.position[0]   
            y = mouse.position[1]
            colorName, colorHex, colorRange= colorPicker(x, y)
            lbl_colorHue.config(text= "Color Family: "+ colorRange.capitalize())
            lbl_colorName.config(text=colorName.capitalize())
            lbl_colorHex.config(text=colorHex)
            canvas.itemconfig(rectangle,  fill=colorHex)
            lbl_colorHex.bind("<Button-1>", lambda e:copy_hex(colorHex))
            r, g, b =webcolors.hex_to_rgb(colorHex)
            h, l, s = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            hue = hueFinder(int(h*360))

            if(l*100 <=  0):
                hue ="Shade"
           
            hue = "Hue: "+ hue
            lbl_hue.config(text=( hue))
            del mouse
    keyboard.on_release(on_key)


    def quit_window(icon, item):
        icon.stop()
        root.destroy()

    # Define a function to show the window again
    def show_window(icon, item):
        icon.stop()
        root.after(0,root.deiconify())

    # Hide the window and show on the system taskbar
    def hide_window():
        root.withdraw()
        image=Image.open("Colorwheel.png")
        menu=(item('Quit', quit_window), item('Show', show_window))
        icon=pystray.Icon("name", image, "Color Picker", menu)
        icon.run()

    root.protocol('WM_DELETE_WINDOW', hide_window)

    
   
    root.mainloop()

def initialization():
    
    with open("./crayola2.json", "r+", encoding="utf8") as f:
        cf = json.load(f)
    color_family = CSS21_HEX_TO_NAMES
    color_family.update(cf)
    

    with open("./colornames.json", "r+", encoding="utf8") as f:
        data = json.load(f)

    css3_db = CSS3_HEX_TO_NAMES
    css3_db.update(data)

   
    
    
    colorName ="black"
    colorHex ="#000000"
   



colorPickerApp()