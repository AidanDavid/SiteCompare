import os
import time
from prettytable import PrettyTable

class FileChecker:
    def __init__(self, prodS, devS):
        self.prodSite = prodS
        self.devSite = devS
        # file sizing/info
        self.fileTable = PrettyTable([
            '\033[97m{}\033[0m'.format("Filename"), '\033[97m{}\033[0m'.format("Found"),
            '\033[97m{}\033[0m'.format("Prod. Size (in Bytes)"), '\033[97m{}\033[0m'.format("Dev. Size (in Bytes)"),
            '\033[97m{}\033[0m'.format("Prod. Modified"), '\033[97m{}\033[0m'.format("Dev. Modified")])
        self.fileTable.align['\033[97m{}\033[0m'.format("Filename")] = "l"

    def explore_directory(self, dir_path, prefix="", site2=False,dirMatch=False):
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
                    self.explore_directory(full_path, prefix=f"{prefix}{entry}/", site2=site2, dirMatch=True)
                else:
                    self.explore_directory(full_path, prefix=f"{prefix}{entry}/", site2=site2)
            else:
                if dirMatch:
                    self.compAddRow(rel_path, prefix=prefix, entry=entry, dirMatch=True)
                else:
                    self.compAddRow(rel_path, prefix=prefix, entry=entry)

    def compAddRow(self, rel_path, prefix="", entry="", dirMatch=False):
        prod = os.path.join(self.prodSite, rel_path)
        dev = os.path.join(self.devSite, rel_path)

        prod_stats = os.stat(prod) if os.path.exists(prod) else False
        dev_stats = os.stat(dev) if os.path.exists(dev) else False

        #standard colorations
        if dirMatch:
            prefix = '\033[92m{}\033[0m'.format(prefix)
        match = '\033[92m'
        found = '\033[92m{}\033[0m'.format("BOTH")
        size = '\033[92m{}\033[0m'
        change = '\033[92m{}\033[0m'

        # found in both
        if prod_stats and dev_stats:
            if prod_stats and dev_stats and prod_stats.st_size != dev_stats.st_size:
                size = '\033[91m{}\033[0m'
            if prod_stats and dev_stats and prod_stats.st_ctime != dev_stats.st_ctime:
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

        # add row based on above
        self.fileTable.add_row([
            f"{prefix}{match}{entry}\033[0m",
            found,
            size.format(prod_stats.st_size) if prod_stats else "N/A",
            size.format(dev_stats.st_size) if dev_stats else "N/A",
            change.format(time.ctime(prod_stats.st_mtime)) if prod_stats else "N/A",
            change.format(time.ctime(dev_stats.st_mtime)) if dev_stats else "N/A"
        ])

    def makeTable(self):
        self.explore_directory(self.prodSite)
        self.explore_directory(self.devSite, site2=True)
