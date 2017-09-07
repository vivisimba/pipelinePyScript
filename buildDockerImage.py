# -*- coding: utf-8 -*-
'''
Created on 2017年9月1日

@author: Simba
'''


import config.config as CONFIG
import os
import zipfile
import logging
import logmodule.logService as logService
import sys
import subprocess
import exception.myException as myexception

        
def unzipFile(zipFilePath, unzipFilePath=None):
    '''
    :param zipFilePath:被解压缩文件的绝对路径
    :param unzipFilePath:解压后存放的绝对路径
    '''
    if zipfile.is_zipfile(zipFilePath):
        print "hello hello"
        fz = zipfile.ZipFile(zipFilePath, 'r')
        for f in fz.namelist():
            fz.extract(f, unzipFilePath)
        return True
    else:
        msg = 'This file is not zip file'
        print msg
        # exception_write("unzipFile", msg)
        logging.error(msg)
        return False


def getFileList(filePath):
    fileList = []
    list_dirs = os.walk(filePath)
    for root, _, files in list_dirs:
        for f in files:
            fileList.append(f)
    return fileList


def removeRepetitionLibs(moduleLibPath, commonLibPath):
    moduleLibList = getFileList(moduleLibPath)
    commonLibList = getFileList(commonLibPath)
    repetList = list((set(moduleLibList).union(set(commonLibList))) ^ (set(moduleLibList) ^ set(commonLibList)))
    # 删除moduleLibPath中重复的libs
    for name in repetList:
        libPath = moduleLibPath + name
        os.remove(libPath)
        print "os.remove(%s)" % (libPath)
    return repetList


def modifyWebXML(xmlPath, libList, commonLibPath):
    old = open(xmlPath)
    texts = old.readlines()
    new_texts = []
    
    s = "<Context>\n"
    s += "  <Resources>\n"
    
    for lib in libList:
        s += '''    <JarResources className="org.apache.catalina.webresources.FileResourceSet" base="%s%s" webAppMount="/WEB-INF/lib/%s"/>\n''' % (commonLibPath, lib, lib)

    s += "  <Resources>\n"
    s += "<Context>\n"

    flag = False
    for line in texts:
        if "</Context>" in line and flag is False:
            line += "\n" + s
            flag = True
        new_texts.append(line)

    if flag is False:
        line += "\n" + s
        new_texts.append(line)
    new = open(xmlPath, 'w')
    new.writelines(new_texts)
    new.close()
    old.close()


# 编辑war包的context.xml文件
def modifyContext(codeDir, moduleName):
    if moduleName in CONFIG.EXTRA_WAR_DIC.keys():
        warPath = os.path.join(codeDir, "outputFileFolder", CONFIG.EXTRA_WAR_DIC[moduleName])
        warDirName = CONFIG.EXTRA_WAR_DIC[moduleName].split(".war")[0]
        warDirPath = os.path.join(codeDir, "outputFileFolder", warDirName)
    else:
        warPath = os.path.join(codeDir, "outputFileFolder", moduleName + ".war")
        warDirPath = os.path.join(codeDir, "outputFileFolder", moduleName)
    if unzipFile(warPath, warDirPath):
        libPath = warDirPath + "/WEB-INF/lib/"
        repetLibList = removeRepetitionLibs(libPath, CONFIG.DOCKER_INFO["thirjarsDirInBuildImage"])
        XML_PATH = os.path.join(codeDir, "outputFileFolder", "context.xml")
        modifyWebXML(XML_PATH, repetLibList, CONFIG.DOCKER_INFO["thirjarsDirInBuildImage"])


# 构建镜像
def createDockerImage(fileDir, dockerfile, newTag, buildLogAbsolutePath):
    if not os.path.exists(buildLogAbsolutePath):
        os.makedirs(buildLogAbsolutePath)
    moduleName = (os.path.splitext(dockerfile)[0]).lower()
    if dockerfile == 'order-job.Dockerfile':
        imageName = os.path.join(CONFIG.DOCKER_INFO["registryaddress"], CONFIG.DOCKER_INFO["billingimagedir"], moduleName + ":" + newTag)
    elif dockerfile == 'billing.Dockerfile':
        imageName = os.path.join(CONFIG.DOCKER_INFO["registryaddress"], CONFIG.DOCKER_INFO["billingimagedir"], moduleName + ":" + newTag)
    elif dockerfile == "uploadjarfile.Dockerfile":
        imageName = os.path.join(CONFIG.DOCKER_INFO["registryaddress"], CONFIG.DOCKER_INFO["billingimagedir"], moduleName + ":" + newTag)
    elif dockerfile == "spark-jobserver.Dockerfile":
        imageName = os.path.join(CONFIG.DOCKER_INFO["registryaddress"], CONFIG.DOCKER_INFO["billingimagedir"], moduleName + ":" + newTag)
    else:
        imageName = os.path.join(CONFIG.DOCKER_INFO["registryaddress"], CONFIG.DOCKER_INFO["bossimagerdir"], moduleName + ":" + newTag)

    actualStr = "docker build -t %s -f %s %s 2>&1 |grep -v 'Sending build context to Docker daemon' > %s/build_%s_image.log" % \
                (imageName, dockerfile, '.', buildLogAbsolutePath, moduleName)
    print actualStr
    print imageName
    print dockerfile

    p = subprocess.Popen(actualStr, shell=True)
    p.wait()
    f = open((buildLogAbsolutePath + ('/build_%s_image.log' % moduleName)), 'r')
    lineList = f.readlines()
    f.close()
    boolFlag = False
    for line in lineList:
        if 'Successfully built' in line:
            boolFlag = True
    return boolFlag


def exception_write(fun_name, msg):
    """
    写入异常信息到日志
    """
    f = open(os.path.join(CONFIG.LOG_HOME, 'log.txt'), 'a')
    line = "%s %s\n" % (fun_name, msg)
    f.write(line)
    f.close()


# 登录镜像仓库
def logInImageRegistory():
    rightStr = 'docker login -u %s  -p %s %s' % (CONFIG.DOCKER_INFO['registoryusername'],
                                                 CONFIG.DOCKER_INFO['registorypassword'],
                                                 CONFIG.DOCKER_INFO['registryaddress'])
    logging.info("exec: %s" % rightStr)
    p = subprocess.Popen(rightStr, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    resList = p.stdout.readlines()
    if len(resList) != 0:
        for i in resList:
            logging.info("%s" % i.strip())
    else:
        errStrList = p.stderr.readlines()
        errStrStripList = []
        for j in errStrList:
            errStrStripList.append(j.strip())
        errStr = ','.join(errStrStripList)
        raise myexception.MyException("%s" % errStr)


# 推送镜像到仓库
def pushImageToRepository(warImageName, tagName, repositoryName):
    imageName = os.path.join(repositoryName, warImageName)
    command = "docker push %s:%s" % (imageName, tagName)
    print command
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    resTup = p.communicate()
    errStr = resTup[1]
    if len(errStr) == 0:
        print "%s pushed successfully." % (imageName + ':' + tagName)
        return True
    else:
        print errStr
        msg = "%s pushed failed." % (imageName + ':' + tagName)
        print msg
        exception_write("pushImageToRepository", msg)
        return False


# 删除镜像
def deleteImage(warImageName, tagName, repositoryName):
    imageName = os.path.join(repositoryName, warImageName)
    command = "docker rmi %s:%s" % (imageName, tagName)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    resTup = p.communicate()
    errStr = resTup[1]
    if len(errStr) == 0:
        print "%s deleted successfully." % (imageName + ':' + tagName)
        return True
    else:
        msg = "%s deleted failed." % (imageName + ':' + tagName)
        print msg
        exception_write("deleteImage", msg)
        return False


def run():
    '''
    :param 脚本本身（非传入参数）
    :param codeDir:   代码目录
    :param moduleName: 模块名
    :param newTag: 标签
    '''
    parameterList = sys.argv
    
    codeDir = parameterList[1]
    moduleName = parameterList[2]
    
    notWarList = CONFIG.MV_ZIP_LIST[:]
    notWarList.append("jobserver")
    
    if moduleName not in notWarList:
        modifyContext(codeDir, moduleName)
    
    os.chdir(os.path.join(codeDir, 'outputFileFolder'))
    
    if moduleName in CONFIG.MV_ZIP_LIST:
        zipFilePath = os.path.join(codeDir, 'outputFileFolder', moduleName + ".zip")
        unzipFileDir = os.path.join(codeDir, 'outputFileFolder', moduleName)
        unzipFile(zipFilePath, unzipFileDir)
    
    # 构建镜像
    baseDir = os.path.join(codeDir, 'outputFileFolder')
    newTag = parameterList[3]
    buildLogAbsolutePath = os.path.join(CONFIG.LOG_HOME, newTag + "_buildimages_log")
    if moduleName == "jobserver":
        # jobserver
        dockerfile = "spark-jobserver.Dockerfile"
        print dockerfile
#         newTag = parameterList[3]
#         buildLogAbsolutePath = os.path.join(CONFIG.LOG_HOME, newTag + "_buildimages_log")
        createDockerImage(baseDir, dockerfile, newTag, buildLogAbsolutePath)
        logging.info("Create image for %s successfully." % "jobserver")
        
        # uploadjarfile
        dockerfile = "uploadjarfile.Dockerfile"
        print dockerfile
#         newTag = parameterList[3]
#         buildLogAbsolutePath = os.path.join(CONFIG.LOG_HOME, newTag + "_buildimages_log")
        createDockerImage(baseDir, dockerfile, newTag, buildLogAbsolutePath)
        logging.info("Create image for %s successfully." % "uploadjarfile")
    else:
        dockerfile = moduleName + ".Dockerfile"
#         newTag = parameterList[3]
#         buildLogAbsolutePath = os.path.join(CONFIG.LOG_HOME, newTag + "_buildimages_log")
        createDockerImage(baseDir, dockerfile, newTag, buildLogAbsolutePath)
        logging.info("Create image for %s successfully." % moduleName)
    
    # 登录镜像仓库
    logInImageRegistory()
    
    # 推送并删除镜像
    if moduleName in ["order-job", "billing"]:
        repositoryName = os.path.join(CONFIG.DOCKER_INFO["registryaddress"], CONFIG.DOCKER_INFO["billingimagedir"])
        pushImageToRepository(moduleName.lower(), newTag, repositoryName)
        deleteImage(moduleName.lower(), newTag, repositoryName)
    elif moduleName == "jobserver":
        repositoryName = os.path.join(CONFIG.DOCKER_INFO["registryaddress"], CONFIG.DOCKER_INFO["billingimagedir"])
        
        pushImageToRepository("spark-jobserver".lower(), newTag, repositoryName)
        deleteImage("spark-jobserver".lower(), newTag, repositoryName)
        
        pushImageToRepository("uploadjarfile".lower(), newTag, repositoryName)
        deleteImage("uploadjarfile".lower(), newTag, repositoryName)
        
    else:
        repositoryName = os.path.join(CONFIG.DOCKER_INFO["registryaddress"], CONFIG.DOCKER_INFO["bossimagerdir"])
        pushImageToRepository(moduleName.lower(), newTag, repositoryName)
        deleteImage(moduleName.lower(), newTag, repositoryName)


if __name__ == '__main__':
    logService.initLogging()
    run()
    logService.destoryLogging()
        
        
        
        
        
        