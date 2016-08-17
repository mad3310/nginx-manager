import base64
import logging
import socket

from tornado.httpclient import HTTPClient
from tornado.httpclient import HTTPError
from tornado.options import options

from utils.configFileOpers import ConfigFileOpers
from utils.invokeCommand import InvokeCommand


confOpers = ConfigFileOpers()

def get_zk_address():
    ret_dict = confOpers.getValue(options.nginx_manager_property, ['zkAddress','zkPort'])
    zk_address = ret_dict['zkAddress']
    zk_port = ret_dict['zkPort']
    return zk_address, zk_port

def retrieve_userName_passwd():
    confDict = confOpers.getValue(options.cluster_property, ['adminUser','adminPassword'])
    adminUser = confDict['adminUser']
    adminPasswd = base64.decodestring(confDict['adminPassword'])
    return (adminUser,adminPasswd)

def retrieve_node_name():
    confDict = confOpers.getValue(options.data_node_property, ['dataNodeName'])
    node_name = confDict['dataNodeName']
    return node_name

def get_dict_from_text(sourceText, keyList):
    totalDict = {}
    resultValue = {}

    lineList = sourceText.split('\n')
    for line in lineList:
        if not line:
            continue

        pos1 = line.find('=')
        key = line[:pos1]
        value = line[pos1+1:len(line)].strip('\n')
        totalDict.setdefault(key,value)

    if keyList == None:
        resultValue = totalDict
    else:
        for key in keyList:
            value = totalDict.get(key)
            resultValue.setdefault(key,value)

    return resultValue

def check_leader():
    invokeCommand = InvokeCommand()
    zk_address, zk_port = get_zk_address()
    cmd = "echo stat |nc %s %s| grep Mode" %(zk_address, zk_port)
    ret_str, _ = invokeCommand._runSysCmd(cmd)
    invokeCommand = None
    if ret_str.find('leader') == -1:
        return False

    return True

def get_host_ip():
    cmd="""printenv |grep ^HOST_IP |awk -F= '{print $2}' """
    invokeCommand = InvokeCommand()
    ret_str, _ = invokeCommand._runSysCmd(cmd)
    invokeCommand = None
    return ret_str

def get_host_name():
    host_name = socket.gethostname()
    return host_name

def getClusterUUID():
    ret_dict = confOpers.getValue(options.cluster_property, ['clusterUUID'])
    clusterUUID = ret_dict['clusterUUID']
    return clusterUUID

def set_file_data(filename, data, mode):
    '''
    @todo: use 'with' way
    '''
    f = open(filename, mode)
    f.write(data)
    f.close()

def get_file_data(filename, mode='rb'):
    f = open(filename, mode)
    data = f.read()
    f.close()
    return data
