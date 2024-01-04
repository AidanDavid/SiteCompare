from FileChecker import FileChecker
from CodeChecker import CodeChecker
import os

class MainClass:
    def __init__(self):
        pass

    def fileComp(self, path1, path2, cc=False, lc=False):
        # production site path
        prodSite = path1 # example: "C:\Users\aidan\OneDrive\Desktop\Wget\websites\bravenlyglobal.com"
        # development site path
        devSite = path2 # example: "C:\Users\aidan\OneDrive\Desktop\Wget\websites\bravenlyglobal.d-solmedia.com"

        fc = FileChecker(prodSite, devSite, code_check=cc, link_check=lc)
        fc.makeTable()
        print(fc.getFileTable())

    def codeComp(self, path1, path2):
        # code 1 path
        file1 = path1 # "C:/Users/aidan/OneDrive/Desktop/CodeFiles/code1.txt"
        # code 2 path
        file2 = path2 # "C:/Users/aidan/OneDrive/Desktop/CodeFiles/code2.txt"

        cc = CodeChecker(file1, file2)
        cc.compare()
        print(cc.getResult())

    def linksCheck(self, path):
        file = path # "C:/Users/aidan/OneDrive/Desktop/CodeFiles/code3.html"

        cc = CodeChecker(file)
        cc.checkLinksPrint()

    def getCheckPath(self):
        working = False
        safePath = ""
        while not working:
            path = input("Enter a path: ")
            # backslashes may cause errors
            safePath = path.replace("\\", "/")
            working = os.path.exists(safePath)
            if not working:
                print("Invalid path")
        return safePath

    def get_check_sub_path(self, super_path):
        working = False
        safePath = super_path
        while not working:
            path = input("Enter filename: ")
            # backslashes may cause errors
            safePath = path.replace("\\", "/")
            working = os.path.exists(super_path + '/' + safePath)
            if not working:
                print("Invalid path")
        return safePath

def main():
    m = MainClass()

    answer = 'x'
    while answer != 'q':
        print("\n*\t*\t*\t*\t*\t*")
        print("*\tSite Compare\t*")
        print("*\t*\t*\t*\t*\t*\n")
        answer = input("What do you want to perform:\n"
                       "(f) File Comparison\n"
                       "(c) Code Comparison\n"
                       "(l) Link check (HTML file)\n"
                       "(q) Quit\n")

        if answer == 'f':
            # get/check first filepath
            path1 = m.getCheckPath()
            # get/check second filepath
            path2 = m.getCheckPath()

            reply = input("Code check (c) or link check (l) (else: neither), performed on files: ")
            if reply == 'c':
                m.fileComp(path1, path2, cc=True)
            elif reply == 'l':
                m.fileComp(path1, path2, lc=True)
            else:
                m.fileComp(path1, path2)
            ans = 'x'
            while ans != 'q' and ans != 'r':
                ans = input("\n\nWhat do you want to perform based on the table generated:\n"
                      "(c) Code Comparison\n"
                      "(l) Link check (HTML file)\n"
                      "(r) Return to Main Menu\n"
                      "(q) Quit\n")

                # perform code compare based on files found by FileChecker
                if ans == 'c':
                    print("\n^ Copy a filename with local path from above ^\n")
                    inp = 'x'
                    while inp != 'q':
                        inp = input("Is file in BOTH (b), PROD. (p), or DEV. (d): ")

                        # user wants to compare two files found in both sites
                        if inp == 'b':
                            test_path = m.get_check_sub_path(path1)
                            if os.path.exists(path2 + '/' + test_path):
                                m.codeComp(path1 + '/' + test_path, path2 + '/' + test_path)
                                break
                            else:
                                print("File is not found in BOTH, please pick another filename or category.")

                        # user wants to compare a production file against another file
                        elif inp == 'p':
                            test_path = m.get_check_sub_path(path1)
                            inp2 = 'x'
                            while inp2 != 'q':
                                inp2 = input("Is other file in PROD. (p), DEV. (d), or elsewhere (e): ")
                                if inp2 == 'p':
                                    test_path2 = m.get_check_sub_path(path1)
                                    m.codeComp(path1 + '/' + test_path, path1 + '/' + test_path2)
                                    break
                                elif inp2 == 'd':
                                    test_path2 = m.get_check_sub_path(path2)
                                    m.codeComp(path1 + '/' + test_path, path2 + '/' + test_path2)
                                    break
                                elif inp2 == 'e':
                                    e_path = m.getCheckPath()
                                    m.codeComp(path1 + '/' + test_path, e_path)
                                    break
                                elif inp2 == 'q':
                                    break
                                else:
                                    print("Enter p, d, or e")
                            break


                        # user wants to compare a development file against another file
                        elif inp == 'd':
                            test_path = m.get_check_sub_path(path2)
                            inp2 = 'x'
                            while inp2 != 'q':
                                inp2 = input("Is other file in PROD. (p), DEV. (d), or elsewhere (e): ")
                                if inp2 == 'p':
                                    test_path2 = m.get_check_sub_path(path1)
                                    m.codeComp(path2 + '/' + test_path, path1 + '/' + test_path2)
                                    break
                                elif inp2 == 'd':
                                    test_path2 = m.get_check_sub_path(path2)
                                    m.codeComp(path2 + '/' + test_path, path2 + '/' + test_path2)
                                    break
                                elif inp2 == 'e':
                                    e_path = m.getCheckPath()
                                    m.codeComp(path2 + '/' + test_path, e_path)
                                    break
                                elif inp2 == 'q':
                                    break
                                else:
                                    print("Enter p, d, or e")
                            break
                        elif inp == 'q':
                            break
                        else:
                            print("Enter b, p, or d")
                    break

                # perform LinkChecker on a file found by FileChecker
                elif ans == 'l':
                    print("\n^ Copy a filename with local path from above ^\n")
                    inp = 'x'
                    while inp != 'q':
                        inp = input("PROD. (p), or DEV. (d): ")
                        if inp == 'p':
                            test_path = m.get_check_sub_path(path1)
                            m.htmlCheck(path1 + '/' + test_path)
                            break
                        elif inp == 'd':
                            test_path = m.get_check_sub_path(path2)
                            m.htmlCheck(path2 + '/' + test_path)
                            break
                        elif inp == 'q':
                            break
                        else:
                            print("Enter p or d")

                # quit application
                elif ans == 'q':
                    answer = 'q'
                else:
                    "Enter c, l, r, or q"


        elif answer == 'c':
            # get/check first filepath
            path1 = m.getCheckPath()
            # get/check second filepath
            path2 = m.getCheckPath()
            m.codeComp(path1, path2)

        elif answer == 'l':
            path = m.getCheckPath()
            m.linksCheck(path)

        else:
            "Enter f, c, l, or q"

if __name__ == "__main__":
  main()