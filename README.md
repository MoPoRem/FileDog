# FileDog
A python script to watch over file and directory changes.

If you are like me, you would like to know when programs create/delete or alter files in your system. with this script you can easily watch what files get changed and when do they get changed in the CMD. 
I'll try to update it with a GUI to reduce chaos (because every second there are 5/10 files changing in the C:\ directory).

## Installation

Currently, you can only clone this repo and run the script locally.

```bash
git cloen https://github.com/MoPoRem/FileDog.git
cd FileDoge/src
python watchdog.py
```

and thats it (if you have the requuirements, obviously)


## Requirements

This project requires win32 package which can be installed with:

`pip install pywin32`


## Usage

After running the scripts, you can specify which paths to watch over. You can use "ALL" to watch over every directory in the system.
you can also separate paths with space

It will ignore all browser files by default, but you can edit that in the settings.

```bash
Enter a path ('ALL' to watch all drives/ seperate paths with space for multiple paths):
>> C:\ D:\
Starting watcher for directory: C:\...
Starting watcher for directory: D:\...
```
