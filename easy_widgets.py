# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 18:19:32 2021

@author: okay lol
"""

from tkinter import Button
from PIL import ImageTk, Image

def get_all(window):
    widgets = window.winfo_children()
    
    for w in widgets:
        if w.winfo_children():
            widgets.extend(w.winfo_children())
            
    return widgets

class EasyButton:
    
    def __init__(self, location, image_name, sz=[115, 53]):
        
        def update_image(self, event):
            if str(event.type) == "Enter":  # Used to be == "Enter", but I guess an update changed that? Alternatively 7
                self.btn.config(image=self.btn_im_s)
                self.btn.image = self.btn_im_s
            
            # elif str(event.type) == "Leave":
            elif str(event.type) == "Leave":  # Used to be == "Leave". Alternatively 8
                self.btn.config(image=self.btn_im)
                self.btn.image = self.btn_im
            else:
                print("Error: update_image() encountered unexpected event: '" + str(event.type) + "'")
        
        # Original sizes used: 110x50
        
        tmp_im = Image.open(f"sprites/{image_name}.png")
        tmp_resized = tmp_im.resize((sz[0], sz[1]), Image.LANCZOS)
        self.btn_im = ImageTk.PhotoImage(tmp_resized)
        
        tmp_im = Image.open(f"sprites/{image_name}_s.png")
        tmp_resized = tmp_im.resize((sz[0], sz[1]), Image.LANCZOS)
        self.btn_im_s = ImageTk.PhotoImage(tmp_resized)

        self.btn = Button(location, bg=location['bg'], image=self.btn_im, borderwidth=0, activebackground=location["background"], takefocus=0)
        
        self.btn.bind("<Enter>", lambda e: update_image(self, e))
        self.btn.bind("<Leave>", lambda e: update_image(self, e))


class EasyCheck:
    
    def __init__(self, location, start_checked, func, sz=66):
        
        self.ischecked = start_checked
        self.isselected = False
        
        def update_and_perform(self, event, function):

            if self.ischecked == 1:
                self.btn.config(image=self.btn_im)
                self.btn.image = self.btn_im
                self.ischecked = 0
            else:
                self.btn.config(image=self.btn_im_t)
                self.btn.image = self.btn_im_t
                self.ischecked = 1
                
            self.isselected = True
            
            func(self)
        
        tmp_im = Image.open(f"sprites/unchecked.jpg")
        tmp_resized = tmp_im.resize((sz, sz), Image.LANCZOS)
        self.btn_im = ImageTk.PhotoImage(tmp_resized)
        
        tmp_im = Image.open(f"sprites/checked.jpg")
        tmp_resized = tmp_im.resize((sz, sz), Image.LANCZOS)
        self.btn_im_t = ImageTk.PhotoImage(tmp_resized)
        
        if self.ischecked == 1:
            starting_image = self.btn_im_t
        else:
            starting_image = self.btn_im
            
        self.btn = Button(location, image=starting_image, borderwidth=0, bg=location["background"], activebackground=location["background"], takefocus=0)
        self.btn.bind("<Button-1>", lambda e, f=func: update_and_perform(self, e, f))
        
        
        
