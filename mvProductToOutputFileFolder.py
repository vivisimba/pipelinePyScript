# -*- coding: utf-8 -*-
'''
Created on 2017年8月21日

@author: Simba
'''


import logmodule.logService as logService
import sys
import exception.myException as myexception
import os
import logging
import shutil
import config.config as CONFIG
import build


# 在目录下，递归查找指定名称的文件，返回文件的绝对路径(列表)
def findFile(rootDir, fileName):
    print fileName
    allFileAbsolutePathList = []
    wantFileAbsolutePathList = []
    tupIterator = os.walk(rootDir)
    for i in tupIterator:
        for j in i[2]:
            allFileAbsolutePathList.append(os.path.join(i[0], j))
    # 获得指定文件的绝对路径列表
    for m in allFileAbsolutePathList:
        if m.endswith(fileName):
            wantFileAbsolutePathList.append(m)
    return wantFileAbsolutePathList


# 在某个目录下查找某个(微服务相关war、zip、jar或者dockerfile)文件，获得该文件的绝对路径（文件需在所查找的目录下唯一）
def getFileAbsolutePath(rootDir, fileName):
    fileSourcePathList = findFile(rootDir, fileName)
    if len(fileSourcePathList) > 1:
        raise myexception.MyException("Find too many files for %s" % fileName)
    elif len(fileSourcePathList) < 1:
        raise myexception.MyException("Didn't find file for %s." % fileName)
    else:
        fileAbsolutePathStr = fileSourcePathList[0]
    return fileAbsolutePathStr


# 将文件从原目录移动到目标目录（移动，非拷贝）
def mvfile(srcDir, desDir, fileName):
    srcPath = os.path.join(srcDir, fileName)
    desPath = os.path.join(desDir, fileName)
    shutil.move(srcPath, desPath)


# 输入源目录、目标目录、文件名，进行拷贝操作
def cpfile(srcDir, desDir, fileName):
    srcPath = os.path.join(srcDir, 'context.xml')
    desPath = os.path.join(desDir, 'context.xml')
    shutil.copy(srcPath, desPath)


# 移动指定模块的指定后缀的文件
def mvSuffixFile(rootDir, moduleName, suffix):
    if suffix == ".war":
        if moduleName == "starDA-web":
            fileName = "starDA" + suffix
        elif moduleName == "haiwai-proxy":
            fileName = "stariboss-haiwai_proxy" + suffix
        elif moduleName == "callcenter-proxy":
            fileName = "stariboss-callcenter_proxy" + suffix
        elif moduleName == "api-gateway-service":
            fileName = "api" + suffix
        else:
            fileName = moduleName + suffix
        fileSourcePath = getFileAbsolutePath(rootDir, fileName)
        fileDesPath = os.path.join(rootDir, "outputFileFolder", fileName)
        shutil.move(fileSourcePath, fileDesPath)
    else:
        fileName = moduleName + suffix
        fileSourcePath = getFileAbsolutePath(rootDir, fileName)
        fileDesPath = os.path.join(rootDir, "outputFileFolder", fileName)
        shutil.move(fileSourcePath, fileDesPath)


# # war包文件移动
# def mvFileForWar(codeDir, moduleName):
#     # 移动构建物
#     # 移动构建生成的war文件
#     mvSuffixFile(codeDir, moduleName, ".war")
#     
#     # 移动对应的dockerfile
#     mvSuffixFile(codeDir, moduleName, ".Dockerfile")
#     
#     # 移动对应的conf文件
#     mvSuffixFile(codeDir, moduleName, ".conf")
#     
#     # 移动对应的run.sh文件
#     getModuleDir(rootDir, moduleDirName)
#     # 从脚本目录拷贝context.xml文件
#     srcPath = os.path.join(CONFIG.ROOT_HOME, 'context', 'context.xml')
#     desPath = os.path.join(codeDir, "outputFileFolder", "context.xml")
#     shutil.copy(srcPath, desPath)


# 移动文件
def mvOrCpFile(codeDir, moduleName):
    if moduleName == "billing":
        pass
    elif moduleName == "jobserver":
        pass
    else:
       
# 运行
def run():
    '''
    :param 脚本本身（非传入参数）
    :param codeDir:   代码目录
    :param moduleName: 模块名
    '''
    parameterList = sys.argv

    # 在代码目录创建outputFileFolder文件夹
    wholeOutputFileFolderDir = os.path.join(parameterList[1], "outputFileFolder")
    os.makedirs(wholeOutputFileFolderDir)
    
    if parameterList[2] == "platform-cache-config":
        productAbsolutePathStr = getFileAbsolutePath(parameterList[1], parameterList[2] + ".zip", parameterList[2], "zip")
        dockerfileAbsolutePathStr = getFileAbsolutePath(parameterList[1], parameterList[2] + ".Dockerfile", parameterList[2], "dockerfile")
        dockerfileAbsoluteDirStr = dockerfileAbsolutePathStr.replace('%s.Dockerfile' % parameterList[2], '')
        
    elif parameterList[2] == "platform-config":
        pass
    elif parameterList[2] == "order-job":
        # 构建order-job.zip包：reopenjob使用
        pass
    elif parameterList[2] == "billing":
        pass
    elif parameterList[2] == "starDA-web":
        pass
    elif parameterList[2] == "api-gateway-service":
        pass
    elif parameterList[2] == "jobserver":
        pass
    elif parameterList[2] == "haiwai-proxy":
        pass
    elif parameterList[2] == "callcenter-proxy":
        pass
    else:
        # 获得构建产物的原绝对路径
        productAbsolutePathStr = getFileAbsolutePath(parameterList[1], parameterList[2] + ".war", parameterList[2], "war")

        # 获得dockerfile的原绝对路径
        dockerfileAbsolutePathStr = getFileAbsolutePath(parameterList[1], parameterList[2] + ".Dockerfile", parameterList[2], "dockerfile")
        # 获得dockerfile所在的目录路径
        dockerfileAbsoluteDirStr = dockerfileAbsolutePathStr.replace('%s.Dockerfile' % parameterList[2], '')

    # 移动构建产物到outputFileFolder目录
    shutil.move(productAbsolutePathStr, os.path.join(wholeOutputFileFolderDir, parameterList[2] + ".war"))
    logging.info("product of %s has been moved to the dir: .../outputFileFolder/." % parameterList[2])
    # 移动dockerfile到outputFileFolder目录
    shutil.move(dockerfileAbsolutePathStr, os.path.join(wholeOutputFileFolderDir, parameterList[2] + ".Dockerfile"))
    logging.info("dockerfile of %s has been moved to the dir: .../outputFileFolder/." % parameterList[2])
    # 移动td-agent.conf文件
    mvfile(dockerfileAbsoluteDirStr, wholeOutputFileFolderDir, parameterList[2] + '.conf')
    logging.info("td-agent.conf of %s has been moved to the dir: .../outputFileFolder/." % parameterList[2])
    # 移动run.sh文件
    mvfile(dockerfileAbsoluteDirStr, wholeOutputFileFolderDir, 'run.sh')
    logging.info("run.sh of %s has been moved to the dir: .../outputFileFolder/." % parameterList[2])
    # 从脚本目录拷贝context.xml文件
    cpfile(os.path.join(CONFIG.ROOT_HOME, 'context'), wholeOutputFileFolderDir, 'context.xml')
    logging.info("context.xml of %s has been copyed to the dir: .../outputFileFolder/." % parameterList[2])
    

if __name__ == '__main__':
    logService.initLogging()
    run()
    logService.destoryLogging()




