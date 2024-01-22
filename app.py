from flask import Flask, render_template, request
from ftplib import FTP
import re
from main import MainClass
from LinkChecker import LinkChecker

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
    valid_path = m.check_path(path, make=True)
    response = m.runcmd(["--directory-prefix=" + valid_path, url], verbose=True)
    return render_template('wget.html', result=response)


# DOES NOT WORK (FILLER)
# ftp download page
@app.route('/ftp', methods=['POST'])
def ftp():
    hostname = request.form['host']
    username = request.form['user']
    password = request.form['pass']
    path = request.form['path']
    try:
        with FTP(hostname) as ftp_instance:
            ftp_instance.login(username, password)
            ftp_instance.cwd(path)
            res = ftp_instance.retrlines('LIST')
    except Exception as e:
        # Print or log the error message
        res = f"FTP Access Error: {e}"
    return render_template('ftp.html', result=res)


# file comparison page
@app.route('/file_comp', methods=['POST'])
def file_comp():
    path1 = request.form['path1']
    path2 = request.form['path2']
    cc = request.form.get('cc', False)
    lc = request.form.get('lc', False)

    if m.check_path(path1) == "Invalid path":
        if m.check_path(path2) == "Invalid path":
            return render_template('file_comp.html', result="Neither path exists!")
        return render_template('file_comp.html', result="Path 1 does not exist!")
    if m.check_path(path2) == "Invalid path":
        return render_template('file_comp.html', result="Path 2 does not exist!")
    # get pretty table, make html
    pretty_table = m.file_comp(path1, path2, cc=cc, lc=lc)
    table_html = pretty_table.get_html_string()

    # remove ANSI add HTML color
    table_html = apply_html_colors(table_html)

    # result page
    return render_template('fc_result.html', result=table_html, p1=path1, p2=path2)


# DOES NOT WORK (FILLER)
# ftp file comp page
@app.route('/file_comp_ftp', methods=['POST'])
def file_comp_ftp():
    hostname1 = request.form['host1']
    username1 = request.form['user1']
    password1 = request.form['pass1']
    path1 = request.form['path1']
    hostname2 = request.form['host2']
    username2 = request.form['user2']
    password2 = request.form['pass2']
    path2 = request.form['path2']
    try:
        with FTP(hostname1) as ftp:
            ftp.login(username1, password1)
            ftp.cwd(path1)
            res = ftp.retrlines('LIST')
        with FTP(hostname2) as ftp:
            ftp.login(username2, password2)
            ftp.cwd(path2)
            res = ftp.retrlines('LIST')
    except Exception as e:
        # Print or log the error message
        res = f"FTP Access Error: {e}"

    return render_template('file_comp_ftp.html', result=res)


# DOES NOT WORK (FILLER)
# code comparison page
@app.route('/code_comp', methods=['POST'])
def code_comp():
    local = request.form.get('local', '')

    path1 = request.form['path1']
    path2 = request.form['path2']

    if len(local) > 0:
        res = m.code_comp(path1 + '/' + local, path2 + '/' + local)
    else:
        res = m.code_comp(path1, path2)

    if type(res) != str:
        # get pretty table, make html
        table_html = res.get_html_string()

        # remove ANSI add HTML color
        res = apply_html_colors(table_html)

    return render_template('code_comp.html', result=res)


# ftp code comp page
@app.route('/code_comp_ftp', methods=['POST'])
def code_comp_ftp():
    hostname1 = request.form['host1']
    username1 = request.form['user1']
    password1 = request.form['pass1']
    path1 = request.form['path1']
    hostname2 = request.form['host2']
    username2 = request.form['user2']
    password2 = request.form['pass2']
    path2 = request.form['path2']
    try:
        with FTP(hostname1) as ftp:
            ftp.login(username1, password1)
            ftp.cwd(path1)
            res = ftp.retrlines('LIST')
        with FTP(hostname2) as ftp:
            ftp.login(username2, password2)
            ftp.cwd(path2)
            res = ftp.retrlines('LIST')
    except Exception as e:
        # Print or log the error message
        res = f"FTP Access Error: {e}"

    return render_template('code_comp_ftp.html', result=res)


# link check page
@app.route('/link_check', methods=['POST'])
def link_check():
    url = request.form['url']
    lc = LinkChecker()
    lc.link_check(url)
    status = apply_html_colors(lc.get_status())
    status = f"The url \'{url}\' is " + status
    return render_template('link_check.html', result=status)


# file link check page
@app.route('/link_check_file', methods=['POST'])
def link_check_file():
    local = request.form.get('local', '')

    path = request.form['path']
    if len(local) > 0:
        out_list = m.links_check(path + '/' + local)
    else:
        out_list = m.links_check(path)

    if type(out_list) == str:
        return render_template('link_check_file.html', result=out_list)
    res = ""
    for item in out_list:
        res = res + item + "\n"
    res = apply_html_colors(res)
    return render_template('link_check_file.html', result=res)


# DOES NOT WORK (FILLER)
# ftp link check page
@app.route('/link_check_ftp', methods=['POST'])
def link_check_ftp():
    hostname = request.form['host']
    username = request.form['user']
    password = request.form['pass']
    path = request.form['path']
    try:
        with FTP(hostname) as ftp_instance:
            ftp_instance.login(username, password)
            ftp_instance.cwd(path)
            res = ftp_instance.retrlines('LIST')
    except Exception as e:
        # Print or log the error message
        res = f"FTP Access Error: {e}"
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
