# Welcome

This is a program designed to help make keeping track of touhou set attempts a lot easier and more convenient. 
No more having to tab into a google sheets page and check a box after each attempt. Just press 2 or 3 on your keyboard and this program will do the rest, even if you aren't tabbed in.

![Picture of program](https://cdn.discordapp.com/attachments/1132881701580845186/1265162213556224041/image.png?ex=66a081a1&is=669f3021&hm=f25ad67f7f5c598cff88205b9ce3098cb15050185761d4532751bdc207057767&)

How does it work? Essentially, it listens to keystrokes and checks to see if 1, 2, or 3 is inputted.

3 - The program will register a cap, and one of the checkboxes will be circled out. If you have sound enabled, you'll hear a fancy chime.

2 - The program will register a miss, and one of the checkboxes will be crossed out.

1 - The program will undo the most recent cap or miss, in case of misinput.

If you need to fill in any numbers anywhere and don't want the program mistakenly recording any more caps or misses while you do, the lock button will stop it from recording input until pressed again.

The redo button will completely clear the current set, starting fresh.

The up and down buttons allow you to customize the set's size. Possible values are 5, 10, 15, 25, and 50.

Toggles for muting audio and changing the graph display are also implemented.

Additionally, you can click on the check boxes, cap rate fraction, cap rate percentage, and streak, and the program will copy them to your clipboard as long as they aren't empty. This way, entering results into a spreadsheet or something is much less annoying.



# Installation

Unfortunately, lots of the convenience this program offers is cancelled out by it being an absolute pain to install. I'll try to describe it here; hopefully it works for you.

First of all, this will probably only work for Windows computers. I run Windows 10, so if that's what you run then it should work fine.
Otherwise, you're probably out of luck unless you already have extensive experience compiling programs and can troubleshoot the absolute hellscape that is terminal environments.
Compilation gets insanely complicated really quickly as soon as anything at all goes wrong — I'm not smart enough to be able to consistently do it on the OS I've been running for my whole life, much less on one I have no experience with.

Anyway, if you're on Windows 10, just follow the steps below and hopefully it'll work. It might also work on Windows 11. If you're on MAC or Linux or something, then I'm very sorry.

Step 1: Click on the dropdown arrow connected to the green "Code" button toward the top of this page. Click on "Download ZIP".

Step 2: Extract the contents using WinRAR or 7-zip. The only ones you need are main.py, easy_widgets.py, the sprites folder, and setup.py. Put them all in the same directory somewhere.

Step 3: Download and install miniconda. As of July 2024, you can use this link:
https://docs.anaconda.com/miniconda/#miniconda-latest-installer-links

Step 4: Open the miniconda terminal. If "miniconda" doesn't bring it up, try "anaconda".

Step 5: Create a python environment with python version 3.8. You can do this by typing the following into the miniconda terminal:

conda create -n myenv python=3.8

If it asks you to confirm anything, enter "yes".

Step 6: Activate your new conda environment. This can be done with the following command: conda activate myenv

Step 7: Install cx_Freeze with the following command: pip install cx_Freeze

If this goes wrong, double check you didn't make a typo. The capital F in "Freeze" is meant to be there. If it still doesn't work, then it looks like that's it. I'm sorry.

Step 8: Unfortunately, this is where luck really comes into play. Try to run the following commands. Given how many there are, some of them will probably fail.
Certain ones can fail and it won't matter. Others are necessary to get the program working, so if they don't work for you then this is probably the end of the road. Again, I'm sorry.

pip install tkinter

pip install pillow

pip install pydub

pip install pynput

pip install pyperclip

pip install threading

pip install pyaudio

Again, if a few of them failed, it isn't necessarily the end of the world. Like I said, some of them can fail and it's fine. Step 10 will determine whether this is the case here.

Step 9: Navigate to the path where you put the files from the ZIP file you downloaded earlier. Copy the path. It should look something like C:\Users\YourName\Documents\TouhouSets

Type "cd" into the conda terminal, then paste in the path you copied. If there are spaces in the names of any of the files, you may have to surround it in quotes.

cd "C:/Users/YourName/Documents/Spellcard Sets"

Step 10: This is where it either all comes together or all falls apart. If you did everything so far and luck was on your side, then this will all work out fine. Enter the following command into miniconda:

python setup.py build

If that doesn't work, then it isn't looking good. There's still one last variation on that command that you can try, however.

python3 setup.py build

If that doesn't work either, then unfortunately there's nothing I can help you with. Maybe google has a solution. If not, then I'm truly sorry, and thank you for stopping by.

If it did work, then there's one last luck check in your way. Go into the newly generated "build" folder. Then in a folder called "exe.win-amd64-3.8", you should find an exe file called "main".
Double-click the file to run it. If you get an error, then I'm sorry. You probably made it further than many others, but it just wasn't meant to be.

If it did work, then congratulations! I'm truly happy for you. If you want, feel free to make a shortcut and name it something other than main. There's also a .ico file in the sprites folder that you can use to change the icon so that it isn't the ugly default one that Windows uses. Anyway, that's about it. Hopefully this works for you. Best of luck!


