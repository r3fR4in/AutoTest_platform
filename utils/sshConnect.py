import io

import paramiko

class SSH:

    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.client.get_transport())

    """关闭连接"""
    def close_connect(self):
        self.sftp.close()
        self.client.close()

    """上传文件"""
    def upload_file(self, localpath, remotepath, filename):
        localFilepath = localpath + '/' + filename
        remoteFilepath = remotepath + '/' + filename
        self.exist_path(remotepath)
        self.sftp.put(localFilepath, remoteFilepath)
        # self.session.exec_command('sudo put ' + localFilepath + ' [' + remoteFilepath + ']')

    """下载文件"""
    def download_file(self, localpath, remotepath, filename):
        localFilepath = localpath + '/' + filename
        remoteFilepath = remotepath + '/' + filename
        self.exist_path(remotepath)
        self.sftp.get(remoteFilepath, localFilepath)
        # self.session.exec_command('sudo scp ')

    """删除文件"""
    def delete_file(self, remotepath, filename):
        filepath = remotepath + '/' + filename
        self.sftp.remove(filepath)
        self.sftp.close()
        self.client.close()

    """判断文件夹是否存在，不存在则创建文件夹（创建文件夹不适用于windows系统，需要提前建好文件夹）"""
    def exist_path(self, path, mode=777):
        try:
            print('path:' + path)
            self.sftp.stat(path)
        except IOError as e:
            print('error:' + str(e))
            self.sftp.mkdir(path, mode)
            # self.client.exec_command('sudo mkdir ' + path)

    """判断文件是否存在"""
    def exist_file(self, path):
        try:
            self.sftp.stat(path)
            return True
        except IOError:
            return False

    """读取远程服务器文件"""
    def open_file(self, localpath, remotepath, filename):
        self.download_file(localpath, remotepath, filename)
        localFilepath = localpath + '/' + filename
        return open(localFilepath, 'rb')


# if __name__ == '__main__':
#     host = '172.30.21.53'
#     port = '22'
#     username = 'Niko'
#     password = 'Abcd1234'
#     ssh = SSH(host, port, username, password)
#     ssh.download_file('D:/PycharmProjects/AutoTest_platform/updateFiles/submittedTests', 'D:/PycharmProjects/at_platform_file/submittedTests', 'test.txt')
