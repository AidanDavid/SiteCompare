"""
File: app.py
Author: Aidan David
Date: 2024-01-23
Description: Web interface for Site Compare. Made to facilitate web development with FileChecker, CodeChecker,
and LinkChecker classes. Allows users to web crawl, access ftp, file compare, code compare, and check links.
"""
from flask import Flask, render_template, request
import re
import os
from main import MainClass

app = Flask(__name__)

m = MainClass()


def apply_html_colors(content):
    # ANSI color to HTML color
    ansi_to_html_color = {
        '91': 'red',
        '92': 'lightgreen',
        '93': 'yellow',
        '94': 'blue',
        '97': 'white'
    }

    # find ANSI color codes
    ansi_code_pattern = re.compile(r'\033\[(\d+)m')

    # replace ANSI with HTML color
    def replace_ansi(match):
        ansi_code = match.group(1)
        html_color = ansi_to_html_color.get(ansi_code, 'darkgrey')  # default darkgrey
        return f'<span style="color: {html_color};">'

    # apply
    content = ansi_code_pattern.sub(replace_ansi, content)

    # remove ANSI codes
    content = content.replace('\033[0m', '</span>')

    return content


# index/main page
@app.route('/')
def index():
    return render_template('index.html')


# Wget download page
@app.route('/wget', methods=['POST'])
def wget():
    url = request.form['url']
    path = request.form['path']
    # ensure path is valid or made
    valid_path = m.check_path(path, make=True)

    # get and display result
    response = m.runcmd(["--directory-prefix=" + valid_path, url], verbose=True)
    return render_template('wget.html', result=response)


# ftp download page
@app.route('/ftp', methods=['POST'])
def ftp():
    host_url = request.form['host']
    username = request.form['user']
    password = request.form['pass']
    path = request.form['path']
    dest = request.form['dest']
    # ensure dest path is valid or made
    valid_dest = m.check_path(dest, make=True)

    # parse the host url given
    result = m.parse_ftp_url(host_url)

    # if the username is in the url
    if result[2] is not None:
        username = result[2]

    # if the password is in the url
    if result[3] is not None:
        password = result[3]

    # if the path is in the url
    if result[4] is not None and len(result[4]) != 0:
        path = result[4]

    # check ftp access status, result[0] == hostname, result[1] == port
    status = m.test_ftp(result[0], result[1], username, password, path)

    # it worked
    if type(status) != int:
        m.download_ftp(status, path, valid_dest)
        res = "FTP download successful!"
        status.quit()
    # got in but the path does not exist
    elif status == 0:
        res = "Path does not exist!"
    # did not get into FTP server
    else:
        res = "Access to FTP failed!"
    return render_template('ftp.html', result=res)


# file comparison page
@app.route('/file_comp', methods=['POST'])
def file_comp():
    path1 = request.form['path1']
    path2 = request.form['path2']
    cc = request.form.get('cc', False)
    lc = request.form.get('lc', False)

    # check if the user provided valid paths
    if m.check_path(path1) == "Invalid path":
        if m.check_path(path2) == "Invalid path":
            return render_template('file_comp.html', result="Neither path exists!")
        return render_template('file_comp.html', result="Path 1 does not exist!")
    if m.check_path(path2) == "Invalid path":
        return render_template('file_comp.html', result="Path 2 does not exist!")

    # check if the user provided directories
    if not os.path.isdir(path1):
        if not os.path.isdir(path2):
            return render_template('file_comp.html', result="Neither path points to a directory!")
        return render_template('file_comp.html', result="Path 1 does not point to a directory!")
    if not os.path.isdir(path2):
        return render_template('file_comp.html', result="Path 2 does not point to a directory!")

    # get pretty table, make html
    pretty_table = m.file_comp(path1, path2, cc=cc, lc=lc)
    table_html = pretty_table.get_html_string()

    # remove ANSI add HTML color
    table_html = apply_html_colors(table_html)

    # result page
    return render_template('fc_result.html', result=table_html, p1=path1, p2=path2)


# FTP file comparison page
@app.route('/file_comp_ftp', methods=['POST'])
def file_comp_ftp():
    host_url1 = request.form['host1']
    username1 = request.form['user1']
    password1 = request.form['pass1']
    path1 = request.form['path1']
    host_url2 = request.form['host2']
    username2 = request.form['user2']
    password2 = request.form['pass2']
    path2 = request.form['path2']
    cc = request.form.get('cc', False)
    lc = request.form.get('lc', False)

    # parse the host url given
    result = m.parse_ftp_url(host_url1)

    # if the username is in the url
    if result[2] is not None:
        username1 = result[2]

    # if the password is in the url
    if result[3] is not None:
        password1 = result[3]

    # if the path is in the url
    if result[4] is not None and len(result[4]) != 0:
        path1 = result[4]

    # try ftp 1
    ftp1 = m.test_ftp(result[0], result[1], username1, password1, path1, is_file=True)
    # it worked
    if type(ftp1) != int:
        res = "FTP 1 successful!"
    # got in but path does not exist
    elif ftp1 == 0:
        res = "Path 1 does not exist!"
    # failed to access FTP server
    else:
        res = "Access to FTP 1 failed!"

    # parse the host url given
    result = m.parse_ftp_url(host_url2)

    # if the username is in the url
    if result[2] is not None:
        username2 = result[2]

    # if the password is in the url
    if result[3] is not None:
        password2 = result[3]

    # if the path is in the url
    if result[4] is not None and len(result[4]) != 0:
        path2 = result[4]

    # try ftp2
    ftp2 = m.test_ftp(result[0], result[1], username2, password2, path2, is_file=True)
    # it worked
    if type(ftp2) != int:
        res = res + " FTP 2 successful!"
    # got in but path does not exist
    elif ftp2 == 0:
        res = res + " Path 2 does not exist!"
    # failed to access FTP server
    else:
        res = res + " Access to FTP 2 failed!"

    # if either FTP access failed
    if type(ftp1) == int or type(ftp2) == int:
        return render_template('file_comp_ftp.html', result=res)
    # successes
    else:
        # get pretty table, make html
        pretty_table = m.file_comp_ftp(ftp1, ftp2, path1, path2, cc=cc, lc=lc)
        table_html = pretty_table.get_html_string()

        ftp1.quit()
        ftp2.quit()

        # remove ANSI add HTML color
        table_html = apply_html_colors(table_html)

        # result page
        return render_template('fc_ftp_result.html', result=table_html, host1=host_url1, host2=host_url2,
                               user1=username1, user2=username2, pass1=password1, pass2=password2, p1=path1, p2=path2)


# code comparison page
@app.route('/code_comp', methods=['POST'])
def code_comp():
    local = request.form.get('local', '')
    path1 = request.form['path1']
    path2 = request.form['path2']

    # is there a local path (from file comparison)
    if len(local) > 0:
        res = m.code_comp_files(path1 + '/' + local, path2 + '/' + local)
    else:
        res = m.code_comp_files(path1, path2)

    # if successful (prettytable, nots str)
    if type(res) != str:
        # get pretty table, make html
        table_html = res.get_html_string()

        # remove ANSI add HTML color
        res = apply_html_colors(table_html)

    return render_template('code_comp.html', result=res)


# ftp code comp page
@app.route('/code_comp_ftp', methods=['POST'])
def code_comp_ftp():
    host_url1 = request.form['host1']
    username1 = request.form['user1']
    password1 = request.form['pass1']
    path1 = request.form['path1']
    host_url2 = request.form['host2']
    username2 = request.form['user2']
    password2 = request.form['pass2']
    path2 = request.form['path2']

    content1 = ''
    content2 = ''

    # parse the host url given
    result = m.parse_ftp_url(host_url1)

    # if the username is in the url
    if result[2] is not None:
        username1 = result[2]

    # if the password is in the url
    if result[3] is not None:
        password1 = result[3]

    # if the path is in the url
    if result[4] is not None and len(result[4]) != 0:
        path1 = result[4]

    # try ftp 1
    status = m.test_ftp(result[0], result[1], username1, password1, path1, is_file=True)
    # it worked
    if type(status) != int:
        res = "FTP 1 successful!"
        content1 = m.read_file_from_ftp(status, path1)
        status.quit()
    # got in but path does not exist
    elif status == 0:
        res = "Path 1 does not exist!"
    # failed to access FTP server
    else:
        res = "Access to FTP 1 failed!"

    # parse the host url given
    result = m.parse_ftp_url(host_url2)

    # if the username is in the url
    if result[2] is not None:
        username2 = result[2]

    # if the password is in the url
    if result[3] is not None:
        password2 = result[3]

    # if the path is in the url
    if result[4] is not None and len(result[4]) != 0:
        path2 = result[4]

    # try ftp2
    status = m.test_ftp(result[0], result[1], username2, password2, path2, is_file=True)
    # it worked
    if type(status) != int:
        res = res + " FTP 2 successful!"
        content2 = m.read_file_from_ftp(status, path2)
        status.quit()
    # got in but path does not exist
    elif status == 0:
        res = res + " Path 2 does not exist!"
    # failed to access FTP server
    else:
        res = res + " Access to FTP 2 failed!"

    # code comp if both contents were found
    if len(content1) > 1 and len(content2) > 1:
        res = m.code_comp_strings(content1, content2)
        print(res)

    # if successful (prettytable, nots str)
    if type(res) != str:
        # get pretty table, make html
        table_html = res.get_html_string()

        # remove ANSI add HTML color
        res = apply_html_colors(table_html)

    return render_template('code_comp_ftp.html', result=res)


# link check page
@app.route('/link_check', methods=['POST'])
def link_check():
    url = request.form['url']
    status = m.link_check(url)
    # remove ANSI add HTML color
    status = apply_html_colors(status)
    status = f"The url \'{url}\' is " + status
    return render_template('link_check.html', result=status)


# file link check page
@app.route('/link_check_file', methods=['POST'])
def link_check_file():
    local = request.form.get('local', '')
    path = request.form['path']

    # is there a local path (from file comparison)
    if len(local) > 0:
        out_list = m.links_check_file(path + '/' + local)
    else:
        out_list = m.links_check_file(path)

    # failure
    if type(out_list) == str:
        return render_template('link_check_file.html', result=out_list)
    res = ""
    for item in out_list:
        res = res + item + "\n"
    # remove ANSI add HTML color
    res = apply_html_colors(res)
    return render_template('link_check_file.html', result=res)


# ftp link check page
@app.route('/link_check_ftp', methods=['POST'])
def link_check_ftp():
    host_url = request.form['host']
    username = request.form['user']
    password = request.form['pass']
    path = request.form['path']

    content = ''

    # parse the host url given
    result = m.parse_ftp_url(host_url)

    # if the username is in the url
    if result[2] is not None:
        username = result[2]

    # if the password is in the url
    if result[3] is not None:
        password = result[3]

    # if the path is in the url
    if result[4] is not None and len(result[4]) != 0:
        path = result[4]

    status = m.test_ftp(result[0], result[1], username, password, path, is_file=True)
    # got in
    if type(status) != int:
        res = "FTP successful!"
        content = m.read_file_from_ftp(status, path)
        status.quit()
    # got in but path does not exist
    elif status == 0:
        res = "Path does not exist!"
    # failed to access FTP server
    else:
        res = "Access to FTP failed!"

    # link check if content found
    if len(content) > 1:
        out_list = m.links_check_string(content)
        # failure
        if type(out_list) == str:
            return render_template('link_check_file.html', result=out_list)
        res = ""
        for item in out_list:
            res = res + item + "\n"
        # remove ANSI add HTML color
        res = apply_html_colors(res)
        return render_template('link_check_file.html', result=res)

    return render_template('link_check_ftp.html', result=res)


# aid with navigating with the radio button
@app.route('/navigate', methods=['POST'])
def navigate():
    selected_page = request.form.get('page')

    if selected_page == 'wget':
        return render_template('wget.html')
    elif selected_page == 'ftp':
        return render_template('ftp.html')
    elif selected_page == 'file_comp':
        return render_template('file_comp.html')
    elif selected_page == 'file_comp_ftp':
        return render_template('file_comp_ftp.html')
    elif selected_page == 'code_comp':
        return render_template('code_comp.html')
    elif selected_page == 'code_comp_ftp':
        return render_template('code_comp_ftp.html')
    elif selected_page == 'link_check':
        return render_template('link_check.html')
    elif selected_page == 'link_check_file':
        return render_template('link_check_file.html')
    elif selected_page == 'link_check_ftp':
        return render_template('link_check_ftp.html')
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
