import requests

class LinkChecker:
    def __init__(self):
        self.url = ""
        self.status = -1

    def getStatus(self):
        if self.status == -1:
            return "Perform linkCheck()"
        else:
            return self.status
    def linkCheck(self, url):
        self.url = url
        try:
            response = requests.head(self.url, allow_redirects=True).status_code
            if isinstance(response, int) and 300 > response:
                self.status = f"working (code: {response})"
            elif isinstance(response, int) and 400 > response:
                self.status = f"working and redirecting (code: {response})"
            elif isinstance(response, int) and 400 == response:
                self.status = f"working, Bad Request (code: {response})"
            elif isinstance(response, int) and 404 > response:
                self.status = f"working, but denied access (code: {response})"
            else:
                self.status = f"broken (code: {response})"
        except requests.RequestException as e:
            print(str(e))