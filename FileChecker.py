import os
import time
from prettytable import PrettyTable
from CodeChecker import CodeChecker

class FileChecker:
    def __init__(self, prodS, devS):
        self.prodSite = prodS
        self.devSite = devS
        # to track files, avoid double printing
        self.processed_files = set()
        # file sizing/info
        self.fileTable = PrettyTable([
            '\033[97m{}\033[0m'.format("Filename"), '\033[97m{}\033[0m'.format("Found"),
            '\033[97m{}\033[0m'.format("Code Match"), '\033[97m{}\033[0m'.format("Links Failed (PROD.)"),
            '\033[97m{}\033[0m'.format("Links Failed (DEV.)"), '\033[97m{}\033[0m'.format("Prod. Size (in Bytes)"),
            '\033[97m{}\033[0m'.format("Dev. Size (in Bytes)"), '\033[97m{}\033[0m'.format("Prod. Modified"),
            '\033[97m{}\033[0m'.format("Dev. Modified")])
        self.fileTable.align['\033[97m{}\033[0m'.format("Filename")] = "l"

    def getFileTable(self):
        return self.fileTable

    def exploreDir(self, dir_path, prefix="", site2=False, dirMatch=False):
        for entry in os.listdir(dir_path):
            full_path = os.path.join(dir_path, entry)
            print(full_path)
            # path dependent
            if not site2:
                rel_path = os.path.relpath(full_path, self.prodSite)
            else:
                rel_path = os.path.relpath(full_path, self.devSite)

            # add prefix and entry recursively call, or process them
            if os.path.isdir(full_path):
                if os.path.exists(f"{self.prodSite}/{rel_path}") and os.path.exists(f"{self.prodSite}/{rel_path}"):
                    self.exploreDir(full_path, prefix=f"{prefix}{entry}/", site2=site2, dirMatch=True)
                else:
                    self.exploreDir(full_path, prefix=f"{prefix}{entry}/", site2=site2)
            else:
                if dirMatch:
                    self.compAddRow(rel_path, prefix=prefix, entry=entry, dirMatch=True)
                else:
                    self.compAddRow(rel_path, prefix=prefix, entry=entry)

    def compAddRow(self, rel_path, prefix="", entry="", dirMatch=False):
        # Process files only if not already processed
        if f"{prefix}{entry}" not in self.processed_files:
            self.processed_files.add(f"{prefix}{entry}")

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
                codeMatch = "N/A"
                links_prod = "N/A"
                links_dev = "N/A"

            if dirMatch:
                prefix = '\033[92m{}\033[0m'.format(prefix)

            # add row based on above
            self.fileTable.add_row([
                f"{prefix}{match}{entry}\033[0m",
                found, codeMatch, links_prod, links_dev,
                size.format(prod_stats.st_size) if prod_stats else "N/A",
                size.format(dev_stats.st_size) if dev_stats else "N/A",
                change.format(time.ctime(round(prod_stats.st_mtime))) if prod_stats else "N/A",
                change.format(time.ctime(round(dev_stats.st_mtime))) if dev_stats else "N/A"
            ])

    def makeTable(self):
        self.exploreDir(self.prodSite)
        self.exploreDir(self.devSite, site2=True)
