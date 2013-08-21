import os

def make_dir(dir_path):
    try:
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
    except Exception, e:
        raise e

INSTANCE_FOLDER_PATH = os.path.join('/tmp', 'instance')
