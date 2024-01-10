"""
File: main.py
Author: Aidan David
Date: 2024-01-10
Description: Tests an inputted link.
"""
import requests


class LinkChecker:
    def __init__(self):
        self.url = ""
        self.status = -1
        self.code = -1

    # gives the link status, or tells the
    def get_status(self):
        if self.status == -1:
            return "Perform link_check()"
        else:
            return self.status

    # gives the link status code
    def get_code(self):
        return self.code

    # actual testing of link
    def link_check(self, url):
        self.url = url
        try:
            # test link, get response
            response = requests.head(self.url, allow_redirects=True).status_code
            # response all good
            if isinstance(response, int) and 300 > response:
                self.code = response
                response = '\033[92m{}\033[0m'.format(response)
                self.status = f"working (code: {response})"
            # response good, redirects
            elif isinstance(response, int) and 400 > response:
                self.code = response
                response = '\033[92m{}\033[0m'.format(response)
                self.status = f"working and redirecting (code: {response})"
            # works, but got bad request error
            elif isinstance(response, int) and 400 == response:
                self.code = response
                response = '\033[93m{}\033[0m'.format(response)
                self.status = f"working, Bad Request (code: {response})"
            # works, but got denied (maybe you have to pay entry/subscription, or need special permissions)
            elif isinstance(response, int) and 404 > response:
                self.code = response
                response = '\033[93m{}\033[0m'.format(response)
                self.status = f"working, but denied access (code: {response})"
            # does not work
            else:
                self.code = response
                response = '\033[91m{}\033[0m'.format(response)
                self.status = f"broken (code: {response})"
        # connection error
        except requests.RequestException as e:
            self.status = "giving a connection error: " + '\033[91m{}\033[0m'.format(str(e))
            self.code = 429
