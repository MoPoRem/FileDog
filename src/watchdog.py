# Thanks to Tim Golden for the excellent examples of win32 package
import os
import threading
import re
import win32file
import win32con
import win32api
import datetime
import configparser




class Watcher():

    def __init__(self, path_to_watch):
        self.path_to_watch = path_to_watch
        self.config_file = configparser.ConfigParser()
        self.ACTIONS = {
          1 : "Created",
          2 : "Deleted",
          3 : "Updated",
          4 : "Renamed from something",
          5 : "Renamed to something"
        }


    def ignoreRegexCreator(self):
        regComp = ''
        if self.config['IGNORE_BROWSER']:
            browsers = {
                'firefox': r"(\\Users\\.*\\AppData\\.*\\Mozilla)",
                'brave': r"(\\Users\\.*\\AppData\\.*\\BraveSoftware)",

            }
            regComp = '|'.join(browsers.values())
        self.regex = re.compile(regComp, re.IGNORECASE)


    def getConfig(self):
        self.config_file.read('config.ini')
        self.config = {}
        if 'IGNORE' in self.config_file:
            self.config['IGNORE_BROWSER'] = self.config_file['IGNORE'].getint(['IGNORE_BROWSER'], 1)
        else:
            self.config['IGNORE_BROWSER'] = 1
            self.config_file['IGNORE'] = {}
            self.config_file['IGNORE']['IGNORE_BROWSER'] = '1'
        # print(f"Configs:\nIgnore Browsers:{self.config['IGNORE_BROWSER']}")
        self.ignoreRegexCreator()


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
        while 1:
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



def main():
    ptw = input("Enter a path ('ALL' to watch all drives/ seperate paths with space for multiple paths):")
    print(ptw.split(" "))
    path_to_watch = [os.path.abspath(path) for path in ptw.split(' ')]
    if ptw.lower() != 'all':
        while 1:
            fl = True
            for path in path_to_watch:
                if not os.path.isdir(path):
                    print(f"{path_to_watch=} is not a valid directory")
                    path_to_watch = input("Please enter a valid directory to watch:")
                    fl = False
            if fl:
                break

    watchers = []
    if ptw.lower() == 'all':
        drives = win32api.GetLogicalDriveStrings()
        drives = [d for d in drives.split('\000') if os.path.isdir(d)]
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
        input("Enter action:")



if __name__ == '__main__':
    main()
