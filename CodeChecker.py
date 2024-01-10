import os
import re
import difflib
from LinkChecker import LinkChecker
from prettytable import PrettyTable


class CodeChecker:
    def __init__(self, path1, path2=""):
        self.path1 = path1
        self.path2 = path2
        self.identical = True
        self.result = "Call compare() first"

    def replace_tabs(self, in_string, tab_width=4):
        return in_string.replace('\t', ' ' * tab_width)

    def get_result(self):
        return self.result

    def color_number_split(self, content, column_width):
        # line numbers to help find changes in source code
        line_num1 = 1
        line_num2 = 1

        # printed lines to maintain line matching
        pline1 = 1
        pline2 = 1

        content1 = ""
        content2 = ""

        for i, line in enumerate(content):
            # lines not in either file
            if line[0] == '?':
                pass
            # added lines
            elif line[0] == '+':
                self.identical = False
                # color line number only to avoid colour bleed
                green_num = '\033[92m{}\033[0m'.format(line_num2)
                content2 = content2 + '\033[92m{}\033[0m'.format(f'{green_num}: {self.replace_tabs(line[1:])}')
                line_num2 += 1
                pline2 += 1
            # deleted lines
            elif line[0] == '-':
                self.identical = False
                # color line number only to avoid colour bleed
                red_num = '\033[91m{}\033[0m'.format(line_num1)
                content1 = content1 + '\033[91m{}\033[0m'.format(f'{red_num}: {self.replace_tabs(line[1:])}')
                line_num1 += 1
                pline1 += 1
            # shared lines
            else:
                white_num = '\033[97m{}\033[0m'.format(line_num1)
                content1 = content1 + f'{white_num}: {self.replace_tabs(line)}'
                white_num = '\033[97m{}\033[0m'.format(line_num2)
                content2 = content2 + f'{white_num}: {self.replace_tabs(line)}'
                line_num1 += 1
                line_num2 += 1

            # add empty lines to line up the output, this may still be uneven if lines are too long
            if pline1 > pline2:
                # deletion followed by common line
                if i < len(content)-1 and content[i+1][0] != '?' and content[i+1][0] != '+':
                    # adjust for lines being split into multiple lines by Pretty Table
                    for j in range(0, len(line), column_width):
                        content2 = content2 + '\n'
                    pline2 += 1
                # deletion followed by addition
                else:
                    # see if deletion and addition are going to print different amounts of lines
                    column_diff = int((len(content[i])+len(str(line_num1))+len(": "))/column_width)\
                                  - int((len(content[i+1])+len(str(line_num2))+len(": "))/column_width)
                    # deletion is longer than addition
                    if column_diff > 0:
                        for k in range(0, column_diff):
                            content[i+1] = content[i+1] + '\n'
                    # addition is longer than deletion
                    elif column_diff < 0:
                        print("here")
                        for m in range(column_diff, 0, 1):
                            content1 = content1 + '\n'
            # additions
            elif pline1 < pline2:
                for n in range(0, len(line), column_width):
                    content1 = content1 + '\n'
                pline1 += 1

        return content1, content2

    def compare(self):

        # make sure path points to a file
        if not os.path.isfile(self.path1):
            print("First path does not point to a file!")
            if not os.path.isfile(self.path2):
                print("Second path does not point to a file either!")
        elif not os.path.isfile(self.path2):
            print("Second path does not point to a file!")
        else:
            # read the files
            with open(self.path1, 'r', encoding='utf-8') as f:
                content1 = f.readlines()
            with open(self.path2, 'r', encoding='utf-8') as f:
                content2 = f.readlines()

            # get differences
            diffs = list(difflib.ndiff(content1, content2))

            # column_width used for PrettTable, but also to ensure code lines up correctly (feel free to change)
            column_width = 80
            new_content1, new_content2 = self.color_number_split(diffs, column_width)

            # print they are identical, else print code with differences
            if self.identical:
                self.result = "Files are identical!"
            else:
                table = PrettyTable(['\033[97m{}\033[0m'.format(f'Path 1: {self.path1}'),
                                     '\033[97m{}\033[0m'.format(f'Path 2: {self.path2}')])
                table.align['\033[97m{}\033[0m'.format(f'Path 1: {self.path1}')] = "l"
                table.align['\033[97m{}\033[0m'.format(f'Path 2: {self.path2}')] = "l"
                table.add_row([new_content1, new_content2])
                table.max_width = column_width

                self.result = table

    # no return, only print
    def check_links_print(self):
        if not os.path.isfile(self.path1):
            print("Path does not point to a file!")
        else:
            with open(self.path1, 'r', encoding='utf-8') as f:
                content = f.readlines()

            # use to test any links found in html file
            lc = LinkChecker()

            link_found = False
            line_num = 1
            for line in content:
                # regex to find URLs
                regex = r'http[s]?://[^\s"<>\')]+'
                matches = re.findall(regex, line)

                if matches:
                    for result in matches:
                        print(f"URL found on line {line_num}: {result}")
                        lc.link_check(result)
                        status = lc.get_status()
                        print(f"The URL above is {status}")
                line_num += 1

            if not link_found:
                print("No links found!")

    # returns number for failed links
    def check_links(self):
        if not os.path.isfile(self.path1):
            print("Path does not point to a file!")
        else:
            with open(self.path1, 'r', encoding='utf-8') as f:
                content = f.readlines()

            # use to test any links found in html file
            lc = LinkChecker()

            links_failed = 0    # 0 == all good, else 1+ failures
            line_num = 1
            for line in content:
                # regex to find URLs
                regex = r'http[s]?://[^\s"<>\')]+'
                matches = re.findall(regex, line)

                if matches:
                    for result in matches:
                        print(f'link found: {result}')
                        lc.link_check(result)
                        if lc.get_code() >= 400:
                            links_failed += 1
                line_num += 1

            return links_failed
