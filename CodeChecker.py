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

    def get_result(self):
        return self.result

    def color_number_split(self, content):
        # line numbers to help find changes in source code
        line_num1 = 1
        line_num2 = 1

        content1 = ""
        content2 = ""

        for line in content:
            # lines not in either file
            if line[0] == '?':
                pass
            # added lines
            elif line[0] == '+':
                self.identical = False
                # remove \n to avoid colour bleed
                content2 = content2 + '\033[92m{}\033[0m'.format(f'{line_num2}: {line[:-1]}')
                # add it back
                if line[-1] != '\n':  # last line only
                    content2 = content2 + '\033[92m{}\033[0m'.format(f'{line[-1]}')
                else:
                    content2 = content2 + line[-1]
                line_num2 += 1
            # deleted lines
            elif line[0] == '-':
                self.identical = False
                # remove last char to avoid colour bleed
                content1 = content1 + '\033[91m{}\033[0m'.format(f'{line_num1}: {line[:-1]}')
                # add it back
                if line[-1] != '\n':  # last line only
                    content1 = content1 + '\033[91m{}\033[0m'.format(f'{line[-1]}')
                else:
                    content1 = content1 + line[-1]
                line_num1 += 1
            # shared lines
            else:
                white_num = '\033[97m{}\033[0m'.format(line_num1)
                content1 = content1 + f'{white_num}: {line}'
                white_num = '\033[97m{}\033[0m'.format(line_num2)
                content2 = content2 + f'{white_num}: {line}'
                line_num1 += 1
                line_num2 += 1

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

            new_content1, new_content2 = self.color_number_split(diffs)

            # print they are identical, else print code with differences
            if self.identical:
                self.result = "Files are identical!"
            else:
                table = PrettyTable(['\033[97m{}\033[0m'.format(f'Path 1: {self.path1}'),
                                     '\033[97m{}\033[0m'.format(f'Path 2: {self.path2}')])
                table.align['\033[97m{}\033[0m'.format(f'Path 1: {self.path1}')] = "l"
                table.align['\033[97m{}\033[0m'.format(f'Path 2: {self.path2}')] = "l"
                table.add_row([new_content1, new_content2])
                table.max_width = 80

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
