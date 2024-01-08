import os
import subprocess
from FileChecker import FileChecker
from CodeChecker import CodeChecker
from LinkChecker import LinkChecker


class MainClass:

    def __init__(self):
        pass

    def runcmd(self, cmd, verbose=False):
        process = subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            text=True,
            shell=True
        )
        if verbose:
            print(process.stdout.strip(), process.stderr)

    def file_comp(self, path1, path2, cc=False, lc=False):
        # production site path
        prod_site = path1  # example: C:\Users\aidan\OneDrive\Desktop\Wget\websites\bravenlyglobal.com
        # development site path
        dev_site = path2  # example: C:\Users\aidan\OneDrive\Desktop\Wget\websites\bravenlyglobal.d-solmedia.com

        fc = FileChecker(prod_site, dev_site, code_check=cc, link_check=lc)
        fc.make_table()
        print(fc.get_file_table())

    def code_comp(self, path1, path2):
        # code 1 path
        file1 = path1  # C:/Users/aidan/OneDrive/Desktop/CodeFiles/code1.txt
        # code 2 path
        file2 = path2  # C:/Users/aidan/OneDrive/Desktop/CodeFiles/code2.txt

        cc = CodeChecker(file1, file2)
        cc.compare()
        print(cc.get_result())

    def links_check(self, path):
        file = path  # C:/Users/aidan/OneDrive/Desktop/CodeFiles/code3.html

        cc = CodeChecker(file)
        cc.check_links_print()

    def get_check_path(self):
        working = False
        safe_path = ""
        while not working:
            path = input("Enter a path: ")
            # backslashes may cause errors
            safe_path = path.replace("\\", "/")
            working = os.path.exists(safe_path)
            if not working:
                print("Invalid path")
        return safe_path

    def get_check_sub_path(self, super_path):
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


def main():
    m = MainClass()

    try:
        answer = 'x'
        while answer != 'q':
            print("\n*\t*\t*\t*\t*\t*")
            print("*\tSite Compare\t*")
            print("*\t*\t*\t*\t*\t*\n")
            answer = input("What do you want to perform:\n"
                           "(w) Wget\n"
                           "(f) File Comparison\n"
                           "(c) Code Comparison\n"
                           "(l) Link check (HTML file)\n"
                           "(q) Quit\n")

            if answer == 'w':
                url = input("Enter url of site to download: ")
                print("Enter the destination for the downloaded files below.")
                path = m.get_check_path()
                m.runcmd(f'wget --directory-prefix={path} --random-wait -r -p -e robots=off -U mozilla {url}', verbose=True)

            elif answer == 'f':
                do_wget = input("Do you need to perform (1) or (2) Wget(s) before starting (else: no): ")
                if do_wget == '1':
                    url = input("Enter url of site to download: ")
                    print("Enter the destination for the downloaded files below.")
                    path1 = m.get_check_path()
                    m.runcmd(["wget", "--random-wait", "-r", "-p", "-e", "robots=off", "-U", "mozilla",
                               f"{url}"], verbose=True, cwd=f"{path1}")
                    print("Enter path to second file set below.")
                    path2 = m.get_check_path()
                elif do_wget == '2':
                    url = input("Enter url of the first site to download: ")
                    print("Enter the destination for the downloaded files below.")
                    path1 = m.get_check_path()
                    m.runcmd(["wget", "--random-wait", "-r", "-p", "-e", "robots=off", "-U", "mozilla",
                               f"{url}"], verbose=True, cwd=f"{path1}")
                    url = input("Enter url of the second site to download: ")
                    print("Enter the destination for the downloaded files below.")
                    path2 = m.get_check_path()
                    m.runcmd(["wget", "--random-wait", "-r", "-p", "-e", "robots=off", "-U", "mozilla",
                               f"{url}"], verbose=True, cwd=f"{path2}")
                else:
                    # get/check first filepath
                    path1 = m.get_check_path()
                    # get/check second filepath
                    path2 = m.get_check_path()

                reply = input("Code check (c) or link check (l) (else: neither), performed on files: ")
                if reply == 'c':
                    m.file_comp(path1, path2, cc=True)
                elif reply == 'l':
                    m.file_comp(path1, path2, lc=True)
                else:
                    m.file_comp(path1, path2)
                ans = 'x'
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
                                if os.path.exists(path2 + '/' + test_path):
                                    m.code_comp(path1 + '/' + test_path, path2 + '/' + test_path)
                                    break
                                else:
                                    print("File is not found in BOTH, please pick another filename or category.")

                            # user wants to compare a production file against another file
                            elif inp == 'p':
                                test_path = m.get_check_sub_path(path1)
                                inp2 = 'x'
                                while inp2 != 'r':
                                    inp2 = input("Is other file in PROD. (p), DEV. (d), or elsewhere (e): ")
                                    if inp2 == 'p':
                                        test_path2 = m.get_check_sub_path(path1)
                                        m.code_comp(path1 + '/' + test_path, path1 + '/' + test_path2)
                                        break
                                    elif inp2 == 'd':
                                        test_path2 = m.get_check_sub_path(path2)
                                        m.code_comp(path1 + '/' + test_path, path2 + '/' + test_path2)
                                        break
                                    elif inp2 == 'e':
                                        e_path = m.get_check_path()
                                        m.code_comp(path1 + '/' + test_path, e_path)
                                        break
                                    elif inp2 == 'r':
                                        break
                                    else:
                                        print("Enter p, d, or e")

                            # user wants to compare a development file against another file
                            elif inp == 'd':
                                test_path = m.get_check_sub_path(path2)
                                inp2 = 'x'
                                while inp2 != 'r':
                                    inp2 = input("Is other file in PROD. (p), DEV. (d), or elsewhere (e): ")
                                    if inp2 == 'p':
                                        test_path2 = m.get_check_sub_path(path1)
                                        m.code_comp(path2 + '/' + test_path, path1 + '/' + test_path2)
                                        break
                                    elif inp2 == 'd':
                                        test_path2 = m.get_check_sub_path(path2)
                                        m.code_comp(path2 + '/' + test_path, path2 + '/' + test_path2)
                                        break
                                    elif inp2 == 'e':
                                        e_path = m.get_check_path()
                                        m.code_comp(path2 + '/' + test_path, e_path)
                                        break
                                    elif inp2 == 'r':
                                        break
                                    else:
                                        print("Enter p, d, or e")
                                break
                            elif inp == 'r':
                                break
                            else:
                                print("Enter b, p, or d")

                    # perform LinkChecker on a file found by FileChecker
                    elif ans == 'l':
                        print("\n^ Copy a filename with local path from above ^\n")
                        inp = 'x'
                        while inp != 'r':
                            inp = input("PROD. (p), or DEV. (d): ")
                            if inp == 'p':
                                test_path = m.get_check_sub_path(path1)
                                m.links_check(path1 + '/' + test_path)
                                break
                            elif inp == 'd':
                                test_path = m.get_check_sub_path(path2)
                                m.links_check(path2 + '/' + test_path)
                                break
                            elif inp == 'r':
                                break
                            else:
                                print("Enter p or d")

                    # quit application
                    elif ans == 'q':
                        answer = 'q'
                    else:
                        "Enter c, l, r, or q"

            elif answer == 'c':
                # get/check first filepath
                path1 = m.get_check_path()
                # get/check second filepath
                path2 = m.get_check_path()
                m.code_comp(path1, path2)

            elif answer == 'l':
                reply = 'x'
                while reply != 'r':
                    reply = input("Check a single link (s) or links in a file (f): ")
                    if reply == 's':
                        url = input("Paste URL here: ")
                        lc = LinkChecker()
                        lc.link_check(url)
                        status = lc.get_status()
                        print(f"The URL above is {status}")
                        break
                    elif reply == 'f':
                        path = m.get_check_path()
                        m.links_check(path)
                        break

            else:
                "Enter w, f, c, l, or q"

    except KeyboardInterrupt:
        print("\nProgram interrupted!")


if __name__ == "__main__":
    main()
