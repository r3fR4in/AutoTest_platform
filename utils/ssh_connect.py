import paramiko


class SSH:

    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

    """ssh连接"""
    def ssh_connect(self):
        client = paramiko.SSHClient()
        # 如果之前没有，连接过的ip，会出现选择yes或者no的操作，自动选择yes
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password)

        return client

    """上传文件"""
    def upload_file(self, localpath, remotepath, filename):
        client = self.ssh_connect()
        sftp = paramiko.SFTPClient.from_transport(client.get_transport())
        localFilepath = localpath + '/' + filename
        remoteFilepath = remotepath + '/' + filename
        self.exist_path(sftp, localpath)
        self.exist_path(sftp, remotepath)
        sftp.put(localFilepath, remoteFilepath)
        sftp.close()
        client.close()

    """下载文件"""
    def download_file(self, localpath, remotepath, filename):
        client = self.ssh_connect()
        sftp = paramiko.SFTPClient.from_transport(client.get_transport())
        localFilepath = localpath + '/' + filename
        remoteFilepath = remotepath + '/' + filename
        self.exist_path(sftp, localpath)
        self.exist_path(sftp, remotepath)
        sftp.get(remoteFilepath, localFilepath)
        sftp.close()
        client.close()

    """删除文件"""
    def delete_file(self, remotepath, filename):
        client = self.ssh_connect()
        sftp = client.open_sftp()
        filepath = remotepath + '/' + filename
        sftp.remove(filepath)
        sftp.close()
        client.close()

    """判断文件夹是否存在，不存在则创建文件夹"""
    @staticmethod
    def exist_path(sftp, path, mode=777):
        try:
            sftp.stat(path)
        except IOError:
            sftp.mkdir(path, mode)


if __name__ == '__main__':
    host = '172.30.21.53'
    port = '22'
    username = 'Niko'
    password = 'Abcd1234'
    ssh = SSH(host, port, username, password)
    ssh.delete_file('D:/PycharmProjects/AutoTest_platform/updateFiles/submittedTests', 'D:/PycharmProjects/at_platform_file/submittedTests', 'test.txt')
