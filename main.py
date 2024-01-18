"""
File: main.py
Author: Aidan David
Date: 2024-01-10
Description: Main event loop. Made to facilitate web development with FileChecker, CodeChecker, and LinkChecker classes.
Allows users to web crawl, file compare, code compare, and check links.
"""
import os
import subprocess
from urllib.parse import urlsplit
from FileChecker import FileChecker
from CodeChecker import CodeChecker
from LinkChecker import LinkChecker


class MainClass:

    def __init__(self):
        pass

    # runs shell commands (Wget)
    def runcmd(self, cmd, verbose=False):
        print("Running Wget...")
        try:
            process = subprocess.run(
                # replace "wget" with your wget.exe path if you are getting error finding wget
                ["wget",
                 "--no-check-certificate", "--random-wait", "-r", "-p", "-e", "robots=off", "-U", "mozilla"] + cmd,
                capture_output=True,
                check=True,
                text=True
            )
            if verbose:
                print(process.stdout.strip(), process.stderr)
            return "Wget complete!"
        except subprocess.CalledProcessError as e:
            if e.returncode == 8:
                return f"Wget completed, but got an error response ({e.returncode}) from the server! " \
                       f"Check the path for success."
            return f"Command triggered an error, exit code: {e.returncode}. Make sure URL is valid!"

    # make use of FileChecker class
    def file_comp(self, path1, path2, cc=False, lc=False):
        print("Loading...")
        # production site path
        prod_site = path1
        # development site path
        dev_site = path2

        fc = FileChecker(prod_site, dev_site, code_check=cc, link_check=lc)
        fc.make_table()
        return fc.get_file_table()

    # make use of CodeChecker class
    def code_comp(self, path1, path2):
        print("Loading...")
        # code 1 path
        file1 = path1
        # code 2 path
        file2 = path2

        cc = CodeChecker(file1, file2)
        cc.compare()
        return cc.get_result()

    # make use of CodeChecker class' link checking
    def links_check(self, path):
        cc = CodeChecker(path)
        return cc.check_links_print()

    # checks a full path, if make == True: path is created, otherwise: must be validated
    def get_check_path(self, make=False):
        # download location should be made if not found
        if make:
            path = input("Enter a path, will be made if does not already exist: ")
            # backslashes may cause errors
            safe_path = path.replace("\\", "/")
            # if not found, make it
            if not os.path.exists(safe_path):
                os.makedirs(safe_path)
        # user input must be an existing path
        else:
            # tracks success of user inputs
            working = False
            safe_path = ""
            while not working:
                path = input("Enter a path: ")
                # backslashes may cause errors
                safe_path = path.replace("\\", "/")
                working = os.path.exists(safe_path)
                if not working:
                    print("Invalid path")
        # returns path without backslashes and validated
        return safe_path


    # checks local path validity based on its super
    def get_check_sub_path(self, super_path):
        # tracks success of user inputs
        working = False
        safe_path = super_path
        while not working:
            path = input("Enter path: ")
            # backslashes may cause errors
            safe_path = path.replace("\\", "/")
            working = os.path.exists(super_path + '/' + safe_path)
            if not working:
                print("Invalid path")
        return safe_path

    # checks a full path, if make == True: path is created, otherwise: must be validated
    def check_path(self, path, make=False):
        # download location should be made if not found
        if make:
            # backslashes may cause errors
            safe_path = path.replace("\\", "/")
            # if not found, make it
            if not os.path.exists(safe_path):
                os.makedirs(safe_path)
        # user input must be an existing path
        else:
            # tracks success of user inputs
            working = False
            safe_path = ""
            if not os.path.exists(safe_path):
                print("Invalid path")
        # returns path without backslashes and validated
        return safe_path

    # Wget adds a file of domain name, this allows for path to add that
    def get_domain_name(self, url):
        # break down the URL into components
        url_bits = urlsplit(url)

        # get netloc component, which includes the domain name
        domain_name = url_bits.netloc

        return domain_name


def main():
    m = MainClass()

    try:
        # tracks main menu user inputs
        answer = 'x'
        while answer != 'q':
            # print main menu
            print("\n*\t*\t*\t*\t*\t*")
            print("*\tSite Compare\t*")
            print("*\t*\t*\t*\t*\t*\n")
            # get user request
            answer = input("What do you want to perform:\n"
                           "(w) Wget\n"
                           "(f) File Comparison\n"
                           "(c) Code Comparison\n"
                           "(l) Link check (HTML file)\n"
                           "(q) Quit\n")

            # user wants to perform a Wget
            if answer == 'w':
                url = input("Enter url of site to download: ")
                print("Enter the destination for the downloaded files below.")
                path = m.get_check_path(make=True)
                print(m.runcmd([f"--directory-prefix={path}", f"{url}"], verbose=True))

            # user wants to perform a file comparison
            elif answer == 'f':
                # determine if user wants to Wget the files to be compared
                do_wget = input("Do you need to perform (1) or (2) Wget(s) before starting (else: no): ")

                # user wants to perform 1 Wget
                if do_wget == '1':
                    # perform Wget for first file set
                    url = input("Enter url of site to download: ")
                    print("Enter the destination for the downloaded files below.")
                    path1 = m.get_check_path(make=True)
                    print(m.runcmd([f"--directory-prefix={path1}", f"{url}"], verbose=True))
                    # add domain name to path (like Wget)
                    path1 = path1 + '/' + m.get_domain_name(url)

                    # get second file set locally
                    print("Enter path to second file set below.")
                    path2 = m.get_check_path()

                    # determine which site is production or development for consistency when making the table
                    which_prod = input("Is the first site production? yes (y), no (else): ")
                    # first was production, stays the same
                    if which_prod == 'y':
                        pass
                    # second was production, so swap
                    else:
                        temp = path1
                        path1 = path2
                        path2 = temp

                # user wants to perform 2 Wgets
                elif do_wget == '2':
                    # perform Wget for first file set
                    url = input("Enter url of the first site to download: ")
                    print("Enter the destination for the downloaded files below.")
                    path1 = m.get_check_path(make=True)
                    print(m.runcmd([f"--directory-prefix={path1}", f"{url}"], verbose=True))
                    # add domain name to path (like Wget)
                    path1 = path1 + '/' + m.get_domain_name(url)

                    # perform Wget for second file set
                    url = input("Enter url of the second site to download: ")
                    print("Enter the destination for the downloaded files below.")
                    path2 = m.get_check_path(make=True)
                    print(m.runcmd([f"--directory-prefix={path2}", f"{url}"], verbose=True))
                    # add domain name to path (like Wget)
                    path2 = path2 + '/' + m.get_domain_name(url)

                    # determine which site is production or development for consistency when making the table
                    which_prod = input("Is the first site production? yes (y), no (else): ")
                    # first was production, stays the same
                    if which_prod == 'y':
                        pass
                    # second was production, so swap
                    else:
                        temp = path1
                        path1 = path2
                        path2 = temp

                else:
                    # get/check first filepath (Production)
                    print("Production site")
                    path1 = m.get_check_path()
                    # get/check second filepath (Development)
                    print("Development site")
                    path2 = m.get_check_path()

                # determine if user wants to code compare or link check the files as well (added to table)
                reply = input("Code check (c) or link check (l) (else: neither), performed on files: ")
                if reply == 'c':
                    print(m.file_comp(path1, path2, cc=True))
                elif reply == 'l':
                    print(m.file_comp(path1, path2, lc=True))
                else:
                    print(m.file_comp(path1, path2))
                ans = 'x'

                # post table creation: do users want to perform anything based on the table contents
                while ans != 'q' and ans != 'r':
                    ans = input("\n\nWhat do you want to perform based on the table generated:\n"
                                "(c) Code Comparison\n"
                                "(l) Link check (HTML file)\n"
                                "(r) Return to Main Menu\n"
                                "(q) Quit\n")

                    # perform code compare based on files found by FileChecker
                    if ans == 'c':
                        print("\n^ Copy filename(s) with local path from above ^\n")
                        inp = 'x'
                        while inp != 'r':
                            inp = input("Is file in BOTH (b), PROD. (p), or DEV. (d): ")

                            # user wants to compare two files found in both sites
                            if inp == 'b':
                                test_path = m.get_check_sub_path(path1)
                                # check that the file is in both paths
                                if os.path.exists(path2 + '/' + test_path):
                                    print(m.code_comp(path1 + '/' + test_path, path2 + '/' + test_path))
                                    break
                                else:
                                    print("File is not found in BOTH, please pick another filename or category.")

                            # user wants to compare a production file against another file
                            elif inp == 'p':
                                test_path = m.get_check_sub_path(path1)
                                inp2 = 'x'
                                while inp2 != 'r':
                                    # user can compare a production file to file from table or elsewhere locally
                                    inp2 = input("Is other file in PROD. (p), DEV. (d), or elsewhere (e): ")
                                    # another production file
                                    if inp2 == 'p':
                                        test_path2 = m.get_check_sub_path(path1)
                                        print(m.code_comp(path1 + '/' + test_path, path1 + '/' + test_path2))
                                        break

                                    # another development file
                                    elif inp2 == 'd':
                                        test_path2 = m.get_check_sub_path(path2)
                                        print(m.code_comp(path1 + '/' + test_path, path2 + '/' + test_path2))
                                        break

                                    # elsewhere locally, needs a full path
                                    elif inp2 == 'e':
                                        e_path = m.get_check_path()
                                        print(m.code_comp(path1 + '/' + test_path, e_path))
                                        break

                                    # return
                                    elif inp2 == 'r':
                                        break
                                    # invalid input
                                    else:
                                        print("Please enter p, d, or e")

                            # user wants to compare a development file against another file
                            elif inp == 'd':
                                test_path = m.get_check_sub_path(path2)
                                inp2 = 'x'
                                while inp2 != 'r':
                                    # user can compare a development file to file from table or elsewhere locally
                                    inp2 = input("Is other file in PROD. (p), DEV. (d), or elsewhere (e): ")
                                    # another production file
                                    if inp2 == 'p':
                                        test_path2 = m.get_check_sub_path(path1)
                                        print(m.code_comp(path2 + '/' + test_path, path1 + '/' + test_path2))
                                        break

                                    # another development file
                                    elif inp2 == 'd':
                                        test_path2 = m.get_check_sub_path(path2)
                                        print(m.code_comp(path2 + '/' + test_path, path2 + '/' + test_path2))
                                        break

                                    # elsewhere locally, needs full path
                                    elif inp2 == 'e':
                                        e_path = m.get_check_path()
                                        print(m.code_comp(path2 + '/' + test_path, e_path))
                                        break

                                    # return
                                    elif inp2 == 'r':
                                        break
                                    # invalid input
                                    else:
                                        print("Please enter p, d, or e")
                                break
                            elif inp == 'r':
                                break
                            else:
                                print("Please enter b, p, or d")

                    # perform LinkChecker on a file found by FileChecker
                    elif ans == 'l':
                        print("\n^ Copy a filename with local path from above ^\n")
                        inp = 'x'
                        while inp != 'r':
                            inp = input("PROD. (p), or DEV. (d): ")
                            # link check on a production file
                            if inp == 'p':
                                test_path = m.get_check_sub_path(path1)
                                print(m.links_check(path1 + '/' + test_path))
                                break

                            # link check on a development file
                            elif inp == 'd':
                                test_path = m.get_check_sub_path(path2)
                                print(m.links_check(path2 + '/' + test_path))
                                break

                            # return
                            elif inp == 'r':
                                break
                            # invalid input
                            else:
                                print("Please enter p or d")

                    # quit application
                    elif ans == 'q':
                        answer = 'q'
                    else:
                        "Please enter c, l, r, or q"

            # user wants to perform a code comparison
            elif answer == 'c':
                # get/check first filepath
                path1 = m.get_check_path()
                # get/check second filepath
                path2 = m.get_check_path()
                print(m.code_comp(path1, path2))

            # user wants to perform a link test
            elif answer == 'l':
                reply = 'x'
                while reply != 'r':
                    reply = input("Check a single link (s) or links in a file (f): ")
                    # user wants to test one link
                    if reply == 's':
                        url = input("Paste URL here: ")
                        lc = LinkChecker()
                        lc.link_check(url)
                        status = lc.get_status()
                        print(f"The URL above is {status}")
                        break
                    # user wants to test all the links in a file
                    elif reply == 'f':
                        path = m.get_check_path()
                        print(m.links_check(path))
                        break

            # user input was invalid
            else:
                "Please enter w, f, c, l, or q"

    # program was halted, not quit (q)
    except KeyboardInterrupt:
        print("\nProgram interrupted!")


# ensures one main instance
if __name__ == "__main__":
    main()
