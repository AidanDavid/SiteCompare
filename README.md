# SiteCompare
Site comparing application for D-SOLMEDIA
Code developed in Python (v.3.10)

Before running the application, you may need to download Wget to your computer.
 - Wget is used to crawl websites and download the necessary files. 
 - If you already have the files downloaded locally, there is no need for Wget.
 - In the "runcmd" function of 'main.py', replace the path to wget.exe with your own.

Python libraries you may have to install include:
- prettytable
- difflib

This program was developed to help web developers compare websites in two distinct states.
It allows users to download websites, compare directories, files and test links.

main (class)
- takes user inputs to be performed upon
- user can perform Wget to download website files
  - When asked to input a path, Wget will create a folder with the name of the site at the end of that path
  - Doing a Wget will overwrite a folder of the same name, use a different path if this is to be avoided
- user can perform file comparison (FileChecker) on their directories (Wget or not)
- user can perform code comparison (CodeChecker) on their files
- user can perform link testing (LinkChecker) on files or urls

FileChecker (class)
- searches through directories/folders to find files and compare them
- compared upon: where they are found, how large they are, and when they were last modified
- optionally compared upon; code similarity (CodeChecker), and/or link success (LinkChecker)

CodeChecker (class)
- allows for readable files to be compared
- will highlight additions from the second file in green
- will highlight deletions from the first file in red
- allows for finding links, before testing (LinkChecker)

LinkChecker (class)
- makes a url request and returns the status/code



General How-to
- Hopefully you find the program straight-forward throughout, but some below details maybe unclear:

- performing a Wget takes time based on website size (could be minutes to hours per site), if you already have the files downloaded, you can skip this

- oftentimes, you can input 'r' to return a step if you entered the wrong option
  - if asked to enter a path or url, this option is not available (enter a valid response to continue)

- when performing file comparisons:
  - the addition of code comparison may add several minutes before the table is generated
  - the addition of link checking may add hours before the table is generated
  - when performing a subsequent code or link check, copy the whole local path found in the leftmost column