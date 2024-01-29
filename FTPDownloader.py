# downloads FTP files to local
import os
import re


class FTPDownloader:
    def __init__(self):
        pass

    # check if item on ftp is a directory
    def is_dir(self, ftp_instance, path):
        # remember current directory
        original_cwd = ftp_instance.pwd()
        # change directory to item_name
        try:
            ftp_instance.cwd(path)
            # go back
            ftp_instance.cwd(original_cwd)
            return True
        # change failed, not a directory
        except Exception as e:
            return False

    # download file from ftp
    def download_file(self, ftp_instance, item_name, path):
        with open(os.path.join(os.getcwd(), item_name), 'wb') as f:
            ftp_instance.retrbinary("RETR {0}".format(path), f.write)

    # recursively mirror directories
    def mirror_dir(self, ftp_instance, local_path, sub_dir):
        add_path = re.split(r'[\\/]', local_path, maxsplit=sub_dir)
        if len(add_path) < 2:
            add_path.append("")
        dir_name = add_path[len(add_path)-1]

        os.chdir(os.getcwd()+'/'+dir_name)

        for item in ftp_instance.nlst(local_path):
            path = local_path + '/' + item
            if self.is_dir(ftp_instance, path):
                if not os.path.exists(item):
                    os.makedirs(item)
                self.mirror_dir(ftp_instance, path, sub_dir+1)
            else:
                self.download_file(ftp_instance, item, path)
        os.chdir("..")

    # download files and directories from path in given ftp_instance to local dest
    def download(self, ftp_instance, path, dest):
        os.chdir(dest)
        self.mirror_dir(ftp_instance, path, 1)
