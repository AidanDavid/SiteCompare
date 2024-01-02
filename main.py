from FileChecker import FileChecker
from CodeChecker import CodeChecker
import os

class MainClass:
    def __init__(self):
        pass

    def callFileComp(self, path1, path2):
        # production site path
        prodSite = path1 # example: "C:\Users\aidan\OneDrive\Desktop\Wget\websites\bravenlyglobal.com"
        # development site path
        devSite = path2 # example: "C:\Users\aidan\OneDrive\Desktop\Wget\websites\bravenlyglobal.d-solmedia.com"

        fc = FileChecker(prodSite, devSite)
        fc.makeTable()
        print(fc.fileTable)

    def callCodeComp(self, path1, path2):
        # code 1 path
        file1 = path1 # "C:/Users/aidan/OneDrive/Desktop/CodeFiles/code1.txt"
        # code 2 path
        file2 = path2 # "C:/Users/aidan/OneDrive/Desktop/CodeFiles/code2.txt"

        cc = CodeChecker(file1, file2)
        cc.compare()

    def getCheckPath(self):
        working = False
        while not working:
            path = input("Enter path to compare: ")
            # backslashes may cause errors
            safePath = path.replace("\\", "/")
            working = os.path.exists(safePath)
            if not working:
                print("Invalid path")
        return safePath

def main():
    m = MainClass()

    answer = 'x'
    while answer != 'q':
        answer = input("What do you want to perform:\n(f) File Comparison\n(c) Code Comparison\n(q) Quit\n")
        if answer == 'f':
            # get/check first filepath
            path1 = m.getCheckPath()
            # get/check second filepath
            path2 = m.getCheckPath()
            m.callFileComp(path1, path2)

        elif answer == 'c':
            # get/check first filepath
            path1 = m.getCheckPath()
            # get/check second filepath
            path2 = m.getCheckPath()
            m.callCodeComp(path1, path2)
        else:
            "Enter f, c or q"

if __name__ == "__main__":
  main()