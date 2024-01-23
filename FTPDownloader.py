# downloads FTP files to local
import os


class FTPDownloader:
    def __init__(self):
        pass

    # check if item on ftp is a directory
    def is_dir(self, ftp_instance, item_name):
        # remember current directory
        original_cwd = ftp_instance.pwd()
        # change directory to item_name
        try:
            ftp_instance.cwd(item_name)
            # go back
            ftp_instance.cwd(original_cwd)
            return True
        # change failed, not a directory
        except Exception as e:
            return False

    # make directory if doesnt exist
    def make_dir(self, fpath):
        dir_item_name = os.path.dirname(fpath)
        while not os.path.exists(dir_item_name):
            try:
                os.mkdir(dir_item_name)
            except Exception as e:
                self.make_dir(dir_item_name)

    # download file from ftp
    def download_file(self, ftp_instance, item_name, dest):
        # make dir if not already made
        self.make_dir(dest)
        # if file doesnt exist
        if not os.path.exists(dest):
            with open(dest, 'wb') as f:
                ftp_instance.retrbinary("RETR {0}".format(item_name), f.write)
        # file exists but should stay the same
        else:
            pass

    # recursively mirror directories
    def mirror_dir(self, ftp_instance, item_name):
        for item in ftp_instance.nlst(item_name):
            if self.is_dir(ftp_instance, item):
                self.mirror_dir(ftp_instance, item)
            else:
                self.download_file(ftp_instance, item, item)

    # download files and directories from path in given ftp_instance to local dest
    def download(self, ftp_instance, path, dest):
        os.chdir(dest)
        self.mirror_dir(ftp_instance, path)