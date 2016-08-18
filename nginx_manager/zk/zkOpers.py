#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2013-7-11

@author: asus
'''
import json
import logging
import threading

from utils.configFileOpers import ConfigFileOpers
from kazoo.client import KazooClient, KazooState
from kazoo.exceptions import SessionExpiredError
from kazoo.retry import KazooRetry
from utils import getClusterUUID, get_zk_address
from utils.decorators import zk_singleton


class ZkOpers(object):

    zk = None

    DEFAULT_RETRY_POLICY = KazooRetry(
        max_tries=None,
        max_delay=10000,
    )

    rootPath = "/letv/nginx"
    confOpers = ConfigFileOpers()

    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.zkaddress, self.zkport = get_zk_address()
        if "" != self.zkaddress and "" != self.zkport:
            self.zk = KazooClient(
                                  hosts=self.zkaddress+':'+str(self.zkport),
                                  connection_retry=self.DEFAULT_RETRY_POLICY,
                                  timeout=20)
            self.zk.add_listener(self.listener)
            self.zk.start()
            logging.info("instance zk client (%s:%s)" % (self.zkaddress, self.zkport))

    def close(self):
        try:
            self.zk.stop()
            self.zk.close()
        except Exception, e:
            logging.error(e)

    def stop(self):
        try:
            self.zk.stop()
        except Exception, e:
            logging.error(e)
            raise

    def listener(self, state):
        if state == KazooState.LOST:
            logging.info("zk connect lost, stop this connection and then start new one!")

        elif state == KazooState.SUSPENDED:
            logging.info("zk connect suspended, stop this connection and then start new one!")
            self.re_connect()
        else:
            pass

    def is_connected(self):
        return self.zk.state == KazooState.CONNECTED

    def re_connect(self):
        zk = KazooClient(hosts=self.zkaddress+':'+str(self.zkport), connection_retry=self.DEFAULT_RETRY_POLICY)
        zk.start()
        self.zk = zk
        return self.zk

    def existCluster(self, uuid=None):
        self.zk.ensure_path(self.rootPath)
        cluster_uuids = self.DEFAULT_RETRY_POLICY(self.zk.get_children, self.rootPath)

        if uuid is None:
            local_uuid = getClusterUUID()
        else:
            local_uuid = uuid

        if local_uuid in cluster_uuids:
            return True

        return False

    '''
    @todo: no used?
    '''
    def __getClusterUUIDs(self):
        self.logger.debug(self.rootPath)
        try:
            dataNodesName = self.DEFAULT_RETRY_POLICY(self.zk.get_children, self.rootPath)
        except SessionExpiredError:
            dataNodesName = self.DEFAULT_RETRY_POLICY(self.zk.get_children, self.rootPath)
        return dataNodesName

    def writeClusterInfo(self,clusterUUID,clusterProps):
        path = self.rootPath + "/" + clusterUUID
        self.zk.ensure_path(path)
        self.DEFAULT_RETRY_POLICY(self.zk.set, path, str(clusterProps))#vesion need to write

    def retrieveClusterProp(self,clusterUUID):
        resultValue = {}
        path = self.rootPath + "/" + clusterUUID
        if self.zk.exists(path):
            resultValue = self.DEFAULT_RETRY_POLICY(self.zk.get, path)

        return resultValue



    '''
    data componentNode
    '''
    def writeDataNodeInfo(self,clusterUUID,dataNodeProps):
        dataNodeName = dataNodeProps['dataNodeName']
        path = self.rootPath + "/" + clusterUUID + "/dataNode/" + dataNodeName
        self.zk.ensure_path(path)
        self.DEFAULT_RETRY_POLICY(self.zk.set, path, str(dataNodeProps))#version need to write

    def retrieve_nginx_node_list(self):
        clusterUUID = getClusterUUID()
        path = self.rootPath + "/" + clusterUUID + "/dataNode"
        container_node_name_list = self.__return_children_to_list(path)
        return container_node_name_list

    def retrieve_nginx_node_info(self, container_node_name):
        clusterUUID = getClusterUUID()
        path = self.rootPath + "/" + clusterUUID + "/dataNode/" + container_node_name
        ip_dict = self.__retrieve_special_path_prop(path)
        return ip_dict

    '''
    started componentNode
    '''
    def write_started_node(self, container_node_name):
        clusterUUID = getClusterUUID()
        path = self.rootPath + "/" + clusterUUID + "/monitor_status/node/started/" + container_node_name
        self.zk.ensure_path(path)

    def remove_started_node(self, container_node_name):
        clusterUUID = getClusterUUID()
        path = self.rootPath + "/" + clusterUUID + "/monitor_status/node/started/" + container_node_name
        if self.zk.exists(path):
            self.DEFAULT_RETRY_POLICY(self.zk.delete, path)

    def retrieve_started_nodes(self):
        clusterUUID = getClusterUUID()
        path = self.rootPath + "/" + clusterUUID + "/monitor_status/node/started"
        started_nodes = self.__return_children_to_list(path)
        return started_nodes

    '''
    @todo: currently, no used
    '''
    def writeNginxCnf(self, NginxCnfPropsFullText):
        clusterUUID = getClusterUUID()
        path = self.rootPath + "/" + clusterUUID + "/nginxcnf"
        self.zk.ensure_path(path)
        self.DEFAULT_RETRY_POLICY(self.zk.set, path, NginxCnfPropsFullText)#version need to write

    '''
    @todo: currently, no used
    '''
    def retrieveNginxCnf(self):
        clusterUUID = getClusterUUID()
        resultValue = {}
        path = self.rootPath + "/" + clusterUUID + "/nginxcnf"
        if self.zk.exists(path):
            resultValue = self.DEFAULT_RETRY_POLICY(self.zk.get, path)
        return resultValue

    def lock_cluster_start_stop_action(self):
        lock_name = "cluster_start_stop"
        return self.__lock_base_action(lock_name)

    def unLock_cluster_start_stop_action(self, lock):
        self.__unLock_base_action(lock)

    '''
    @todo: currently, no used
    '''
    def unLock_aysnc_monitor_action(self, lock):
        self.__unLock_base_action(lock)

    def __lock_base_action(self, lock_name):
        clusterUUID = getClusterUUID()
        path = "%s/%s/lock/%s" % (self.rootPath, clusterUUID, lock_name)
        lock = self.zk.Lock(path, threading.current_thread())
        isLock = lock.acquire(True,1)
        return (isLock,lock)

    def __unLock_base_action(self, lock):
        if lock is not None:
            lock.release()

    def __return_children_to_list(self, path):
        self.zk.ensure_path(path)
        children = self.DEFAULT_RETRY_POLICY(self.zk.get_children, path)

        children_to_list = []
        if len(children) != 0:
            for i in range(len(children)):
                children_to_list.append(children[i])
        return children_to_list

    def __retrieve_special_path_prop(self,path):
        data = None

        if self.zk.exists(path):
            data,_ = self.DEFAULT_RETRY_POLICY(self.zk.get, path)

        resultValue = {}
        if data != None and data != '':
            resultValue = self.__format_data(data)

        return resultValue

    def __format_data(self, data):
        local_data = data.replace("'", "\"").replace("[u\"", "[\"").replace(" u\"", " \"")
        formatted_data = json.loads(local_data)
        return formatted_data


@zk_singleton
class Scheduler_ZkOpers(ZkOpers):
    """
        used for monitor
    """

    def __init__(self):
        '''
        Constructor
        '''
        ZkOpers.__init__(self)


@zk_singleton
class Requests_ZkOpers(ZkOpers):

    def __init__(self):
        '''
        Constructor
        '''
        ZkOpers.__init__(self)


@zk_singleton
class Common_ZkOpers(ZkOpers):

    def __init__(self):
        '''
        Constructor
        '''
        ZkOpers.__init__(self)
