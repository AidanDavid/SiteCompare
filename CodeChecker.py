"""
File: CodeChecker.py
Author: Aidan David
Date: 2024-01-29
Description: Compares code files to help determine where similar code has be altered.
Makes use of LinkChecker class to find and test links in a file.
"""
import os
import re
import difflib
from LinkChecker import LinkChecker
from prettytable import PrettyTable


class CodeChecker:
    def __init__(self, path1="", path2="", str1="", str2=""):
        self.path1 = path1
        self.path2 = path2
        self.str1 = str1
        self.str2 = str2
        self.identical = True
        self.result = "Call compare() first"

    # replace \t char with spaces to make string length match output
    def replace_tabs(self, in_string, tab_width=4):
        return in_string.replace('\t', ' ' * tab_width)

    # gives identical or table
    def get_result(self):
        return self.result

    # splits a string into strings of a max size
    def split_string(self, input_string, chunk_size):
        return [input_string[i:i + chunk_size] for i in range(0, len(input_string), chunk_size)]

    # takes difflib content and organizes it into deletions, additions and mutual code (with colors and spacing)
    def color_number_split(self, content, column_width):
        # line numbers to help find changes in source code
        line_num1 = 1
        line_num2 = 1

        # printed lines to maintain line matching
        # i.e.   |1:+Hi      |           |
        #        |2: Hello   |1. Hello   |
        #        |3: Bye     |2. Bye     |
        # pline1 and pline2 help maintain this (for column 1 and 2)
        pline1 = 1
        pline2 = 1

        content1 = ""
        content2 = ""

        for i, line in enumerate(content):
            line_list = self.split_string(line, column_width)
            # lines not in either file
            if line[0] == '?':
                pass
            # added lines
            elif line[0] == '+':
                self.identical = False
                # color line number only to avoid colour bleed (green)
                green_num = '\033[92m{}\033[0m'.format(line_num2)
                #                                                                                    [1:] skips '+'
                content2 = content2 + '\033[92m{}\033[0m'.format(f'{green_num}: {self.replace_tabs(line_list[0][1:])}')
                # lines over max_width
                for item in line_list[1:]:
                    content2 = content2 + '\n' + item
                    pline2 += 1
                # previous deletion longer than addition
                if pline1 > pline2:
                    while pline1-1 > pline2:
                        content2 = content2 + '\n'
                        pline2 += 1
                # increase counters
                line_num2 += 1
                pline2 += 1
            # deleted lines
            elif line[0] == '-':
                self.identical = False
                # color line number only to avoid colour bleed (red)
                red_num = '\033[91m{}\033[0m'.format(line_num1)
                #                                                                                  [1:] skips '-'
                content1 = content1 + '\033[91m{}\033[0m'.format(f'{red_num}: {self.replace_tabs(line_list[0][1:])}')
                for item in line_list[1:]:
                    content1 = content1 + '\n' + item
                    pline1 += 1
                # increase counters
                line_num1 += 1
                pline1 += 1
            # shared lines
            else:
                # color line number only to avoid colour bleed (white)
                white_num = '\033[97m{}\033[0m'.format(line_num1)
                content1 = content1 + f'{white_num}: {self.replace_tabs(line_list[0])}'
                white_num = '\033[97m{}\033[0m'.format(line_num2)
                content2 = content2 + f'{white_num}: {self.replace_tabs(line_list[0])}'
                for item in line_list[1:]:
                    content1 = content1 + '\n' + item
                    content2 = content2 + '\n' + item
                # increase counters
                line_num1 += 1
                line_num2 += 1

            # add empty lines to line up the output, this may still be uneven if lines are too long
            if pline1 > pline2:
                # deletion followed by common line
                if i < len(content) - 1 and content[i + 1][0] != '?' and content[i + 1][0] != '+':
                    while pline1 > pline2:
                        content2 = content2 + '\n'
                        pline2 += 1
            # additions make more printed lines
            elif pline1 < pline2:
                while pline1 < pline2:
                    content1 = content1 + '\n'
                    pline1 += 1

        # 2 full code sets colored and organized
        return content1, content2

    # strings to be compared line by line and put in table
    def compare_strings(self):
        # get lines from string
        str1_lines = self.str1.splitlines()
        str2_lines = self.str2.splitlines()

        # make them into proper line (newline)
        for i in range(0, len(str1_lines)-1):
            str1_lines[i] = str1_lines[i] + '\n'

        for j in range(0, len(str2_lines)-1):
            str2_lines[j] = str2_lines[j] + '\n'

        # get differences
        diffs = list(difflib.ndiff(str1_lines, str2_lines))

        # column_width used to ensure code lines up correctly (feel free to change)
        column_width = 100
        new_content1, new_content2 = self.color_number_split(diffs, column_width)

        # print they are identical, else print code with differences
        if self.identical:
            self.result = "Files are identical!"
        else:
            table = PrettyTable(['\033[97m{}\033[0m'.format(f'Code 1'),
                                 '\033[97m{}\033[0m'.format(f'Code 2')])
            table.align['\033[97m{}\033[0m'.format(f'Code 1')] = "l"
            table.align['\033[97m{}\033[0m'.format(f'Code 2')] = "l"
            table.add_row([new_content1, new_content2])

            self.result = table

    # takes local path, makes strings to be compared line by line and put in table
    def compare_files(self):
        # make sure path points to a file
        if not os.path.isfile(self.path1):
            self.result = "First path does not point to a file!"
            if not os.path.isfile(self.path2):
                self.result = self.result + "\nSecond path does not point to a file either!"
            return self.result
        elif not os.path.isfile(self.path2):
            self.result = "Second path does not point to a file!"
            return self.result
        else:
            # read the files
            with open(self.path1, 'r', encoding='utf-8') as f:
                content1 = f.readlines()
            with open(self.path2, 'r', encoding='utf-8') as f:
                content2 = f.readlines()

            # get differences
            diffs = list(difflib.ndiff(content1, content2))

            # column_width used to ensure code lines up correctly (feel free to change)
            column_width = 100
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

                self.result = table

    # gives printable responses (local file)
    def check_links_print_file(self):
        # check if file
        if not os.path.isfile(self.path1):
            return "Path does not point to a file!"
        # read the file
        else:
            with open(self.path1, 'r', encoding='utf-8') as f:
                content = f.readlines()

            # use to test any links found in html file
            lc = LinkChecker()

            # to see when and if links found
            links_list = []
            line_num = 1
            for line in content:
                # regex to find URLs
                regex = r'http[s]?://[^\s"<>\')]+'
                matches = re.findall(regex, line)

                # use link check on any links
                if matches:
                    for result in matches:
                        links_list.append(f"URL found on line {line_num}: {result}")
                        lc.link_check(result)
                        status = lc.get_status()
                        links_list.append(f"The URL above is {status}")
                line_num += 1

            if len(links_list) < 1:
                return "No links found!"
            return links_list

    # gives printable responses (local file)
    def check_links_print_string(self):
        # use to test any links found in html file
        lc = LinkChecker()

        # get string in lines
        lines = self.str1.splitlines()

        # to see when and if links found
        links_list = []
        line_num = 1
        for line in lines:
            # regex to find URLs
            regex = r'http[s]?://[^\s"<>\')]+'
            matches = re.findall(regex, line)

            # use link check on any links
            if matches:
                for result in matches:
                    links_list.append(f"URL found on line {line_num}: {result}")
                    lc.link_check(result)
                    status = lc.get_status()
                    links_list.append(f"The URL above is {status}")
            line_num += 1

        if len(links_list) < 1:
            return "No links found!"
        return links_list

    # returns number for failed links found in a file
    def check_links_file(self):
        # check if file
        if not os.path.isfile(self.path1):
            return "Path does not point to a file!"
        # read the file
        else:
            with open(self.path1, 'r', encoding='utf-8') as f:
                content = f.readlines()

            # use to test any links found in html file
            lc = LinkChecker()

            links_failed = 0  # 0 == all good, else 1+ failures
            line_num = 1
            for line in content:
                # regex to find URLs
                regex = r'http[s]?://[^\s"<>\')]+'
                matches = re.findall(regex, line)

                # use link check on any links
                if matches:
                    for result in matches:
                        lc.link_check(result)
                        if lc.get_code() >= 400:
                            links_failed += 1
                line_num += 1

            return links_failed

    # returns number for failed links found in a string
    def check_links_string(self):
        # use to test any links found in html file
        lc = LinkChecker()

        # get string in lines
        lines = self.str1.splitlines()

        links_failed = 0  # 0 == all good, else 1+ failures
        line_num = 1
        for line in lines:
            # regex to find URLs
            regex = r'http[s]?://[^\s"<>\')]+'
            matches = re.findall(regex, line)

            # use link check on any links
            if matches:
                for result in matches:
                    lc.link_check(result)
                    if lc.get_code() >= 400:
                        links_failed += 1
            line_num += 1

        return links_failed
