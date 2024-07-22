# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15, 9:47PM, 2024

@author: okay lol
"""

import pyperclip

from pynput import keyboard

from easy_widgets import EasyButton
from PIL import ImageTk, Image

from tkinter import Canvas

from tkinter import Tk
from tkinter import Label
from tkinter import Frame
from tkinter import Event
from tkinter.font import Font

from pydub import AudioSegment
from pydub.playback import play
import threading

ROOT_BG = "#282828"  # Constant for the background of the root element. A lighter grey color.
FRAME_BG = "#181818"  # Constant for the background of certain frame elements. A darker grey color.
ALL_SIZES = [5, 10, 15, 25, 50]  # Keeps track of legal set sizes

global root  #
global frames  # A dict that holds basically every GUI element
global images  # A dict that holds images

global this  # The index of the current position in the current set
global set_size  # Keeps track of the size of the current set
global this_set  # Tracks caps/misses for the current set

global canvas_size  # A list that tracks the x-y dimensions of the canvas element used for drawing the graph

global percentage  # (0 to 100 / 100%) or (0 to 15 / 15), for example
global locked  # The locked state disables the reading of keyboard input to modify set progress
global muted  # Disables sound

global streak  # Current caps in a row for the current set
global max_streak  # Maximum streak achieved for the current set

global copy_id  # Keeps track of the "Text Copied!" popup that temporarily appears when you copy set stats

frames = {}
images = {'garbage': []}  # Lots of image vars are effectively useless, but are necessary for images to function

this = 0
set_size = 15
this_set = [0] * 15

percentage = True
locked = False
muted = False

copy_id = (0, None)  # (event id int, frame)


def make_image(name: str, size: tuple = (40, 40)) -> None:
    """
    Takes a str of an image name, creates an image, and stores the image with the name as the key in the images dict.
    ------------

    :param name: str :
        The name of the image file in ./sprites/
    :param size: tuple :
        A tuple of the desired dimensions of the image
    :return: None
    """

    images['garbage'].append(Image.open(f"sprites/{name}.png"))
    images['garbage'].append(images['garbage'][-1].resize(size, Image.LANCZOS))
    images[f'{name}'] = ImageTk.PhotoImage(images['garbage'][-1])


# -----------------------------------------------------------------------------


def raise_above_all(window: Tk) -> None:
    """
    Raises the window above everything else when the program is first opened.
    ------------

    :param window: Tk :
        The root element
    """

    window.attributes('-topmost', 1)
    window.attributes('-topmost', 0)


# -----------------------------------------------------------------------------


def init_root() -> None:
    """
    Initializes the program's window, configuring its grid settings and dimensions, among other things.
    ------------

    :return: N/A
    """

    global root
    root = Tk()
    app_width = 1000
    app_height = 600
    x_coord = int((root.winfo_screenwidth() / 2) - (app_width / 2))
    y_coord = int((root.winfo_screenheight() / 2) - (app_height / 2))

    root.geometry(f'{app_width}x{app_height}+{x_coord}+{y_coord}')
    root.title("Spellcard Sets")
    root.iconbitmap("sprites/card.ico")

    root['bg'] = FRAME_BG
    root.overrideredirect(0)

    raise_above_all(root)
    root.grid_propagate(False)
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.update()


# -----------------------------------------------------------------------------


init_root()  # Call the init_root() function to immediately create the root.


def quit_root(tracker: keyboard.Listener) -> None:
    """
    Stops the key input listener, cancels scheduled events, and destroys the root element.
    ------------

    :param tracker: keyboard.Listener :
        Listens to key inputs. 1, 2, and 3 can be pressed to update set progress
    :return: None
    """

    tracker.stop()
    for after_id in root.tk.eval('after info').split():
        root.after_cancel(after_id)
    root.destroy()


# -----------------------------------------------------------------------------


def frame_config(frame: Frame, max_value: int, rows: bool) -> None:
    """
    A simple function to configure 0 to max_value-1 rows or columns in a window element.
    ------------

    :param frame: Frame :
        The frame to configure
    :param max_value: int :
        One greater than the max value to configure up to
    :param rows: bool :
        Whether rows should be the ones configured (rather than columns)
    :return: None
    """

    if rows:
        for x in range(max_value):
            frame.grid_rowconfigure(x, weight=1)
    else:
        for x in range(max_value):
            frame.grid_columnconfigure(x, weight=1)


# -----------------------------------------------------------------------------


def find_set_position() -> int:
    """
    A function designed to find the current index of the list this_set, which tracks the current set results.
    ------------

    :return: int
        The index of the most recently completed attempt in this_set
    """

    index = len(this_set) - 1
    v = this_set[index]

    while v == 0 and index > 0:
        index -= 1
        v = this_set[index]

    return index


# -----------------------------------------------------------------------------


def change_size(direction: str) -> None:
    """
    Changes the size of the set. Also updates the checkboxes, and ties together other loose ends that arise from this.
    ------------

    :param direction: str :
        Either 'up' or 'down'. Whether to increase or decrease the size of the set.
    :return: None
    """

    global frames
    global set_size
    global this_set
    global this
    global copy_id

    index = ALL_SIZES.index(set_size)
    first_index = index

    if direction == 'up':
        # If you try to increase the size above the max size, wrap around instead.
        index = (index + 1) % len(ALL_SIZES)
    else:
        # " "
        index = (index + (len(ALL_SIZES) - 1)) % len(ALL_SIZES)
    set_size = ALL_SIZES[index]

    if len(this_set) < set_size:
        # Increase the size of this_set. Harmless, so it can be done in one line
        this_set += ([0] * (set_size - len(this_set)))
    else:
        # Decrease the size of this_set. Will prevent it from being changed if set progress will be cut off
        tmp = find_set_position()
        if tmp >= set_size:
            if ALL_SIZES[index - 1] != 0:
                print("Cannot change size.")
                set_size = ALL_SIZES[first_index]
                manage_audio('gank')  # Error sound. Don't ask why it's called "gank," I have no idea
                return
            this = set_size - 1
        this_set = this_set[:set_size]

    if copy_id[0]:
        # If a 'Text Copied!' popup is current placed anywhere, cancel the event that removes it later and remove it now
        root.after_cancel(copy_id[0])
        copy_id[1].place_forget()

    frames['set_count']['text'] = set_size
    frame_config(frames['boxes'], set_size // 5, True)

    # Destroy frames and checkboxes so new ones can be created
    for f in frames['internal']:
        f.destroy()

    for f in frames['checks']:
        f.destroy()

    manage_audio('pause')
    make_boxes()

    # Redraw graph scaled to the current set size.
    if locked:
        lock(False)
    else:
        canvas_redo(False)


# -----------------------------------------------------------------------------


def toggle_graph() -> None:
    """
    Changes the style of the graph. Can either display as a percentage of successful caps, or as a running total of caps
    ------------

    :return: None
    """

    global percentage
    percentage = not percentage
    manage_audio('achievement')
    if locked:
        lock(False)
    else:
        canvas_redo(False)


# -----------------------------------------------------------------------------


def reset_all() -> None:
    """
    Clears set progress. If the locked state is enabled, disable it.
    ------------

    :return: None
    """

    global this
    global this_set
    global frames
    global locked

    if locked:
        frames['right-chains'].place_forget()
        frames['left-chains'].place_forget()
        locked = False
    elif this == 0:
        manage_audio('gank')
        return

    this = 0
    this_set = [0] * set_size

    for box in frames['checks']:
        box['image'] = images['unchecked']

    canvas_redo(False)

    manage_audio('item-increment')  # These audio names aren't particularly accurate


# -----------------------------------------------------------------------------


def make_window() -> None:
    """
    Handles the creation of basically everything in the window. Also handles most instances of event binding.
    ------------

    :return: None
    """

    global root
    global frames
    global images

    for n in ['x', 'o', 'unchecked']:
        # Initializes and store checkbox state images in the images dict
        make_image(n)
    # Initializes and stores chain images for the locked function later on
    make_image('right-chains', (150, 150))
    make_image('left-chains', (110, 230))

    # Images for flames accompanying streaks
    make_image('flame')
    make_image('golden flame')
    make_image('purple flame')  # Unused
    make_image('grey flame')

    # The 'left' frame contains checkboxes and config buttons
    frames['left'] = Frame(root, bg=ROOT_BG, width=root.winfo_width() / 3, height=root.winfo_height())
    frames['left'].grid_propagate(False)
    frames['left'].grid_columnconfigure(0, weight=1)
    frames['left'].grid_rowconfigure(0, weight=3)
    frames['left'].grid_rowconfigure(1, weight=1)

    frames['left'].grid(row=0, column=0, sticky="w")
    root.update()

    # 'boxes' is one frame that contains rows of checkboxes
    frames['boxes'] = Frame(frames['left'], bg=frames['left']['bg'], width=frames['left'].winfo_width(), height=400)
    frames['boxes'].grid_propagate(False)
    frames['boxes'].grid(row=0, column=0)

    frame_config(frames['boxes'], 5, False)
    frame_config(frames['boxes'], 3, True)

    # 'config' is where all of the config buttons are placed
    frames['config'] = Frame(frames['left'], bg=frames['left']['bg'], width=frames['left'].winfo_width() - 10,
                             height=150)
    frames['config'].grid_propagate(False)
    frames['config'].grid_columnconfigure(0, weight=1)
    frames['config'].grid_rowconfigure(0, weight=1)
    frames['config'].grid_rowconfigure(1, weight=3)
    frames['config'].grid_rowconfigure(2, weight=1)
    frames['config'].grid(row=1, column=0)

    # -------------------------------------------
    # For config buttons

    # Increases/decreases set size
    frames['up'] = EasyButton(frames['config'], 'up', [40, 40])
    frames['up'].btn.grid(row=0, column=0)
    frames['up'].btn.bind("<Button-1>", lambda e: change_size('up'))
    frames['down'] = EasyButton(frames['config'], 'down', [40, 40])
    frames['down'].btn.grid(row=2, column=0)
    frames['down'].btn.bind("<Button-1>", lambda e: change_size('down'))

    # Displays the set size
    frames['set_count'] = Label(frames['config'],
                                bg=frames['config']['bg'],
                                font=Font(family="Book Antiqua", size=30, weight='bold'),
                                fg='white', text="15")
    frames['set_count'].grid(row=1, column=0)

    # Toggles display modes of the canvas graph
    frames['graph'] = EasyButton(frames['config'], 'bar graph', [40, 40])
    frames['graph'].btn.place(x=210, y=55)
    frames['graph'].btn.bind("<Button-1>", lambda e: toggle_graph())

    # Clears the current set
    frames['reset'] = EasyButton(frames['config'], 'reset', [40, 40])
    frames['reset'].btn.place(x=70, y=55)
    frames['reset'].btn.bind("<Button-1>", lambda e: reset_all())

    # Toggles locked
    frames['lock'] = EasyButton(frames['config'], 'lock', [40, 40])
    frames['lock'].btn.place(x=10, y=55)
    frames['lock'].btn.bind("<Button-1>", lambda e: lock())

    # Toggles mute
    frames['mute'] = EasyButton(frames['config'], 'mute', [40, 40])
    frames['mute'].btn.place(x=270, y=55)
    frames['mute'].btn.bind("<Button-1>", lambda e: mute())

    make_boxes()

    # The 'right' frame contains statistics about the current set as well as the canvas graph
    w = root.winfo_width() * (2 / 3)
    frames['right'] = Frame(root, bg=FRAME_BG, width=w, height=root.winfo_height())
    frames['right'].grid_propagate(False)
    frames['right'].grid_columnconfigure(0, weight=1)
    frames['right'].grid_rowconfigure(0, weight=1)
    frames['right'].grid_rowconfigure(1, weight=3)
    frames['right'].grid(row=0, column=1)

    # The fabled canvas. Draws the graph for the current set
    frames['canvas'] = Canvas(frames['right'], bg=frames['right']['bg'], width=w, height=250,
                              highlightthickness=0,
                              )
    frames['canvas'].grid(row=1, column=0, sticky="s", pady=25)
    global canvas_size
    canvas_size = [617, int(frames['canvas']['height']) - 20]

    # Giant frame containing statistics
    frames['stats'] = Frame(frames['right'], bg=frames['right']['bg'], width=frames['right']['width'], height=300)
    frames['stats'].grid_propagate(False)
    frame_config(frames['stats'], 3, False)
    frames['stats'].grid_rowconfigure(0, weight=1)
    frames['stats'].grid(row=0, column=0)

    # Smaller frames containing statistics ↓ ↓ ↓

    frames['left-stats'] = Frame(frames['stats'], bg=frames['stats']['bg'], width=185, height=150)
    frames['left-stats'].grid_propagate(False)
    frame_config(frames['left-stats'], 3, True)
    frames['left-stats'].grid_columnconfigure(0, weight=1)
    frames['left-stats'].grid(row=0, column=0, sticky='s', pady=63)

    frames['mid-stats'] = Frame(frames['stats'], bg=frames['stats']['bg'], width=200, height=45)
    frames['mid-stats'].grid_propagate(False)
    frames['mid-stats'].grid_rowconfigure(0, weight=1)
    frames['mid-stats'].grid(row=0, column=1, sticky='w')

    frames['right-stats'] = Frame(frames['stats'], bg=frames['stats']['bg'], width=200, height=45)
    frames['right-stats'].grid_propagate(False)
    frames['right-stats'].grid_rowconfigure(0, weight=1)
    frames['right-stats'].grid(row=0, column=2)

    frames['mid-stats'].bind("<Enter>", lambda e, a=['%', 'percent', 'rate']: rate_color_change(e, a))
    frames['mid-stats'].bind("<Leave>", lambda e, a=['%', 'percent', 'rate']: rate_color_change(e, a))

    frames['right-stats'].bind("<Enter>", lambda e, a=['streak', 'st', 'max']: rate_color_change(e, a))
    frames['right-stats'].bind("<Leave>", lambda e, a=['streak', 'st', 'max']: rate_color_change(e, a))

    frames['left-stats'].bind("<Enter>", lambda e, a=['numerator', 'divisor', 'line']: rate_color_change(e, a))
    frames['left-stats'].bind("<Leave>", lambda e, a=['numerator', 'divisor', 'line']: rate_color_change(e, a))

    # -------------------------------------------
    # For mid-stats, which displays the cap rate as a percentage
    frames['rate'] = Label(frames['mid-stats'],
                           bg=frames['mid-stats']['bg'],
                           font=Font(family="Book Antiqua", size=15, weight='bold'),
                           fg='white', text="Rate:   ")
    frames['rate'].grid(row=0, column=0, sticky='s')
    frames['percent'] = Label(frames['mid-stats'],
                              bg=frames['mid-stats']['bg'],
                              font=Font(family="Book Antiqua", size=30, weight='bold'),
                              fg='white', text="0.0")
    frames['percent'].grid(row=0, column=1, sticky='e')
    frames['%'] = Label(frames['mid-stats'],
                        bg=frames['mid-stats']['bg'],
                        font=Font(family="Book Antiqua", size=15, weight='bold'),
                        fg='white', text="%")
    frames['%'].grid(row=0, column=2, sticky='s')

    frames['mid-stats'].bind("<Button-1>", lambda e: copy_percentage())
    frames['percent'].bind("<Button-1>", lambda e: copy_percentage())
    frames['rate'].bind("<Button-1>", lambda e: copy_percentage())
    frames['%'].bind("<Button-1>", lambda e: copy_percentage())

    # -------------------------------------------
    # For right-stats, which displays cap streak info

    frames['streak'] = Label(frames['right-stats'],
                             bg=frames['right-stats']['bg'],
                             font=Font(family="Book Antiqua", size=15, weight='bold'),
                             fg='white', text="Streak:   ")
    frames['streak'].grid(row=0, column=0, sticky='s')
    frames['st'] = Label(frames['right-stats'],
                         bg=frames['right-stats']['bg'],
                         font=Font(family="Book Antiqua", size=30, weight='bold'),
                         fg='white', text="0")
    frames['st'].grid(row=0, column=1, sticky='e')
    frames['fire'] = Label(frames['right-stats'],
                           bg=frames['right-stats']['bg'],
                           fg='white', image=images['flame'])
    frames['fire'].grid(row=0, column=2, sticky='e')

    frames['max'] = Label(frames['right'],
                          bg=frames['right']['bg'],
                          font=Font(family="Book Antiqua", size=10, weight='bold'),
                          # fg='white', text="Best:   0",
                          fg='white', text='',
                          )
    frames['max'].place(x=465, y=180)

    frames['right-stats'].bind("<Button-1>", lambda e: copy_streak())
    frames['st'].bind("<Button-1>", lambda e: copy_streak())
    frames['streak'].bind("<Button-1>", lambda e: copy_streak())
    frames['fire'].bind("<Button-1>", lambda e: copy_streak())
    frames['max'].bind("<Button-1>", lambda e: copy_streak())

    # -------------------------------------------
    # For left-stats, which displays the cap rate as a fraction (XX/15)

    frames['numerator'] = Label(frames['left-stats'],
                                bg=frames['left-stats']['bg'],
                                font=Font(family="Book Antiqua", size=50, weight='bold'),
                                fg='white', text="0")
    frames['numerator'].grid(row=0, column=0, sticky='s')
    frames['line'] = Label(frames['left-stats'],
                           bg=frames['left-stats']['bg'],
                           font=Font(family="Book Antiqua", size=40, weight='bold'),
                           fg='white', text="—")
    frames['line'].grid(row=1, column=0)
    frames['divisor'] = Label(frames['left-stats'],
                              bg=frames['left-stats']['bg'],
                              font=Font(family="Book Antiqua", size=50, weight='bold'),
                              fg='white', text="0")
    frames['divisor'].grid(row=2, column=0, pady=10)

    frames['left-stats'].bind("<Button-1>", lambda e: copy_rate())
    frames['numerator'].bind("<Button-1>", lambda e: copy_rate())
    frames['divisor'].bind("<Button-1>", lambda e: copy_rate())
    frames['line'].bind("<Button-1>", lambda e: copy_rate())

    # Initializes the 'Text Copied!' image
    make_image('copied', (150, 60))
    frames['copied'] = Label(frames['right'],
                             bg=frames['right']['bg'],
                             fg='white', image=images['copied'])  # winfo_width() == 154
    # The same image, but with a different parent frame
    frames['copied_pattern'] = Label(frames['left'],
                                     bg=frames['left']['bg'],
                                     fg='white', image=images['copied'])

    canvas_redo(False)


# -----------------------------------------------------------------------------


def rate_color_change(e: Event, names: list) -> None:
    """
    When mousing over a frame with selectable text, this function darkens the text color of all labels in that frame.
    Mousing out is also handled by this function.
    ------------

    :param e: tkinter.event :
        Either an enter or leave event
    :param names: list of str :
        The names of all of the elements that should have their colors changed concurrently
    :return:
    """

    for name in names:
        if str(e.type) == 'Enter':
            frames[name]['fg'] = '#bababa'
        else:
            frames[name]['fg'] = 'white'


# -----------------------------------------------------------------------------


def color_grad() -> list:
    """
    Creates a color gradient for the canvas graph.
    ------------

    :return: list of str
        The array of colors to be used for the canvas graph as hex values
    """

    # cyan's hex code is 0x00ffff
    # white's  is        0xffffff

    # If the set is completed and the cap rate is 100%, enable special color change
    perfect = (this_set.count(1) == set_size)
    purple = True

    if not perfect or set_size < 10:
        # For cyan shades, only one RGB value needs to be changed
        diff = 150 / set_size
    else:
        diff = []
        if purple:
            # For purple shades, two values need to be changed
            diff.append(255 / set_size)
            diff.append(64 / set_size)
        else:
            # Unused gold color to match the golden flame. Didn't look as nice
            diff.append((255 - 160) / set_size)
            diff.append(255 / set_size)

    arr = []
    for color in range(set_size):
        if not perfect or set_size < 10:
            # Disables the fancy purple gradient if the set size is only 5.
            new_color = '#%x' % int(255 - (diff * color))
            new_color += 'ffff'
        else:
            mid = '%x' % (255 - int(diff[0] * color))
            if len(mid) < 2:
                mid = '0' + mid
            end = '%x' % (255 - int(diff[1] * color))
            new_color = '#ff' + mid + end

        arr.append(new_color)

    if not perfect:
        # Only successful caps will change the gradient. For instance, a (0 / 15) set will be fully white on the graph.
        mistake_grad = []
        index = 0
        for x in range(set_size):
            if this_set[x] == 1:
                index += 1
            mistake_grad.append(arr[index])
        arr = mistake_grad

    return arr


# -----------------------------------------------------------------------------


def mute() -> None:
    """
    Toggles mute on the audio sfx for everything.
    ------------

    :return: None
    """

    global muted
    muted = not muted
    if not muted:
        manage_audio('progress-complete')


# -----------------------------------------------------------------------------


def calculate(arr: list, current: int, perc: bool) -> list:
    """
    Calculates the graph's bars' heights based on either percentage of successful caps or on total caps.
    ------------

    :param arr: list of ints :
        The set to calculate things for. Will always be 'this_set'
    :param current: int :
        Index of the current set item. Will always be 'this'
    :param perc: bool :
        Whether to calculate is as a percentage of caps, or a percentage of caps out of 15
    :return: list :
        An array of floats from 0 to 1, representing the proportions of heights of bars on a graph
    :exception: ZeroDivisionError
        If arr is an empty list, division by zero can occur
    """

    ret = []
    for x in range(current):
        if perc:
            ret.append(arr[:x + 1].count(1) / (x + 1))
        else:
            ret.append(arr[:x + 1].count(1) / len(arr))
    return ret


# -----------------------------------------------------------------------------


def find_max_streak() -> int:
    """
    Finds the maximum streak achieved in the current set.
    ------------

    :return: int
        The value of the max streak
    """

    st = 0
    max_st = 0
    index = this - 1
    while index >= 0:
        if this_set[index] == 1:
            st += 1
            if st > max_st:
                max_st = st
        else:
            st = 0
        index -= 1
    return max_st


# -----------------------------------------------------------------------------


def find_streak() -> int:
    """
    Finds the current streak.
    ------------

    :return: int
        The value of the current streak
    """
    st = 0
    index = this - 1
    while this_set[index] == 1 and index >= 0:
        st += 1
        index -= 1
    return st


# -----------------------------------------------------------------------------


def manage_audio(custom_request: str = '') -> None:
    """
    Responsible for creating a thread to play audio and playing it. Plays a combo sound if no argument is given.
    ------------
    
    :param custom_request: str :
        The name of a wav file (extension omitted) of a sound to be played.
        by default, it will play a combo sound
    :return: None
    """

    global streak

    if muted:
        return

    if not custom_request:
        if this_set[this - 1] == 2:
            # If the most recent result was a miss
            audio = AudioSegment.from_file(f'sprites/fruit/Visceral-impact-{(this_set.count(2) % 3) + 1}.wav')
        elif streak == set_size:
            if set_size > 5:
                # For perfect full sets with a size above 5
                audio = AudioSegment.from_file(f'sprites/fruit/starfruit-buy.wav')
            else:
                # For perfect full sets of size 5. A less impactful sound
                audio = AudioSegment.from_file(f'sprites/fruit/new-best-score.wav')
        elif streak > 14:
            # Fanciest combo sound apart from starfruit-buy. For very large streaks
            tmp = AudioSegment.from_file(f'sprites/fruit/extra-life.wav')
            audio = tmp.overlay(AudioSegment.from_file(f'sprites/fruit/combo.wav'))
        elif streak <= 8:
            # Nice combo sound. For respectable streaks
            audio = AudioSegment.from_file(f'sprites/fruit/combo-{streak}.wav')
        else:
            # Fancy combo sound. For fairly large streaks
            tmp = AudioSegment.from_file(f'sprites/fruit/combo-blitz-{(streak % 8)}.wav')
            audio = tmp.overlay(AudioSegment.from_file(f'sprites/fruit/combo-{(streak % 8)}.wav'))
    else:
        # For audio from other functions, usually unrelated to combo sounds
        audio = AudioSegment.from_file(f'sprites/fruit/{custom_request}.wav')

    audio -= 20
    # Volume is loud and my ears are sensitive

    t = threading.Thread(target=play, args=(audio,))
    # Sfx are played in a thread so that they don't pause the rest of the functions of the program
    t.start()


# -----------------------------------------------------------------------------


def lock(toggle: bool = True) -> None:
    """
    Disables keyboard input in the program via the locked variable. Draws the graph in grey and adds some chains.
    ------------

    :param toggle: bool :
        Whether to change the locked variable. In case you need to redraw the graph in grey without locking/unlocking
    :return: 
    """

    global this
    global locked

    frames['canvas'].delete('all')
    # Clear the canvas

    if toggle:
        locked = not locked

    if not locked:
        # Undo the effects of locking
        frames['fire']['image'] = images['flame']
        frames['right-chains'].place_forget()
        frames['left-chains'].place_forget()
        manage_audio('powerup-deflect')
        canvas_redo(False)
        root.title("Spellcard Sets")
        return

    if toggle:
        # Looks redundant, but putting this earlier on makes it play when it shouldn't
        # and putting the stuff from earlier here causes problems
        manage_audio('equip-locked')

    root.title("Spellcard Sets (locked)")

    frames['fire']['image'] = images['grey flame']

    start = 20  # Starting x-value for the graph
    min_height = 20

    gap_size = 5
    gap = (set_size - 1) * gap_size
    # Gaps between bars in the graph

    size = ((canvas_size[0] + gap_size) - gap) / set_size
    # Horizontal size of each bar in the graph. Scales with set_size

    # Draws the grey bars for the graph at 0%, 50%, and 100%
    frames['canvas'].create_rectangle((start, min_height, (size + gap_size) * set_size + start,
                                       min_height + 5), fill=ROOT_BG, width=0)
    frames['canvas'].create_rectangle((start, min_height + (canvas_size[1] / 2), (size + gap_size) * set_size + start,
                                       min_height + (canvas_size[1] / 2) + 5), fill=ROOT_BG, width=0)
    frames['canvas'].create_rectangle((start, canvas_size[1] + 15, (size + gap_size) * set_size + start,
                                       canvas_size[1] + 20), fill=ROOT_BG, width=0)

    arr = calculate(this_set, this, percentage)
    # The heights of all the bars to be drawn on the canvas

    for set_item in range(0, this):
        # For each nonzero value in this_set, draw a bar on the graph

        start = (size + gap_size) * set_item + 20
        # The starting x value of the current bar

        h = min(((1 - arr[set_item]) * canvas_size[1]) + 20, 245)
        # Bars have a minimum size of 10px, so that you can still see graph bars at 0%

        frames['canvas'].create_rectangle((start, h, start + size, 250), fill='#999999', width=0)
        # Drawing the bars themselves

        if set_item + 1 == this:
            # Only draw text for the most recent bar
            if percentage:
                # Text is a percentage of the current cap rate
                frames['canvas'].create_text(start + (size / 2), 8, fill='white',
                                             font=Font(family="Book Antiqua", size=15, weight='bold'),
                                             text=int(arr[set_item] * 100))
            else:
                # Text is the current number of caps
                frames['canvas'].create_text(start + (size / 2), 8, fill='white',
                                             font=Font(family="Book Antiqua", size=15, weight='bold'),
                                             text=this_set.count(1))

    if toggle:
        frames['right-chains'] = Label(frames['right'],
                                       bg=frames['right']['bg'],
                                       fg='white', image=images['right-chains'])
        frames['right-chains'].place(relx=0.775, y=-25)

        frames['left-chains'] = Label(frames['right'],
                                      bg=frames['right']['bg'],
                                      fg='white', image=images['left-chains'])
        frames['left-chains'].place(x=-45, y=0)
        # The world if tkinter let you make the frames containing labels with transparent .png images transparent too:


# -----------------------------------------------------------------------------


def canvas_redo(play_sound: bool = True) -> None:
    """
    The most important function in the program. Draws the bar graph and handles a ton of smaller things
    like streak flames, updating statistic display values, and more.
    ------------

    :param play_sound:
    :return:
    """

    global this
    global streak
    global max_streak

    streak = find_streak()

    if play_sound:
        manage_audio()

    if this > 0:
        # Causes a ZeroDivisionError if done outside of an if statement
        percent = round((this_set.count(1) / this) * 100, 1)
        frames['percent']['text'] = percent

        # There can only be a max streak if cap attempts have been made
        max_streak = find_max_streak()
        if max_streak > 1 and max_streak > streak:
            # If the current streak is the current best, no need to display the current best.
            # Same goes for if the best streak is only one cap "in a row."
            frames['max']['text'] = f'Best:   {max_streak}'
        else:
            frames['max']['text'] = ''
    else:
        frames['percent']['text'] = '0.0'
        frames['max']['text'] = ''

    frames['st']['text'] = streak
    frames['numerator']['text'] = this_set.count(1)
    frames['divisor']['text'] = this

    # Get the list containing color gradient values for the bars on the graph
    colors = color_grad()

    frames['canvas'].delete('all')

    # Everything from here on out is more or less as seen in the lock() function.
    # I originally had a lot of redundant code here, but I cleaned it up when I implemented locking, then copied it over

    gap_size = 5
    gap = (set_size - 1) * gap_size
    size = ((canvas_size[0] + gap_size) - gap) / set_size

    start = 20
    min_height = 20
    frames['canvas'].create_rectangle((start, min_height, (size + gap_size) * set_size + start,
                                       min_height + 5), fill=ROOT_BG, width=0)
    frames['canvas'].create_rectangle((start, min_height + (canvas_size[1] / 2), (size + gap_size) * set_size + start,
                                       min_height + (canvas_size[1] / 2) + 5), fill=ROOT_BG, width=0)
    frames['canvas'].create_rectangle((start, canvas_size[1] + 15, (size + gap_size) * set_size + start,
                                       canvas_size[1] + 20), fill=ROOT_BG, width=0)

    if frames['fire']['image'] != images['flame'] and streak != set_size:
        frames['fire']['image'] = images['flame']
    else:
        # Display a golden flame by the streak counter if and only if the full set is completed perfectly
        frames['fire']['image'] = images['golden flame']

    arr = calculate(this_set, this, percentage)

    if not len(arr):
        return

    if this > 0:
        arr = calculate(this_set, this, percentage)
    else:
        arr = [0]

    for set_item in range(0, this):
        start = (size + gap_size) * set_item + 20

        h = min(((1 - arr[set_item]) * canvas_size[1]) + 20, 245)

        # I use a list for colors, unlike in lock(), since it displays in a gradient instead of one solid color
        frames['canvas'].create_rectangle((start, h, start + size, 250), fill=colors[set_item], width=0)
        if set_item + 1 == this:
            if percentage:
                frames['canvas'].create_text(start + (size / 2), 8, fill='white',
                                             font=Font(family="Book Antiqua", size=15, weight='bold'),
                                             text=int(arr[set_item] * 100))
            else:
                frames['canvas'].create_text(start + (size / 2), 8, fill='white',
                                             font=Font(family="Book Antiqua", size=15, weight='bold'),
                                             text=this_set.count(1))


# -----------------------------------------------------------------------------


def make_boxes() -> None:
    """
    Makes the check boxes that keep track of set results. Also handles some event binding.
    ------------

    :return: None
    """

    global set_size

    rows = set_size // 5

    for x in range(ALL_SIZES[-1] // 5):
        # Configure rows. Check boxes are displayed in groups of 5
        frames['boxes'].grid_rowconfigure(x, weight=1)

    frames['internal'] = []
    for x in range(rows):
        frames['internal'].append(Frame(frames['boxes'], bg="#484848", width=frames['boxes']['width'], height=50))
        frames['internal'][-1].grid_propagate(False)
        frames['internal'][-1].grid_rowconfigure(0, weight=1)
        for i in range(1, 6):
            frames['internal'][-1].grid_columnconfigure(i, weight=2)

        # Arbitrary weight value on slots on either side of the checkboxes so I can center them a bit more
        frames['internal'][-1].grid_columnconfigure(0, weight=6)
        frames['internal'][-1].grid_columnconfigure(6, weight=6)

        frames['internal'][-1].grid(row=x, column=0, sticky="n")

    frames['checks'] = []
    for y in range(rows):
        for x in range(1, 6):
            frames['checks'].append(Label(frames['internal'][y],
                                          bg=frames['boxes']['bg'],
                                          image=images['unchecked'],
                                          highlightthickness=1,
                                          ))
            frames['checks'][-1].grid(row=0, column=x)
    for i in range(this):
        if this_set[i] == 2:  # 2 == miss
            frames['checks'][i]['image'] = images['x']
        elif this_set[i] == 1:  # 1 == cap
            frames['checks'][i]['image'] = images['o']
        else:
            break

    # Because the frame is so much bigger than where the checkboxes are, a motion tracker is used to determine when
    # the cursor enters an area around where the checkboxes themselves are displayed.
    frames['boxes'].bind("<Motion>", lambda e, h=frames['internal'][-1].winfo_y: frame_motion(e))
    frames['boxes'].bind("<Leave>", lambda e: frame_color(e))

    for frame in frames['internal']:
        frame.bind("<Enter>", lambda e: frame_color(e))
        frame.bind("<Leave>", lambda e: frame_color(e))
        frame.bind("<Button-1>", lambda e: copy_pattern(e))

    for check in frames['checks']:
        check.bind("<Button-1>", lambda e: copy_pattern(e))
    frames['boxes'].bind("<Button-1>", lambda e: copy_pattern(e))


# -----------------------------------------------------------------------------


def copy_pattern(event: Event) -> None:
    """
    Copies the pattern of caps and misses and O's and X's, respectively, to clipboard.
    ------------

    :param event: Event :
        Tkinter event automatically generated and passed to this function
    """

    global copy_id

    if this == 0:
        return
    if str(event.widget) == '.!frame.!frame':
        # Checks if the current widget is the 'boxes' frame, in which case verify that the cursor is close enough to
        # where the checkboxes are before letting the function continue.
        if event.y > frames['internal'][-1].winfo_y():
            return

    # If you get one cap, followed by two misses, followed by two more caps, the result will be:
    #                                                                               OXXOO
    string = ''
    for index in range(this):
        if this_set[index] == 1:
            string += 'O'
        elif this_set[index] == 2:
            string += 'X'
        if ((index + 1) % 5) == 0:
            string += '\n'

    pyperclip.copy(string.strip())

    if copy_id[0]:
        # If a notification for text being copied already exists,
        # remove it, replace it where needed, then reset the timer for when it disappears again.
        root.after_cancel(copy_id[0])
        copy_id[1].place_forget()

    frames['copied_pattern'].place(x=88, y=frames['internal'][-1].winfo_y() + 75)

    copy_id = (root.after(1000, lambda: frames['copied_pattern'].place_forget()), frames['copied_pattern'])

    manage_audio('powerup-starfruit')


# -----------------------------------------------------------------------------


def copy_streak() -> None:
    """
    Copies the best streak of the set to clipboard. Copying the current streak would be more intuitive but less useful.
    ------------

    :return: None
    """

    global copy_id

    if this == 0:
        return

    pyperclip.copy(max_streak)

    if copy_id[0]:
        root.after_cancel(copy_id[0])
        copy_id[1].place_forget()

    frames['copied'].place(x=frames['right-stats'].winfo_x(), y=200)

    copy_id = (root.after(1000, lambda: frames['copied'].place_forget()), frames['copied'])

    manage_audio('powerup-starfruit')


# -----------------------------------------------------------------------------


def copy_rate() -> None:
    """
        Copies the cap rate as a fraction to clipboard.
        ------------

        :return: None
        """

    global copy_id

    if this == 0:
        return

    text = f'{this_set.count(1)}/{this}'

    pyperclip.copy(text)

    if copy_id[0]:
        root.after_cancel(copy_id[0])
        copy_id[1].place_forget()

    frames['copied'].place(x=frames['left-stats'].winfo_x() + 15, y=240)

    copy_id = (root.after(1000, lambda: frames['copied'].place_forget()), frames['copied'])

    manage_audio('powerup-starfruit')


# -----------------------------------------------------------------------------


def copy_percentage() -> None:
    """
    Copies the cap rate as a percentage to the clipboard.
    ------------

    :return: None
    """

    global copy_id

    if this == 0:
        return

    if not this_set.count(1):
        text = str(0) + '%'
    else:
        text = str(this_set.count(1) / this * 100) + '%'

    pyperclip.copy(text)

    if copy_id[0]:
        root.after_cancel(copy_id[0])
        copy_id[1].place_forget()

    frames['copied'].place(x=frames['mid-stats'].winfo_x() + 15, y=200)

    copy_id = (root.after(1000, lambda: frames['copied'].place_forget()), frames['copied'])

    manage_audio('powerup-starfruit')


# -----------------------------------------------------------------------------


def frame_color(event: Event) -> None:
    """
    Changes the frame color of the frame containing the checkboxes when the user mouses over them.
    ------------

    :param event: Event :
        The tkinter event automatically passed to the function when the event is triggered.
    :return:
    """

    if str(event.type) == 'Enter':
        for frame in frames['internal']:
            frame['bg'] = '#686868'
    else:
        for frame in frames['internal']:
            frame['bg'] = '#484848'


# -----------------------------------------------------------------------------


def frame_motion(event: Event) -> None:
    """
    Changes the frame color of the frame containing the checkboxes. Since the containing frame is much bigger,
    check if the mouse is close enough to the checkboxes first.
    ------------

    :param event: Event :
        The tkinter event automatically passed to the function when the event is triggered.
    :return:
    """

    if event.y > frames['internal'][-1].winfo_y():
        for frame in frames['internal']:
            if frame['bg'] != '#484848':
                frame['bg'] = '#484848'
        return
    for frame in frames['internal']:
        if frame['bg'] != '#686868':
            frame['bg'] = '#686868'


# -----------------------------------------------------------------------------


def on_press(key: keyboard) -> None:
    """
    Checks keystrokes for 1's, 2's, and 3's, which correspond to functions of the program.
    1 removes a set value, 2 adds a miss, and 3 adds a cap. This function is disabled when the locked state is active.
    ------------

    :param key: Keyboard key :
        A keystroke registered by a keyboard listener
    :return: None
    """

    global this_set
    global this

    start = this
    # For easy access if it's determined that changing the size of the set is not possible

    if locked:
        # Don't do anything with key input if locked
        return

    try:
        reverse = key.char == '1'
        # If key input is 1, remove an entry from the set
        if reverse:
            if this == 0:
                manage_audio('gank')
                return
            manage_audio('pome-zoomout')
            this = max(this - 1, 0)
            this_set[this] = 0
        elif this >= set_size:
            return

        if key.char == '3':
            # If key input is 3, add a cap to the set
            this_set[this] = 1
            this += 1
            if start > this:
                tmp = this_set[0]
                this_set = [0] * 15
                this_set[0] = tmp

        elif key.char == '2':
            # If key input is 2, add a miss to the set
            this_set[this] = 2
            this += 1
            if start > this:
                tmp = this_set[0]
                this_set = [0] * 15
                this_set[0] = tmp

        if start != this:
            canvas_redo(not reverse)

            # Ensure all of the checkbox states are correct
            for x in range(len(frames['checks'])):
                if this_set[x] == 0:
                    frames['checks'][x]['image'] = images['unchecked']
                elif this_set[x] == 1:
                    frames['checks'][x]['image'] = images['o']
                else:
                    frames['checks'][x]['image'] = images['x']
    except AttributeError:
        # For special keys not handled by the listener
        pass


# -----------------------------------------------------------------------------

try:
    with keyboard.Listener(on_press=on_press) as listener:
        root.protocol('WM_DELETE_WINDOW', lambda l=listener: quit_root(l))
        make_window()
        root.mainloop()
        listener.join()
except Exception as ex:
    root.destroy()
    raise ex
# ----------------
# --------
# --
