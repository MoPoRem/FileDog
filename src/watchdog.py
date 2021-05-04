# Thanks to Tim Golden for the excellent examples of win32 package
import os
import sys
import threading
import re
import win32file
import win32con
import win32api
import datetime
import configparser




class Watcher(threading.Thread):

    def __init__(self, path_to_watch):
        self.run = True
        self.path_to_watch = path_to_watch
        self.config_file = configparser.ConfigParser()
        self.ACTIONS = {
          1 : "Created",
          2 : "Deleted",
          3 : "Updated",
          4 : "Renamed from something",
          5 : "Renamed to something"
        }


    def command(self, cmd):
        cmd_list = cmd.split(" ")
        if cmd_list[0].lower() == 'kill':
            print(f"Kill command issued for {self.path_to_watch}")
            self.run = False

        # TODO: DIC and separate function for each separate setting
        if cmd_list[0].lower() == 'ignore':
            if len(cmd_list) < 3 :
                print("Missing required arguments.")
                return
            if not cmd_list[3].isdecimal():
                print("Ignore value most of 0 or 1")
                return
            self.setConfig(cmd_list[1], cmd_list[2])



    def ignoreRegexCreator(self):
        regComp = 'a^'
        if int(self.config['IGNORE_BROWSER']) == 1:
            browsers = {
                'firefox': r"(\\Users\\.*\\AppData\\.*\\Mozilla)",
                'brave': r"(\\Users\\.*\\AppData\\.*\\BraveSoftware)",
                'edge': r"(\\Users\\.*\AppData\.*\\Microsoft\\Edge)"
            }
            regComp = '|'.join(browsers.values())
        self.regex = re.compile(regComp, re.IGNORECASE)



    def getConfig(self):
        self.config_file.read('settings.ini')
        if not hasattr(self, 'config'):
            self.config = {}
        if 'IGNORE' in self.config_file:
            self.config['IGNORE_BROWSER'] = self.config_file['IGNORE'].getint('IGNORE_BROWSER', 1)
        else:
            self.config['IGNORE_BROWSER'] = 1
            self.config_file['IGNORE'] = {}
            self.config_file['IGNORE']['IGNORE_BROWSER'] = '1'
        # print(f"Configs:\nIgnore Browsers:{self.config['IGNORE_BROWSER']}")
        self.ignoreRegexCreator()
        with open('settings.ini', 'w') as configfile:
            self.config_file.write(configfile)


    def setConfig(self, attr, value):
        if attr == 'browser':
            self.config['IGNORE_BROWSER'] = value
            print(f"Browser ignore set to: {self.config['IGNORE_BROWSER']}")
            self.ignoreRegexCreator()
        return True



    def start(self):
        print(f"Starting watcher for directory: {self.path_to_watch}...")
        self.getConfig()
        FILE_LIST_DIRECTORY = 0x0001
        hDir = win32file.CreateFile (
          self.path_to_watch,
          FILE_LIST_DIRECTORY,
          win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
          None,
          win32con.OPEN_EXISTING,
          win32con.FILE_FLAG_BACKUP_SEMANTICS,
          None
        )
        while self.run:
            results = win32file.ReadDirectoryChangesW(
            hDir,
            1024,
            True,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
             win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
             win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
             win32con.FILE_NOTIFY_CHANGE_SIZE |
             win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
             win32con.FILE_NOTIFY_CHANGE_SECURITY,
            None,
            None
            )
            for action, file in results:
                full_filename = os.path.join(self.path_to_watch, file)
                if not re.search(self.regex, full_filename):
                    try:
                        stats = os.stat(full_filename)
                        size = stats.st_size / (1024*1024)
                    except (FileNotFoundError, PermissionError):
                        size = 0
                    s = f"{datetime.datetime.now()} | {self.ACTIONS.get(action, 'Unknown')}-->{full_filename} {size:.2f}mb"
                    print(s)


def get_all_drives():
    drives = win32api.GetLogicalDriveStrings()
    drives = [d for d in drives.split('\000') if os.path.isdir(d)]
    return drives




def main():
    ptw = input("Enter a path ('ALL' to watch all drives/ seperate paths with space for multiple paths):")
    print(ptw.split(" "))
    path_to_watch = [os.path.abspath(path) for path in ptw.split(' ')]
    if ptw.lower() != 'all':
        while 1:
            fl = True
            for path in path_to_watch:
                if not os.path.isdir(path):
                    print(f"{path_to_watch} is not a valid directory")
                    path_to_watch = input("Please enter a valid directory to watch:")
                    if path_to_watch == 'all':
                        ptw = 'all'
                        break
                    path_to_watch = [os.path.abspath(path) for path in path_to_watch.split(' ')]
                    fl = False
            if fl: break
    watchers = []
    if ptw.lower() == 'all':
        drives = get_all_drives()
        for drive in drives:
            watchers.append(Watcher(drive))
    else:
        for path in path_to_watch:
            watchers.append(Watcher(path))
    functions = [watcher.start for watcher in watchers]
    threads = list()
    for f in functions:
        x = threading.Thread(target=f)
        threads.append(x)
        x.start()
    while 1:
        try:
            cmd = input("Enter action:")
            if cmd == 'kill':
                os._exit(1)
            for watcher in watchers:
                watcher.command(cmd)
        except (KeyboardInterrupt, SystemExit):
            sys.exit()
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    main()
