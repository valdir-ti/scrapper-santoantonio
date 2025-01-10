import os

def connect_ftp():
    ftp_config = {
        "ftp_host": os.getenv('FTP_HOST'),
        "ftp_user": os.getenv('FTP_USER'),
        "ftp_password": os.getenv('FTP_PASS'),
        "ftp_folder": "/santo-antonio/images"
    }
    return ftp_config