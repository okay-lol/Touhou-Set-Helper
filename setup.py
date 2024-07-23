from cx_Freeze import setup, Executable

base = None    

executables = [Executable("main.py", base = "Win32GUI")]

include_files = [('sprites', 'sprites')]

packages = ["tkinter", "PIL", "pydub", "pynput", "pyperclip", "threading"]

build_exe_options = {
    'packages': packages,
    'include_files': include_files,
}

setup(
    name = "<Spellcard Sets>",
    options = {'build_exe': build_exe_options},
    version = "0.0.0",
    description = '',
    executables = executables
)