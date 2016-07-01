'''
Created on Mar 14, 2015

@author: root
'''
import kazoo
import re
import urllib
import tornado
import logging

from zk.zkOpers import Common_ZkOpers
from utils.exceptions import ZKLockException
from utils import retrieve_userName_passwd
from tornado.httpclient import HTTPRequest
from common.abstractOpers import AbstractOpers
from tornado.httpclient import AsyncHTTPClient
from tornado.gen import Callback, Wait

class BaseClusterOpers(AbstractOpers):
    
    oper_type_node_uri = {
        "start":"/cluster/node/start",
        "stop":"/cluster/node/stop",
        "reload":"/cluster/node/reload",
        "config":"/cluster/node/config",
        "enable":"/cluster/node/enable",
        "disable":"/cluster/node/disable"
    }
    
    def __init__(self):
        super(BaseClusterOpers, self).__init__()
    
    def baseOpers(self, node_info_list, oper_type, params={}):
        isLock = False
        lock = None
        zkOper = Common_ZkOpers()
        
        try:
            isLock,lock = zkOper.lock_cluster_start_stop_action()
            self.__dispatch(node_info_list, oper_type, params)
            
        except kazoo.exceptions.LockTimeout:
            raise ZKLockException("current operation is using by other people, please wait a moment to try again!")
        
        finally:
            if isLock:
                zkOper.unLock_cluster_start_stop_action(lock)

    @tornado.gen.engine
    def __dispatch(self, node_info_list, oper_type, params={}):
        result_dict = {}
        adminUser, adminPasswd = retrieve_userName_passwd()
        key_sets = set()
        url_post= self.oper_type_node_uri.get(oper_type)
        logging.info('node list:%s' % str(node_info_list))
        http_client = AsyncHTTPClient()
        try:
            for node_info in node_info_list:
                node_ip = node_info['dataNodeIp']
                node_external_port = node_info['dataNodeExternalPort']
                requesturi = "http://%s:%s%s" % (node_ip, node_external_port, url_post)
                request = HTTPRequest(url=requesturi, method='POST', body=urllib.urlencode(''),
                                      auth_username = adminUser, auth_password = adminPasswd)
                callback_key = "%s_%s" % (node_ip,node_external_port)
                key_sets.add(callback_key)
                http_client.fetch(request, callback=(yield Callback(callback_key)))
                
            error_record_msg = ''
            error_record_ip_list = []
            for callback_key in key_sets:
                response = yield Wait(callback_key)
                
                if response.error:
                    return_result = False
                    message = "remote access,the key:%s,error message:%s" % (callback_key,response.error)
                    error_record_msg += message + "|"
                else:
                    return_result = response.body.strip()
                
                if re.search("successfully", return_result) is None:
                    callback_key_ip, callback_key_port = callback_key.split("_")
                    error_record_ip_list.append("%s:%s" % (callback_key_ip, callback_key_port))
               
            if error_record_ip_list:
                result_dict.setdefault("message","cluster operations failed")
                result_dict.setdefault("detail_message", error_record_msg)
                result_dict.setdefault("ip", error_record_ip_list)
            else:
                result_dict.setdefault("message","cluster operations %s successfully" % oper_type)
            
            logging.info('dispatch result:%s' % str(result_dict))
        finally:
            if http_client is not None:
                http_client.close() 
