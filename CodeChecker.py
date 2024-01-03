from LinkChecker import LinkChecker
from prettytable import PrettyTable
import difflib
import os
import re

class CodeChecker:
    def __init__(self, path1, path2=""):
        self.path1 = path1
        self.path2 = path2
        self.identical = True
        self.result = "Call compare() first"

    def getPath1(self):
        return self.path1

    def getPath2(self):
        return self.path2

    def getIdentical(self):
        return self.identical

    def notIdentical(self):
        self.identical = False

    def isIdentical(self):
        self.identical = True

    def getResult(self):
        return self.result

    def colorNumberSplit(self, content):
        # line numbers to help find changes in source code
        lineNum1 = 1
        lineNum2 = 1

        content1 = ""
        content2 = ""

        for line in content:
            # lines not in either file
            if line[0] == '?':
                lineNum1 -= 1
                lineNum2 -= 1
            # added lines
            elif line[0] == '+':
                self.notIdentical()
                # remove \n to avoid colour bleed
                content2 = content2 + '\033[92m{}\033[0m'.format(f'{lineNum2}: {line[:-1]}')
                # add it back
                if line[-1] != '\n':  # last line only
                    content2 = content2 + '\033[92m{}\033[0m'.format(f'{line[-1]}')
                else:
                    content2 = content2 + line[-1]
                lineNum2 += 1
            # deleted lines
            elif line[0] == '-':
                self.notIdentical()
                # remove last char to avoid colour bleed
                content1 = content1 + '\033[91m{}\033[0m'.format(f'{lineNum1}: {line[:-1]}')
                # add it back
                if line[-1] != '\n': # last line only
                    content1 = content1 + '\033[91m{}\033[0m'.format(f'{line[-1]}')
                else:
                    content1 = content1 + line[-1]
                lineNum1 += 1
            # shared lines
            else:
                content1 = content1 + f'{lineNum1}: {line}'
                content2 = content2 + f'{lineNum2}: {line}'
                lineNum1 += 1
                lineNum2 += 1

        return content1, content2

    def compare(self):

        # make sure path points to a file
        if not os.path.isfile(self.getPath1()):
            print("First path does not point to a file!")
            if not os.path.isfile(self.getPath2()):
                print("Second path does not point to a file either!")
        elif not os.path.isfile(self.getPath2()):
            print("Second path does not point to a file!")
        else:
            # read the files
            with open(self.getPath1(), 'r', encoding='utf-8') as f:
                content1: list[str] = f.readlines()
            with open(self.getPath2(), 'r', encoding='utf-8') as f:
                content2: list[str] = f.readlines()

            # get differences
            diffs = list(difflib.ndiff(content1, content2))

            newContent1, newContent2 = self.colorNumberSplit(diffs)

            # print they are identical, else print code with differences
            if self.getIdentical():
                self.result = "Files are identical!"
            else:
                table = PrettyTable(['\033[97m{}\033[0m'.format(f'Path 1: {self.path1}'), '\033[97m{}\033[0m'.format(f'Path 2: {self.path2}')])
                table.align['\033[97m{}\033[0m'.format(f'Path 1: {self.path1}')] = "l"
                table.align['\033[97m{}\033[0m'.format(f'Path 2: {self.path2}')] = "l"
                table.add_row([newContent1, newContent2])

                self.result = table

    def checkHTML(self):
        if not os.path.isfile(self.path1):
            print("Path does not point to a file!")
        else:
            with open(self.path1, 'r') as f:
                content = f.readlines()

            # use to test any links found in html file
            lc = LinkChecker()

            lineNum = 1
            for line in content:
                # regex to find URLs
                regex = r'http[s]?://[^\s"\')]+'
                matches = re.findall(regex, line)

                if matches:
                    for result in matches:
                        print(f"URL found on line {lineNum}: {result}")
                        lc.linkCheck(result)
                        status = lc.getStatus()
                        print(f"The URL above is {status}")
                else:
                    print(f"No URL found on line {lineNum}")

                lineNum += 1



