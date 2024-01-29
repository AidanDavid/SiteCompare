"""
File: main.py
Author: Aidan David
Date: 2024-01-29
Description: Makes use of other program classes to add functionality used by app.py for the web interface.
"""
import os
import subprocess
from ftplib import FTP
from io import BytesIO
from urllib.parse import urlparse
from urllib.parse import urlsplit
from FileChecker import FileChecker
from CodeChecker import CodeChecker
from LinkChecker import LinkChecker
from FTPDownloader import FTPDownloader
from FTPFileChecker import FTPFileChecker


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

        fc = FileChecker(path1, path2, code_check=cc, link_check=lc)
        fc.make_table()
        return fc.get_file_table()

    def file_comp_ftp(self, ftp1, ftp2, path1, path2, cc=False, lc=False):
        print("Loading...")

        fc = FTPFileChecker(ftp1, ftp2, path1, path2, code_check=cc, link_check=lc)
        fc.make_table()
        return fc.get_file_table()

    # make use of CodeChecker class (local file)
    def code_comp_files(self, file1, file2):
        print("Loading...")

        cc = CodeChecker(path1=file1, path2=file2)
        cc.compare_files()
        return cc.get_result()

    # make use of CodeChecker class (str)
    def code_comp_strings(self, content1, content2):
        print("Loading...")

        cc = CodeChecker(str1=content1, str2=content2)
        cc.compare_strings()
        return cc.get_result()

    # make use of CodeChecker class' link checking (local file)
    def links_check_file(self, path):
        cc = CodeChecker(path1=path)
        return cc.check_links_print_file()

    # make use of CodeChecker class' link checking (str)
    def links_check_string(self, content):
        cc = CodeChecker(str1=content)
        return cc.check_links_print_string()

    # uses LinkChecker to test a URL
    def link_check(self, url):
        lc = LinkChecker()
        lc.link_check(url)
        return lc.get_status()

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
            # backslashes may cause errors
            safe_path = path.replace("\\", "/")
            if not os.path.exists(safe_path):
                return "Invalid path"
        # returns path without backslashes and validated
        return safe_path

    # Wget adds a file of domain name, this allows for path to add that
    def get_domain_name(self, url):
        # break down the URL into components
        url_bits = urlsplit(url)

        # get netloc component, which includes the domain name
        domain_name = url_bits.netloc

        return domain_name

    # get FTP info
    def parse_ftp_url(self, ftp_url):
        parsed_url = urlparse(ftp_url)
        if parsed_url.scheme != 'ftp':
            return 'Invalid FTP URL. Scheme must be "ftp".'

        hostname = parsed_url.hostname
        port = int(parsed_url.port) or 21  # default 21
        username = parsed_url.username
        password = parsed_url.password
        path = parsed_url.path.lstrip('/')  # remove leading slash from path

        return hostname, port, username, password, path

    # test an FTP, connect, login and path
    def test_ftp(self, hostname, port, username, password, path, is_file=False):
        ftp_instance = FTP()  # Create an instance of the FTP class
        try:
            ftp_instance.connect(hostname, port)
            try:
                ftp_instance.login(username, password)
                if not is_file:
                    try:
                        ftp_instance.cwd(path)
                        return ftp_instance
                    except Exception as e:
                        # path failed
                        return 0
                else:
                    try:
                        dummy_file = BytesIO()
                        # try to retrieve the file content
                        ftp_instance.retrbinary(f"RETR {path}", dummy_file.write)
                        return ftp_instance
                    except Exception as e:
                        # path failed
                        return 0

            except Exception as e:
                # access failed
                return -1
        except Exception as e:
            # connection failed
            return -2

    # download FTP to local
    def download_ftp(self, ftp_instance, path, dest):
        fd = FTPDownloader()
        fd.download(ftp_instance, path, dest)

    #
    def read_file_from_ftp(self, ftp_instance, path, encoding='utf-8'):
        contents = BytesIO()
        ftp_instance.retrbinary(f"RETR {path}", contents.write)
        return contents.getvalue().decode(encoding)
