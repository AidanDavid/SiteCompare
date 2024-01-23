# SiteCompare
Site comparing application for D-SOL Media
Code developed in Python (v.3.10)

Before running the application, you may need to download Wget to your computer.
 - Wget is used to crawl websites and download the necessary files. 
 - If you already have the files downloaded locally, there is no need for Wget.

  If you have never used Wget before:
   - On Linux, you may already have Wget preinstalled.
   - On MacOS, install Wget using Homebrew.
   - On Windows, download Wget (https://eternallybored.org/misc/wget/). 
     - Once it’s downloaded, make sure it’s added to the PATH variable.
   https://www.scrapingbee.com/blog/python-wget/ may be useful for details or assistance.

Python libraries you may have to install include:
- flask
- requests
- prettytable
You can use requirements.txt to do this. Paste the following in your console:
pip install -r requirements.txt

This program was developed to help web developers compare websites in two distinct states.
It allows users to download websites, download FTP files, compare directories, files and test links.

app (class)
- web interface for the below classes
- makes use of main to perform functionality
- makes use of html files in 'templates' for display

main (class)
- takes user inputs to be performed upon
- user can perform Wget to download website files
  - When asked to input a path, Wget will create a folder with the name of the site at the end of that path
  - Doing a Wget will overwrite a folder of the same name, use a different path if this is to be avoided
- user can perform file comparison (FileChecker) on their directories (Wget or not)
- user can perform code comparison (CodeChecker) on their files
- user can perform link testing (LinkChecker) on files or urls
- user can perform FTP downloads (FTPDownloader)

FileChecker (class)
- searches through directories/folders to find files and compare them
- compared upon: where they are found, how large they are, and when they were last modified
- optionally compared upon; code similarity (CodeChecker), and/or link success (LinkChecker)

CodeChecker (class)
- allows for readable files to be compared
- will highlight additions from the second file in green
- will highlight deletions from the first file in red
- allows for finding links, before testing (LinkChecker)
  - may run into formatting issues when comparing files with a lot of lines, and or very long lines

LinkChecker (class)
- makes a url request and returns the status/code

FTPDownloader (class)
- downloads files from FTP server, maintaining structure



General How-to
- Hopefully you find the program straight-forward throughout, but some below details maybe unclear:

- when asked to provide a URL, paste something such as: https://website.com/
- when asked to provide a path, paste something such as: C:\Users\username\Desktop\website\CodeFiles\codefile.html
  - after a file comparison, subsequent code and link check paths only need to be local to the website files, such as: CodeFiles\codefile.html
  - (this would be found in the leftmost column of the file comparing table)

- performing a Wget takes time based on website size (could be minutes to hours per site), if you already have the files downloaded, you can skip this

- when performing file comparisons:
  - the addition of code comparison may add several minutes before the table is generated
  - the addition of link checking may add hours before the table is generated
  - when performing a subsequent code or link check, copy the whole local path found in the leftmost column
  - on line 156, there is a list of file endings that are looked for as code:
    - if certain code files are not being recognized, you may have to add the file ending to the list (ex. .cpp)

- at current, FTP functionality has undergone limited testing
