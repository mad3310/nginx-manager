# -*- coding: utf-8 -*-

from base import APIHandler
from tornado_letv.tornado_basic_auth import require_basic_auth
from tornado.web import asynchronous
from componentCluster.clusterOpers import ClusterOpers
from common.clusterStatus import ClusterStatus

'''
Created on 2013-7-21

@author: asus
'''


class Sync_Handler(APIHandler):

    cluster_opers = ClusterOpers()

    def post(self):
        '''
        function: sync cluster info from zk to local properties file
        url example: curl -d "clusterUUID=***" "http://localhost:8888/cluster/sync"
        '''
        requestParam = self.get_all_arguments()
        self.cluster_opers.syncExistedCluster(requestParam)

        result = {}
        result.setdefault("message", "sync nginx to local successful!")
        self.finish(result)


@require_basic_auth
class Cluster_Handler(APIHandler):

    cluster_opers = ClusterOpers()

    def post(self):
        '''
        function: create cluster and add the first nginx node to cluster, info record to zk
        url example: curl --user root:root -d "clusterName=nginx_cluster&dataNodeIp=192.168.116.129&dataNodeName=nginx_cluster_node_1[&dataNodeExternalPort=**]" "http://localhost:8888/cluster"
        '''
        requestParam = self.get_all_arguments()
        clusterUUID = self.cluster_opers.create(requestParam)

        result, data = {}, {}
        data.setdefault('uuid', clusterUUID)
        result.setdefault('data', data)
        result.setdefault("message", "create cluster successfully!")
        self.finish(result)

    def get(self):
        '''
        function: retrieve the cluster status
        url example: curl --user root:root "http://localhost:8888/cluster"
        '''
        cluster_status = self.cluster_opers.retrieve_cluster_started_status()

        result = {}
        result.setdefault('data', {'status': cluster_status})
        if ClusterStatus.STARTED == cluster_status:
            result.setdefault("message", "cluster is available, cluster status is started!")
        elif ClusterStatus.STARTED_PART == cluster_status:
            result.setdefault("message", "cluster is available, but part of nodes are not started!")
        else:
            result.setdefault("message", "cluster is not available, cluster status is stopped!")

        self.finish(result)


@require_basic_auth
class Cluster_Start_Handler(APIHandler):

    cluster_opers = ClusterOpers()

    @asynchronous
    def post(self):
        '''
        function: start cluster
        url example: curl --user root:root -d "" "http://localhost:8888/cluster/start"
        '''

        result = self.cluster_opers.start()
        self.finish(result)


@require_basic_auth
class Cluster_Stop_Handler(APIHandler):

    cluster_opers = ClusterOpers()

    @asynchronous
    def post(self):
        '''
        function: stop cluster
        url example: curl --user root:root -d "" "http://localhost:8888/cluster/stop"
        '''
        result = self.cluster_opers.stop()
        self.finish(result)


@require_basic_auth
class Cluster_Reload_Handler(APIHandler):

    cluster_opers = ClusterOpers()

    @asynchronous
    def post(self):
        '''
        function: reload cluster
        url example: curl --user root:root -d "" "http://localhost:8888/cluster/reload"
        '''
        result = self.cluster_opers.reload()
        self.finish(result)


@require_basic_auth
class Cluster_Config_Handler(APIHandler):

    cluster_opers = ClusterOpers()

    @asynchronous
    def post(self):
        '''
        function: config cluster, currently, only for upstream
        url example: curl --user root:root -d "upstreamName=newupstream&serverPorts=10.200.84.21:3333,10.200.84.22:3333,10.200.84.23:3333" "http://localhost:8888/cluster/config"
        '''
        requestParam = self.get_all_arguments()
        result = self.cluster_opers.config(requestParam)
        self.finish(result)


@require_basic_auth
class Cluster_Enable_Handler(APIHandler):

    cluster_opers = ClusterOpers()

    def post(self):
        '''
        function: enable proxy cluster
        url example: curl --user root:root -d "" "http://localhost:8888/cluster/enable"
        '''

        result = self.cluster_opers.enable()
        self.finish(result)


@require_basic_auth
class Cluster_Disable_Handler(APIHandler):

    cluster_opers = ClusterOpers()

    def post(self):
        '''
        function: enable proxy cluster
        url example: curl --user root:root -d "" "http://localhost:8888/cluster/enable"
        '''

        result = self.cluster_opers.disable()
        self.finish(result)
