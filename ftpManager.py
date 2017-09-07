# -*- coding: utf-8 -*-
'''
Created on 2017年8月23日

@author: Simba
'''


import ftplib
import os
import logging
import logmodule.logService as logService


class myFtp:
    ftp = ftplib.FTP()
    bIsDir = False
    path = ""
    
    def __init__(self, host, port='21'):
        # self.ftp.set_debuglevel(2) # 打开调试级别2，显示详细信息
        # self.ftp.set_pasv(0)      # 0主动模式 1 #被动模式
        self.ftp.connect(host, port)
            
    def Login(self, user, passwd):
        self.ftp.login(user, passwd)
        logging.info(self.ftp.welcome)

    def DownLoadFile(self, LocalFile, RemoteFile):
        file_handler = open(LocalFile, 'wb')
        self.ftp.retrbinary("RETR %s" % (RemoteFile), file_handler.write)
        file_handler.close()
        return True
    
    def UpLoadFile(self, LocalFile, RemoteFile):
        if os.path.isfile(LocalFile) is False:
            return False
        file_handler = open(LocalFile, "rb")
        self.ftp.storbinary('STOR %s' % RemoteFile, file_handler, 4096)
        file_handler.close()
        return True

    def UpLoadFileTree(self, LocalDir, RemoteDir):
        if os.path.isdir(LocalDir) is False:
            return False
        logging.info("LocalDir: %s" % LocalDir)
        LocalNames = os.listdir(LocalDir)
        print "list:", LocalNames
        
        print RemoteDir
        self.ftp.cwd(RemoteDir)
        for Local in LocalNames:
            src = os.path.join(LocalDir, Local)
            if os.path.isdir(src):
                self.UpLoadFileTree(src, Local)
            else:
                self.UpLoadFile(src, Local)
                
        self.ftp.cwd("..")
        return
    
    def DownLoadFileTree(self, LocalDir, RemoteDir):
        print "remoteDir:", RemoteDir
        if os.path.isdir(LocalDir) is False:
            os.makedirs(LocalDir)
        self.ftp.cwd(RemoteDir)
        RemoteNames = self.ftp.nlst()
        print "RemoteNames", RemoteNames
        print self.ftp.nlst("/del1")
        for filee in RemoteNames:
            Local = os.path.join(LocalDir, filee)
            if self.isDir(filee):
                self.DownLoadFileTree(Local, filee)
            else:
                self.DownLoadFile(Local, filee)
        self.ftp.cwd("..")
        return
    
    def show(self, listt):
        result = listt.lower().split(" ")
        if self.path in result and "<dir>" in result:
            self.bIsDir = True
     
    def isDir(self, path):
        self.bIsDir = False
        self.path = path
        # this ues callback function ,that will change bIsDir value
        self.ftp.retrlines('LIST', self.show)
        return self.bIsDir
    
    def close(self):
        self.ftp.quit()
        
        
# ftp下载目录
def ftpDownloadDir(ftpHost, ftpuser, ftpPwd, localDir, remoteDir):
    ftp = myFtp(ftpHost)
    ftp.Login(ftpuser, ftpPwd)
    ftp.DownLoadFileTree(localDir, remoteDir)
    ftp.close()


# ftp上传目录
def ftpUploadDir(ftpHost, ftpuser, ftpPwd, localDir, remoteDir):
    ftp = myFtp(ftpHost)
    ftp.Login(ftpuser, ftpPwd)
    ftp.UpLoadFileTree(localDir, remoteDir)
    ftp.close()


# ftp下载文件
def ftpDownloadFile(ftpHost, ftpuser, ftpPwd, localFilepath, remoteFilepath):
    ftp = myFtp(ftpHost)
    ftp.Login(ftpuser, ftpPwd)
    ftp.DownLoadFile(localFilepath, remoteFilepath)
    ftp.close()


# ftp上传文件

def ftpUploadFile(ftpHost, ftpuser, ftpPwd, localFilepath, remoteFilepath):
    ftp = myFtp(ftpHost)
    ftp.Login(ftpuser, ftpPwd)
    ftp.UpLoadFile(localFilepath, remoteFilepath)
    ftp.close()


if __name__ == "__main__":
    logService.initLogging()
    ftp = myFtp('10.0.250.250')
    ftp.Login('buildftp', 'buildftp')
    ftp.DownLoadFileTree(r'D:\a\aa\bbbb', r'/DataBk/build/star-billing/V10.3.0-RC/V10.3.0-RC/V10.3.0-RC-296-170725')
    ftp.close()
    logService.destoryLogging()
    