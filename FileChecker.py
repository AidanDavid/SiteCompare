import os
import time
import re
from prettytable import PrettyTable
from CodeChecker import CodeChecker

class FileChecker:
    def __init__(self, prodS, devS, code_check=False, link_check=False):
        self.prodSite = prodS
        self.devSite = devS
        # to track files, avoid double printing
        self.processed_files = set()
        self.code_check = code_check
        self.link_check = link_check
        # file sizing/info
        if code_check:
            self.fileTable = PrettyTable([
                '\033[97m{}\033[0m'.format("Filename"), '\033[97m{}\033[0m'.format("Found"),
                '\033[97m{}\033[0m'.format("Code Match"), '\033[97m{}\033[0m'.format("Prod. Size (in Bytes)"),
                '\033[97m{}\033[0m'.format("Dev. Size (in Bytes)"), '\033[97m{}\033[0m'.format("Prod. Modified"),
                '\033[97m{}\033[0m'.format("Dev. Modified")])
        elif link_check:
            self.fileTable = PrettyTable([
                '\033[97m{}\033[0m'.format("Filename"), '\033[97m{}\033[0m'.format("Found"),
                '\033[97m{}\033[0m'.format("Links Failed (PROD.)"), '\033[97m{}\033[0m'.format("Links Failed (DEV.)"),
                '\033[97m{}\033[0m'.format("Prod. Size (in Bytes)"), '\033[97m{}\033[0m'.format("Dev. Size (in Bytes)"),
                '\033[97m{}\033[0m'.format("Prod. Modified"), '\033[97m{}\033[0m'.format("Dev. Modified")])
        else:
            self.fileTable = PrettyTable([
                '\033[97m{}\033[0m'.format("Filename"), '\033[97m{}\033[0m'.format("Found"),
                '\033[97m{}\033[0m'.format("Prod. Size (in Bytes)"), '\033[97m{}\033[0m'.format("Dev. Size (in Bytes)"),
                '\033[97m{}\033[0m'.format("Prod. Modified"), '\033[97m{}\033[0m'.format("Dev. Modified")])

        self.fileTable.align['\033[97m{}\033[0m'.format("Filename")] = "l"

    def getFileTable(self):
        return self.fileTable

    def escape_ansi(self, str):
        ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        return ansi_escape.sub('', str)

    def exploreDir(self, dir_path, prefix="", site2=False):
        for entry in os.listdir(dir_path):
            full_path = os.path.join(dir_path, entry)
            # path dependent
            if not site2:
                rel_path = os.path.relpath(full_path, self.prodSite)
            else:
                rel_path = os.path.relpath(full_path, self.devSite)

            # add prefix and entry recursively call, or process them
            if os.path.isdir(full_path):
                if os.path.exists(f"{self.prodSite}/{rel_path}") and os.path.exists(f"{self.prodSite}/{rel_path}"):
                    self.exploreDir(full_path, prefix=f"{prefix}{entry}/", site2=site2)
                else:
                    self.exploreDir(full_path, prefix=f"{prefix}{entry}/", site2=site2)
            else:
                self.compAddRow(rel_path, prefix=prefix, entry=entry)

    def compAddRow(self, rel_path, prefix="", entry=""):
        # Process files only if not already processed
        full_path_key = os.path.join(prefix, entry)
        if full_path_key not in self.processed_files:
            self.processed_files.add(full_path_key)

            prod = os.path.join(self.prodSite, rel_path)
            dev = os.path.join(self.devSite, rel_path)

            prod_stats = os.stat(prod) if os.path.exists(prod) else False
            dev_stats = os.stat(dev) if os.path.exists(dev) else False

            # Standard colorations
            match = '\033[92m'
            found = '\033[92m{}\033[0m'.format("BOTH")
            size = '\033[92m{}\033[0m'
            change = '\033[92m{}\033[0m'

            # found in both
            if prod_stats and dev_stats:
                if prod_stats and dev_stats and prod_stats.st_size != dev_stats.st_size:
                    size = '\033[91m{}\033[0m'
                if prod_stats and dev_stats and time.ctime(prod_stats.st_mtime) != time.ctime(dev_stats.st_mtime):
                    change = '\033[91m{}\033[0m'

            # found in production only
            elif prod_stats:
                match = '\033[93m'
                found = '\033[93m{}\033[0m'.format("PROD.")
                size = '\033[97m{}\033[0m'
                change = '\033[97m{}\033[0m'

            # found in development only
            else:
                match = '\033[94m'
                found = '\033[94m{}\033[0m'.format("DEV.")
                size = '\033[97m{}\033[0m'
                change = '\033[97m{}\033[0m'


            #only do search if user chose to
            if self.code_check or self.link_check:
                codeMatch = "n/a"
                links_prod = "n/a"
                links_dev = "n/a"
                # determine if a file is code, if so apply code matching
                isCode = False
                # file extensions being looked for, add more if necessary
                fileExt = ['.html', '.css', '.js', '.php', '.xml', '.ts', '.sql', '.json', '.py']
                noTrail = entry.split('@')
                for ext in fileExt:
                    if noTrail[0].lower().endswith(ext):
                        isCode = True

                # if not code: irrelevant
                #   if only found in either: not comparable (irrelevant)
                #       if the file is found in both and identical: True
                #       else: false
                if isCode:
                    if self.code_check:
                        # code compare
                        if found == '\033[92m{}\033[0m'.format("BOTH"):
                            path1 = self.prodSite + '/' + prefix + entry
                            path2 = self.devSite + '/' + prefix + entry
                            cc = CodeChecker(path1, path2)
                            cc.compare()
                            if cc.getResult() == "Files are identical!":
                                codeMatch = '\033[92m{}\033[0m'.format("TRUE")
                            else:
                                codeMatch = '\033[91m{}\033[0m'.format("FALSE")
                        else:
                            codeMatch = "N/A"

                    else:
                        # link check
                        if found == '\033[92m{}\033[0m'.format("BOTH"):
                            cc = CodeChecker(self.prodSite + '/' + prefix + entry)
                            links_failed = cc.checkLinks()
                            if links_failed > 0:
                                links_prod = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_prod = '\033[92m{}\033[0m'.format(links_failed)
                            cc = CodeChecker(self.devSite + '/' + prefix + entry)
                            links_failed = cc.checkLinks()
                            if links_failed > 0:
                                links_dev = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_dev = '\033[92m{}\033[0m'.format(links_failed)

                        elif found == '\033[93m{}\033[0m'.format("PROD."):
                            cc = CodeChecker(self.prodSite + '/' + prefix + entry)
                            links_failed = cc.checkLinks()
                            if links_failed > 0:
                                links_prod = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_prod = '\033[92m{}\033[0m'.format(links_failed)
                            links_dev = "N/A"

                        else:
                            cc = CodeChecker(self.devSite + '/' + prefix + entry)
                            links_failed = cc.checkLinks()
                            if links_failed > 0:
                                links_dev = '\033[91m{}\033[0m'.format(links_failed)
                            else:
                                links_dev = '\033[92m{}\033[0m'.format(links_failed)
                            links_prod = "N/A"
                else:
                    if self.code_check:
                        codeMatch = "N/A"
                    else:
                        links_prod = "N/A"
                        links_dev = "N/A"

                # color path before file
                if os.path.exists(self.prodSite + '/' + prefix) and os.path.exists(self.devSite + '/' + prefix):
                    prefix = '\033[92m{}\033[0m'.format(prefix)
                else:
                    # color matching, green; else yellow
                    if prod_stats:
                        directories = prefix.split('/')
                        prefix = ""
                        for i, directory in enumerate(directories):
                            if i < len(directories) - 1:
                                #                                      removes color for the comparison
                                if os.path.exists(self.devSite + '/' + self.escape_ansi(prefix)):
                                    prefix = prefix + '\033[92m{}\033[0m'.format(directory + '/')
                                else:
                                    prefix = prefix + '\033[93m{}\033[0m'.format(directory + '/')
                    # color matching, green; else blue
                    else:
                        directories = prefix.split('/')
                        prefix = ""
                        for i, directory in enumerate(directories):
                            if i < len(directories) - 1:
                                #                                       removes color for the comparison
                                if os.path.exists(self.prodSite + '/' + self.escape_ansi(prefix)):
                                    prefix = prefix + '\033[92m{}\033[0m'.format(directory + '/')
                                else:
                                    prefix = prefix + '\033[94m{}\033[0m'.format(directory + '/')


                if self.code_check:
                    # add row based on above
                    self.fileTable.add_row([
                        f"{prefix}{match}{entry}\033[0m",
                        found, codeMatch,
                        size.format(prod_stats.st_size) if prod_stats else "N/A",
                        size.format(dev_stats.st_size) if dev_stats else "N/A",
                        change.format(time.ctime(round(prod_stats.st_mtime))) if prod_stats else "N/A",
                        change.format(time.ctime(round(dev_stats.st_mtime))) if dev_stats else "N/A"
                    ])
                else:
                    # add row based on above
                    self.fileTable.add_row([
                        f"{prefix}{match}{entry}\033[0m",
                        found, links_prod, links_dev,
                        size.format(prod_stats.st_size) if prod_stats else "N/A",
                        size.format(dev_stats.st_size) if dev_stats else "N/A",
                        change.format(time.ctime(round(prod_stats.st_mtime))) if prod_stats else "N/A",
                        change.format(time.ctime(round(dev_stats.st_mtime))) if dev_stats else "N/A"
                    ])

            else:
                # color path before file
                if os.path.exists(self.prodSite + '/' + prefix) and os.path.exists(self.devSite + '/' + prefix):
                    prefix = '\033[92m{}\033[0m'.format(prefix)
                else:
                    # color matching, green; else yellow
                    if prod_stats:
                        directories = prefix.split('/')
                        prefix = ""
                        for i, directory in enumerate(directories):
                            if i < len(directories) - 1:
                                #                                      removes color for the comparison
                                if os.path.exists(self.devSite + '/' + self.escape_ansi(prefix)):
                                    prefix = prefix + '\033[92m{}\033[0m'.format(directory + '/')
                                else:
                                    prefix = prefix + '\033[93m{}\033[0m'.format(directory + '/')
                    # color matching, green; else blue
                    else:
                        directories = prefix.split('/')
                        prefix = ""
                        for i, directory in enumerate(directories):
                            if i < len(directories) - 1:
                                #                                       removes color for the comparison
                                if os.path.exists(self.prodSite + '/' + self.escape_ansi(prefix)):
                                    prefix = prefix + '\033[92m{}\033[0m'.format(directory + '/')
                                else:
                                    prefix = prefix + '\033[94m{}\033[0m'.format(directory + '/')

                # add row based on above
                self.fileTable.add_row([
                    f"{prefix}{match}{entry}\033[0m",
                    found,
                    size.format(prod_stats.st_size) if prod_stats else "N/A",
                    size.format(dev_stats.st_size) if dev_stats else "N/A",
                    change.format(time.ctime(round(prod_stats.st_mtime))) if prod_stats else "N/A",
                    change.format(time.ctime(round(dev_stats.st_mtime))) if dev_stats else "N/A"
                ])

    def makeTable(self):
        self.exploreDir(self.prodSite)
        self.exploreDir(self.devSite, site2=True)
