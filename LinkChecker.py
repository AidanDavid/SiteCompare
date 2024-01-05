import requests

class LinkChecker:
    def __init__(self):
        self.url = ""
        self.status = -1
        self.code = -1

    def getStatus(self):
        if self.status == -1:
            return "Perform linkCheck()"
        else:
            return self.status

    def getCode(self):
        return self.code

    def linkCheck(self, url):
        self.url = url
        try:
            response = requests.head(self.url, allow_redirects=True).status_code
            if isinstance(response, int) and 300 > response:
                self.code = response
                response = '\033[92m{}\033[0m'.format(response)
                self.status = f"working (code: {response})"
            elif isinstance(response, int) and 400 > response:
                self.code = response
                response = '\033[92m{}\033[0m'.format(response)
                self.status = f"working and redirecting (code: {response})"
            elif isinstance(response, int) and 400 == response:
                self.code = response
                response = '\033[93m{}\033[0m'.format(response)
                self.status = f"working, Bad Request (code: {response})"
            elif isinstance(response, int) and 404 > response:
                self.code = response
                response = '\033[93m{}\033[0m'.format(response)
                self.status = f"working, but denied access (code: {response})"
            else:
                self.code = response
                response = '\033[91m{}\033[0m'.format(response)
                self.status = f"broken (code: {response})"
        except requests.RequestException as e:
            self.status = "giving a connection error: " + '\033[91m{}\033[0m'.format(str(e))
            self.code = 429