import os
from config import setting
import shutil

def remove_temp_file():
    """删除镜像的临时文件"""
    rootdir = os.path.join(setting.BASE_DIR, "updateFiles")
    filePathList = os.listdir(rootdir)
    for filePath in filePathList:
        path = os.path.join(rootdir, filePath)
        fileList = os.listdir(path)
        for file in fileList:
            f = os.path.join(path, file)
            if os.path.isfile(f):
                os.remove(f)
            else:
                shutil.rmtree(f)
