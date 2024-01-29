"""
File: FTPFileChecker.py
Author: Aidan David
Date: 2024-01-23
Description: Compares directories/folders and files (from FTP) based on organization, size, and modification date.
Can be further compared using CodeChecker (and LinkChecker)
"""
import re
import time
from io import BytesIO
from CodeChecker import CodeChecker
from prettytable import PrettyTable


class FTPFileChecker:
    def __init__(self, prod_ftp, dev_ftp, prod_path, dev_path, code_check=False, link_check=False):
        # sites to be compared
        self.prod_site = prod_ftp
        self.dev_site = dev_ftp
        # paths to be compared
        self.prod_path = prod_path
        self.dev_path = dev_path
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

    # check if item on ftp is a directory
    def is_dir(self, ftp_instance, path):
        # remember current directory
        original_cwd = ftp_instance.pwd()
        # change directory to item_name
        try:
            ftp_instance.cwd(path)
            # go back
            ftp_instance.cwd(original_cwd)
            return True
        # change failed, not a directory
        except Exception as e:
            return False

    def file_exists(self, ftp, file_path):
        try:
            ftp.size(file_path)
            return True
        except Exception as e:
            return False
        
    def read_file_from_ftp(self, ftp_instance, path, encoding='utf-8'):
        contents = BytesIO()
        ftp_instance.retrbinary(f"RETR {path}", contents.write)
        return contents.getvalue().decode(encoding)

    # color the directories before the file based on their matching
    def color_prefix(self, prefix, prod=False):
        # color matching, green; else yellow
        if prod:
            directories = prefix.split('/')
            new_prefix = ""
            for i, directory in enumerate(directories):
                if i < len(directories) - 1:
                    try:
                        original_cwd = self.dev_site.pwd()
                        #                                                   removes color for the comparison
                        dir_match = self.dev_site.cwd(self.dev_path + '/' + self.escape_ansi(new_prefix) + directory)
                        self.dev_site.cwd(original_cwd)
                    except Exception as e:
                        dir_match = False
                    if not dir_match:
                        new_prefix = new_prefix + '\033[93m{}\033[0m'.format(directory + '/')
                    else:
                        new_prefix = new_prefix + '\033[92m{}\033[0m'.format(directory + '/')

        # color matching, green; else blue
        else:
            directories = prefix.split('/')
            new_prefix = ""
            for i, directory in enumerate(directories):
                if i < len(directories) - 1:
                    try:
                        original_cwd = self.prod_site.pwd()
                        #                                                   removes color for the comparison
                        dir_match = self.prod_site.cwd(self.prod_path + '/' + self.escape_ansi(new_prefix) + directory)
                        self.prod_site.cwd(original_cwd)
                    except Exception as e:
                        dir_match = False
                    if not dir_match:
                        new_prefix = new_prefix + '\033[94m{}\033[0m'.format(directory + '/')
                    else:
                        new_prefix = new_prefix + '\033[92m{}\033[0m'.format(directory + '/')

        return new_prefix

    # searches directory to get subdirectories and files
    def explore_directory(self, dir_path, prefix="", site2=False):
        if not site2:
            for entry in self.prod_site.nlst(dir_path):
                full_path = dir_path + '/' + entry

                # add prefix and entry recursively call, or process them
                if self.is_dir(self.prod_site, full_path):
                    self.explore_directory(full_path, prefix=f"{prefix}{entry}/", site2=site2)
                else:
                    # Ensure super_path ends with a slash
                    super_path = self.prod_path.rstrip('/') + '/'
                    rel_path = full_path[len(super_path):]

                    self.compare_add_row(rel_path, prefix=prefix, entry=entry)
        else:
            for entry in self.dev_site.nlst(dir_path):
                full_path = dir_path + '/' + entry

                # add prefix and entry recursively call, or process them
                if self.is_dir(self.dev_site, full_path):
                    self.explore_directory(full_path, prefix=f"{prefix}{entry}/", site2=site2)
                else:
                    # Ensure super_path ends with a slash
                    super_path = self.dev_path.rstrip('/') + '/'
                    rel_path = full_path[len(super_path):]

                    self.compare_add_row(rel_path, prefix=prefix, entry=entry)

    # compares the entries to the table based on size, modification date (code, links)
    def compare_add_row(self, rel_path, prefix="", entry=""):
        # Process files only if not already processed
        full_path_key = prefix + '/' + entry
        if full_path_key not in self.processed_files:
            # add to set to avoid doubles
            self.processed_files.add(full_path_key)

            # get path before entry
            prod = self.prod_path + rel_path
            dev = self.dev_path + rel_path

            # determine if file is found in production and development
            prod_found = True if self.file_exists(self.prod_site, prod) else False
            dev_found = True if self.file_exists(self.dev_site, dev) else False

            # Standard colors (92==green)
            match = '\033[92m'
            found = '\033[92m{}\033[0m'.format("BOTH")
            size = '\033[92m{}\033[0m'
            change = '\033[92m{}\033[0m'
            # initialize modified times
            formatted_prod = ""
            formatted_dev = ""

            # found in both
            if prod_found and dev_found:
                # if size and time differ, color red(==91)
                if prod_found and dev_found and self.prod_site.size(prod) != self.dev_site.size(dev):
                    size = '\033[91m{}\033[0m'

                # get modification time
                mod_time_prod = self.prod_site.sendcmd(f"MDTM {prod}")
                # format
                formatted_prod = time.ctime(time.mktime(time.strptime(mod_time_prod[4:], "%Y%m%d%H%M%S")))
                # get modification time
                mod_time_dev = self.dev_site.sendcmd(f"MDTM {dev}")
                # format
                formatted_dev = time.ctime(time.mktime(time.strptime(mod_time_dev[4:], "%Y%m%d%H%M%S")))
                if prod_found and dev_found and formatted_prod != formatted_dev:
                    change = '\033[91m{}\033[0m'

            # found in production only (93==yellow), (97==white)
            elif prod_found:
                match = '\033[93m'
                found = '\033[93m{}\033[0m'.format("PROD.")
                size = '\033[97m{}\033[0m'
                change = '\033[97m{}\033[0m'
                # get modification time
                mod_time_prod = self.prod_site.sendcmd(f"MDTM {prod}")
                # format
                formatted_prod = time.ctime(time.mktime(time.strptime(mod_time_prod[4:], "%Y%m%d%H%M%S")))

            # found in development only (94==blue), (97==white)
            else:
                match = '\033[94m'
                found = '\033[94m{}\033[0m'.format("DEV.")
                size = '\033[97m{}\033[0m'
                change = '\033[97m{}\033[0m'
                # get modification time
                mod_time_dev = self.dev_site.sendcmd(f"MDTM {dev}")
                # format
                formatted_dev = time.ctime(time.mktime(time.strptime(mod_time_dev[4:], "%Y%m%d%H%M%S")))

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
                            path1 = self.prod_path + '/' + prefix + entry
                            path2 = self.dev_path + '/' + prefix + entry
                            content1 = self.read_file_from_ftp(self.prod_site, path1)
                            content2 = self.read_file_from_ftp(self.dev_site, path2)
                            
                            cc = CodeChecker(str1=content1, str2=content2)
                            cc.compare_strings()

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
                            path = self.prod_path + '/' + prefix + entry
                            content = self.read_file_from_ftp(self.prod_site, path)
                            
                            cc = CodeChecker(str1=content)
                            links_failed = cc.check_links_string()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_prod = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_prod = '\033[92m{}\033[0m'.format(links_failed)

                            # development file
                            path = self.dev_path + '/' + prefix + entry
                            content = self.read_file_from_ftp(self.dev_site, path)

                            cc = CodeChecker(str1=content)
                            links_failed = cc.check_links_string()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_dev = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_dev = '\033[92m{}\033[0m'.format(links_failed)

                        # production file links
                        elif found == '\033[93m{}\033[0m'.format("PROD."):
                            path = self.prod_path + '/' + prefix + entry
                            content = self.read_file_from_ftp(self.prod_site, path)

                            cc = CodeChecker(str1=content)
                            links_failed = cc.check_links_string()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_prod = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_prod = '\033[92m{}\033[0m'.format(links_failed)
                            links_dev = "N/A"

                        # development file links
                        else:
                            path = self.dev_path + '/' + prefix + entry
                            content = self.read_file_from_ftp(self.dev_site, path)

                            cc = CodeChecker(str1=content)
                            links_failed = cc.check_links_string()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_dev = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_dev = '\033[92m{}\033[0m'.format(links_failed)
                            links_prod = "N/A"

                    elif self.code_check:
                        # code compare
                        if found == '\033[92m{}\033[0m'.format("BOTH"):
                            path1 = self.prod_path + '/' + prefix + entry
                            path2 = self.dev_path + '/' + prefix + entry
                            content1 = self.read_file_from_ftp(self.prod_site, path1)
                            content2 = self.read_file_from_ftp(self.dev_site, path2)

                            cc = CodeChecker(str1=content1, str2=content2)
                            cc.compare_strings()

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
                            path = self.prod_path + '/' + prefix + entry
                            content = self.read_file_from_ftp(self.prod_site, path)

                            cc = CodeChecker(str1=content)
                            links_failed = cc.check_links_string()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_prod = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_prod = '\033[92m{}\033[0m'.format(links_failed)

                            # development file
                            path = self.dev_path + '/' + prefix + entry
                            content = self.read_file_from_ftp(self.dev_site, path)

                            cc = CodeChecker(str1=content)
                            links_failed = cc.check_links_string()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_dev = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_dev = '\033[92m{}\033[0m'.format(links_failed)

                        # production file links
                        elif found == '\033[93m{}\033[0m'.format("PROD."):
                            path = self.prod_path + '/' + prefix + entry
                            content = self.read_file_from_ftp(self.prod_site, path)

                            cc = CodeChecker(str1=content)
                            links_failed = cc.check_links_string()

                            # green 0 for no failures, red number for failures
                            if links_failed > 0:
                                links_prod = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_prod = '\033[92m{}\033[0m'.format(links_failed)
                            links_dev = "N/A"

                        # development file links
                        else:
                            path = self.dev_path + '/' + prefix + entry
                            content = self.read_file_from_ftp(self.dev_site, path)

                            cc = CodeChecker(str1=content)
                            links_failed = cc.check_links_string()

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
                if prod_found and dev_found:
                    prefix = '\033[92m{}\033[0m'.format(prefix)
                else:
                    prefix = self.color_prefix(prefix, prod=prod_found)

                # add row with code and link check columns
                if self.code_check and self.link_check:
                    # add row based on above
                    self.file_table.add_row([
                        f"{prefix}{match}{entry}\033[0m",
                        found, code_match, links_prod, links_dev,
                        size.format(self.prod_site.size(prod)) if prod_found else "N/A",
                        size.format(self.dev_site.size(dev)) if dev_found else "N/A",
                        change.format(formatted_prod) if prod_found else "N/A",
                        change.format(formatted_dev) if dev_found else "N/A"
                    ])
                # add row with code check column
                elif self.code_check:
                    # add row based on above
                    self.file_table.add_row([
                        f"{prefix}{match}{entry}\033[0m",
                        found, code_match,
                        size.format(self.prod_site.size(prod)) if prod_found else "N/A",
                        size.format(self.dev_site.size(dev)) if dev_found else "N/A",
                        change.format(formatted_prod) if prod_found else "N/A",
                        change.format(formatted_dev) if dev_found else "N/A"
                    ])
                # add row with link check columns
                else:
                    # add row based on above
                    self.file_table.add_row([
                        f"{prefix}{match}{entry}\033[0m",
                        found, links_prod, links_dev,
                        size.format(self.prod_site.size(prod)) if prod_found else "N/A",
                        size.format(self.dev_site.size(dev)) if dev_found else "N/A",
                        change.format(formatted_prod) if prod_found else "N/A",
                        change.format(formatted_dev) if dev_found else "N/A"
                    ])

            else:
                # color path before file
                if prod_found and dev_found:
                    prefix = '\033[92m{}\033[0m'.format(prefix)
                else:
                    prefix = self.color_prefix(prefix, prod=prod_found)

                # add row based on above
                self.file_table.add_row([
                    f"{prefix}{match}{entry}\033[0m",
                    found,
                    size.format(self.prod_site.size(prod)) if prod_found else "N/A",
                    size.format(self.dev_site.size(dev)) if dev_found else "N/A",
                    change.format(formatted_prod) if prod_found else "N/A",
                    change.format(formatted_dev) if dev_found else "N/A"
                ])

    # explores both directories to get every subdirectory and file to be compared
    def make_table(self):
        self.explore_directory(self.prod_path)
        self.explore_directory(self.dev_path, site2=True)
