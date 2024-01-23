"""
File: main.py
Author: Aidan David
Date: 2024-01-23
Description: Compares directories/folders and files based on organization, size, and modification date.
Can be further compared using CodeChecker (and LinkChecker)
"""
import os
import re
import time
from CodeChecker import CodeChecker
from prettytable import PrettyTable


class FileChecker:
    def __init__(self, prod_site_in, dev_site_in, code_check=False, link_check=False):
        # paths to be compared
        self.prod_site = prod_site_in
        self.dev_site = dev_site_in
        # to track files, avoid double printing
        self.processed_files = set()
        # possible extra checks/columns
        self.code_check = code_check
        self.link_check = link_check
        # prettytable file info
        # do code checks
        if code_check and link_check:
            self.file_table = PrettyTable([
                '\033[97m{}\033[0m'.format("Filename"), '\033[97m{}\033[0m'.format("Found"),
                '\033[97m{}\033[0m'.format("Code Match"),
                '\033[97m{}\033[0m'.format("Links Failed (PROD.)"), '\033[97m{}\033[0m'.format("Links Failed (DEV.)"),
                '\033[97m{}\033[0m'.format("Prod. Size (in Bytes)"), '\033[97m{}\033[0m'.format("Dev. Size (in Bytes)"),
                '\033[97m{}\033[0m'.format("Prod. Modified"), '\033[97m{}\033[0m'.format("Dev. Modified")])
        elif code_check:
            self.file_table = PrettyTable([
                '\033[97m{}\033[0m'.format("Filename"), '\033[97m{}\033[0m'.format("Found"),
                '\033[97m{}\033[0m'.format("Code Match"), '\033[97m{}\033[0m'.format("Prod. Size (in Bytes)"),
                '\033[97m{}\033[0m'.format("Dev. Size (in Bytes)"), '\033[97m{}\033[0m'.format("Prod. Modified"),
                '\033[97m{}\033[0m'.format("Dev. Modified")])
        # do link checks
        elif link_check:
            self.file_table = PrettyTable([
                '\033[97m{}\033[0m'.format("Filename"), '\033[97m{}\033[0m'.format("Found"),
                '\033[97m{}\033[0m'.format("Links Failed (PROD.)"), '\033[97m{}\033[0m'.format("Links Failed (DEV.)"),
                '\033[97m{}\033[0m'.format("Prod. Size (in Bytes)"), '\033[97m{}\033[0m'.format("Dev. Size (in Bytes)"),
                '\033[97m{}\033[0m'.format("Prod. Modified"), '\033[97m{}\033[0m'.format("Dev. Modified")])
        # standard table
        else:
            self.file_table = PrettyTable([
                '\033[97m{}\033[0m'.format("Filename"), '\033[97m{}\033[0m'.format("Found"),
                '\033[97m{}\033[0m'.format("Prod. Size (in Bytes)"), '\033[97m{}\033[0m'.format("Dev. Size (in Bytes)"),
                '\033[97m{}\033[0m'.format("Prod. Modified"), '\033[97m{}\033[0m'.format("Dev. Modified")])

        # format local paths to the left
        self.file_table.align['\033[97m{}\033[0m'.format("Filename")] = "l"

    # returns table, for printing
    def get_file_table(self):
        return self.file_table

    # undoes coloring, may or may not be required (safer)
    def escape_ansi(self, str_in):
        ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', str_in)

    # color the directories before the file based on their matching
    def color_prefix(self, prefix, prod=False):
        # color matching, green; else yellow
        if prod:
            directories = prefix.split('/')
            new_prefix = ""
            for i, directory in enumerate(directories):
                if i < len(directories) - 1:
                    #                                      removes color for the comparison
                    if not os.path.exists(self.dev_site + '/' + self.escape_ansi(new_prefix) + directory):
                        new_prefix = new_prefix + '\033[93m{}\033[0m'.format(directory + '/')
                    else:
                        new_prefix = new_prefix + '\033[92m{}\033[0m'.format(directory + '/')

        # color matching, green; else blue
        else:
            directories = prefix.split('/')
            new_prefix = ""
            for i, directory in enumerate(directories):
                if i < len(directories) - 1:
                    #                                       removes color for the comparison
                    if not os.path.exists(self.prod_site + '/' + self.escape_ansi(new_prefix) + directory):
                        new_prefix = new_prefix + '\033[94m{}\033[0m'.format(directory + '/')
                    else:
                        new_prefix = new_prefix + '\033[92m{}\033[0m'.format(directory + '/')

        return new_prefix

    # searches directory to get subdirectories and files
    def explore_directory(self, dir_path, prefix="", site2=False):
        for entry in os.listdir(dir_path):
            full_path = os.path.join(dir_path, entry)
            # path dependent
            if not site2:
                rel_path = os.path.relpath(full_path, self.prod_site)
            else:
                rel_path = os.path.relpath(full_path, self.dev_site)

            # add prefix and entry recursively call, or process them
            if os.path.isdir(full_path):
                self.explore_directory(full_path, prefix=f"{prefix}{entry}/", site2=site2)
            else:
                self.compare_add_row(rel_path, prefix=prefix, entry=entry)

    # compares the entries to the table based on size, modification date (code, links)
    def compare_add_row(self, rel_path, prefix="", entry=""):
        # Process files only if not already processed
        full_path_key = os.path.join(prefix, entry)
        if full_path_key not in self.processed_files:
            # add to set to avoid doubles
            self.processed_files.add(full_path_key)

            # get full file path(s)
            prod = os.path.join(self.prod_site, rel_path)
            dev = os.path.join(self.dev_site, rel_path)

            # determine if file is found in production and development
            prod_stats = os.stat(prod) if os.path.exists(prod) else False
            dev_stats = os.stat(dev) if os.path.exists(dev) else False

            # Standard colors (92==green)
            match = '\033[92m'
            found = '\033[92m{}\033[0m'.format("BOTH")
            size = '\033[92m{}\033[0m'
            change = '\033[92m{}\033[0m'

            # found in both
            if prod_stats and dev_stats:
                # if size and time differ, color red(==91)
                if prod_stats and dev_stats and prod_stats.st_size != dev_stats.st_size:
                    size = '\033[91m{}\033[0m'
                if prod_stats and dev_stats and time.ctime(prod_stats.st_mtime) != time.ctime(dev_stats.st_mtime):
                    change = '\033[91m{}\033[0m'

            # found in production only (93==yellow), (97==white)
            elif prod_stats:
                match = '\033[93m'
                found = '\033[93m{}\033[0m'.format("PROD.")
                size = '\033[97m{}\033[0m'
                change = '\033[97m{}\033[0m'

            # found in development only (94==blue), (97==white)
            else:
                match = '\033[94m'
                found = '\033[94m{}\033[0m'.format("DEV.")
                size = '\033[97m{}\033[0m'
                change = '\033[97m{}\033[0m'

            # only do search if user chose to
            if self.code_check or self.link_check:
                # standard that the column is empty
                code_match = "n/a"
                links_prod = "n/a"
                links_dev = "n/a"
                # determine if a file is code, if so apply code matching
                is_code = False
                # file extensions being looked for, add more if necessary
                file_extension = ['.html', '.css', '.js', '.php', '.xml', '.ts', '.sql', '.json', '.py']
                no_trail = entry.split('@')
                for ext in file_extension:
                    if no_trail[0].lower().endswith(ext):
                        is_code = True

                # if not code: irrelevant
                if is_code:
                    if self.code_check and self.link_check:
                        # code compare
                        if found == '\033[92m{}\033[0m'.format("BOTH"):
                            path1 = self.prod_site + '/' + prefix + entry
                            path2 = self.dev_site + '/' + prefix + entry
                            cc = CodeChecker(path1, path2)
                            cc.compare_files()

                            # green true for matching code, red false otherwise
                            if cc.get_result() == "Files are identical!":
                                code_match = '\033[92m{}\033[0m'.format("TRUE")
                            else:
                                code_match = '\033[91m{}\033[0m'.format("FALSE")
                        else:
                            code_match = "N/A"

                        # link check
                        # found in both file links
                        if found == '\033[92m{}\033[0m'.format("BOTH"):
                            # production file
                            cc = CodeChecker(self.prod_site + '/' + prefix + entry)
                            links_failed = cc.check_links()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_prod = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_prod = '\033[92m{}\033[0m'.format(links_failed)

                            # development file
                            cc = CodeChecker(self.dev_site + '/' + prefix + entry)
                            links_failed = cc.check_links()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_dev = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_dev = '\033[92m{}\033[0m'.format(links_failed)

                        # production file links
                        elif found == '\033[93m{}\033[0m'.format("PROD."):
                            cc = CodeChecker(self.prod_site + '/' + prefix + entry)
                            links_failed = cc.check_links()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_prod = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_prod = '\033[92m{}\033[0m'.format(links_failed)
                            links_dev = "N/A"

                        # development file links
                        else:
                            cc = CodeChecker(self.dev_site + '/' + prefix + entry)
                            links_failed = cc.check_links()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_dev = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_dev = '\033[92m{}\033[0m'.format(links_failed)
                            links_prod = "N/A"

                    elif self.code_check:
                        # code compare
                        if found == '\033[92m{}\033[0m'.format("BOTH"):
                            path1 = self.prod_site + '/' + prefix + entry
                            path2 = self.dev_site + '/' + prefix + entry
                            cc = CodeChecker(path1, path2)
                            cc.compare_files()

                            # green true for matching code, red false otherwise
                            if cc.get_result() == "Files are identical!":
                                code_match = '\033[92m{}\033[0m'.format("TRUE")
                            else:
                                code_match = '\033[91m{}\033[0m'.format("FALSE")
                        else:
                            code_match = "N/A"

                    else:
                        # link check
                        # found in both file links
                        if found == '\033[92m{}\033[0m'.format("BOTH"):
                            # production file
                            cc = CodeChecker(self.prod_site + '/' + prefix + entry)
                            links_failed = cc.check_links()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_prod = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_prod = '\033[92m{}\033[0m'.format(links_failed)

                            # development file
                            cc = CodeChecker(self.dev_site + '/' + prefix + entry)
                            links_failed = cc.check_links()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_dev = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_dev = '\033[92m{}\033[0m'.format(links_failed)

                        # production file links
                        elif found == '\033[93m{}\033[0m'.format("PROD."):
                            cc = CodeChecker(self.prod_site + '/' + prefix + entry)
                            links_failed = cc.check_links()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_prod = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_prod = '\033[92m{}\033[0m'.format(links_failed)
                            links_dev = "N/A"

                        # development file links
                        else:
                            cc = CodeChecker(self.dev_site + '/' + prefix + entry)
                            links_failed = cc.check_links()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_dev = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_dev = '\033[92m{}\033[0m'.format(links_failed)
                            links_prod = "N/A"

                # standard empty
                else:
                    if self.code_check:
                        code_match = "N/A"
                    else:
                        links_prod = "N/A"
                        links_dev = "N/A"

                # color path before file
                if prod_stats and dev_stats:
                    prefix = '\033[92m{}\033[0m'.format(prefix)
                else:
                    prefix = self.color_prefix(prefix, prod=prod_stats)

                # add row with code and link check columns
                if self.code_check and self.link_check:
                    # add row based on above
                    self.file_table.add_row([
                        f"{prefix}{match}{entry}\033[0m",
                        found, code_match, links_prod, links_dev,
                        size.format(prod_stats.st_size) if prod_stats else "N/A",
                        size.format(dev_stats.st_size) if dev_stats else "N/A",
                        change.format(time.ctime(round(prod_stats.st_mtime))) if prod_stats else "N/A",
                        change.format(time.ctime(round(dev_stats.st_mtime))) if dev_stats else "N/A"
                    ])
                # add row with code check column
                elif self.code_check:
                    # add row based on above
                    self.file_table.add_row([
                        f"{prefix}{match}{entry}\033[0m",
                        found, code_match,
                        size.format(prod_stats.st_size) if prod_stats else "N/A",
                        size.format(dev_stats.st_size) if dev_stats else "N/A",
                        change.format(time.ctime(round(prod_stats.st_mtime))) if prod_stats else "N/A",
                        change.format(time.ctime(round(dev_stats.st_mtime))) if dev_stats else "N/A"
                    ])
                # add row with link check columns
                else:
                    # add row based on above
                    self.file_table.add_row([
                        f"{prefix}{match}{entry}\033[0m",
                        found, links_prod, links_dev,
                        size.format(prod_stats.st_size) if prod_stats else "N/A",
                        size.format(dev_stats.st_size) if dev_stats else "N/A",
                        change.format(time.ctime(round(prod_stats.st_mtime))) if prod_stats else "N/A",
                        change.format(time.ctime(round(dev_stats.st_mtime))) if dev_stats else "N/A"
                    ])

            else:
                # color path before file
                if prod_stats and dev_stats:
                    prefix = '\033[92m{}\033[0m'.format(prefix)
                else:
                    prefix = self.color_prefix(prefix, prod=prod_stats)

                # add row based on above
                self.file_table.add_row([
                    f"{prefix}{match}{entry}\033[0m",
                    found,
                    size.format(prod_stats.st_size) if prod_stats else "N/A",
                    size.format(dev_stats.st_size) if dev_stats else "N/A",
                    change.format(time.ctime(round(prod_stats.st_mtime))) if prod_stats else "N/A",
                    change.format(time.ctime(round(dev_stats.st_mtime))) if dev_stats else "N/A"
                ])

    # explores both directories to get every subdirectory and file to be compared
    def make_table(self):
        self.explore_directory(self.prod_site)
        self.explore_directory(self.dev_site, site2=True)
