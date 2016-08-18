'''
Created on Mar 13, 2015

@author: root
'''
import os
from utils.invokeCommand import InvokeCommand
from tornado.options import options
from utils import retrieve_node_name
from common.abstractOpers import AbstractOpers
from zk.zkOpers import Common_ZkOpers
from utils.exceptions import UserVisiableException
from utils import getClusterUUID, set_file_data
from utils.configFileOpers import ConfigFileOpers
from configuration.configOpers import ConfigOpers
from configuration.upstream import UpStream
from configuration.server import Server
from configuration.location import Location
from common.operType import OperType


class NodeOpers(AbstractOpers):
    '''
    classdocs
    '''
    invokeCommand = InvokeCommand()
    confOpers = ConfigFileOpers()
    base_config_path = '/etc/nginx/'
    man = ConfigOpers(base_config_path)

    def __init__(self):
        '''
        Constructor
        '''

    def create(self, params):
        if params == {} or params is None:
            raise UserVisiableException("please set the componentNode info!")

        dataNodeInternalPort = params.get('dataNodeInternalPort')
        if dataNodeInternalPort is not None:
            raise UserVisiableException("no need to set the dataNodeInternalPort param!")

        zkOper = Common_ZkOpers()

        local_uuid = getClusterUUID()
        existCluster = zkOper.existCluster(local_uuid)
        if not existCluster:
            raise UserVisiableException("sync componentCluster info error! please check if sync uuid is right!")

        params.setdefault("dataNodeInternalPort", options.port)
        dataNodeExternalPort = params.get('dataNodeExternalPort')
        if dataNodeExternalPort is None or '' == dataNodeExternalPort:
            params.setdefault("dataNodeExternalPort", options.port)

        self.confOpers.setValue(options.data_node_property, params)
        dataNodeProprs = self.confOpers.getValue(options.data_node_property)
        zkOper.writeDataNodeInfo(local_uuid, dataNodeProprs)

        result = {}
        result.setdefault("message", "Configuration on this componentNode has been done successfully")
        return result

    def start(self):
        _, ret_val = self.invokeCommand._runSysCmd(options.start_nginx)

        result = {}
        if ret_val != 0:
            result.setdefault("message", "start nginx failed")
        else:
            container_name =  retrieve_node_name()
            zkOper = Common_ZkOpers()
            zkOper.write_started_node(container_name)
            result.setdefault("message", "start nginx successfully")

        return result

    def stop(self):
        _, ret_val = self.invokeCommand._runSysCmd(options.stop_nginx)

        result = {}
        if ret_val != 0:
            result.setdefault("message", "stop nginx failed")
        else:
            container_name = retrieve_node_name()
            zkOper = Common_ZkOpers()
            zkOper.remove_started_node(container_name)
            result.setdefault("message", "stop nginx successfully")

        return result

    def reload(self):
        _, ret_val = self.invokeCommand._runSysCmd(options.reload_nginx)

        result = {}
        if ret_val != 0:
            result.setdefault("message", "reload nginx failed")
        else:
            result.setdefault("message", "reload nginx successfully")
            container_name =  retrieve_node_name()
            zkOper = Common_ZkOpers()
            zkOper.write_started_node(container_name)
        return result

    def config(self, params):

        _upstream_name = params.get('upstreamName')
        _servers_ports = params.get('serverPorts')
        _cluster = params.get('containerClusterName')
        server_list = _servers_ports.split(',') if ',' in _servers_ports else [_servers_ports]
        upstream = UpStream(_upstream_name, server_list)
        self.man.save_upstream(upstream)
        self.man.enable_server( os.path.basename(self.man.upstream_file_path) )

        server = self.__get_server(_upstream_name)
        filename = '%ssites-available/%s.conf' % (self.base_config_path, _cluster)
        set_file_data(filename, str(server), 'w')
        self.man.enable_server('%s.conf' % _cluster)
        self.invokeCommand._runSysCmd(options.reload_nginx)

        result = {}
        result.setdefault("message", "node config upstream successfully")
        return result

    def __get_server(self, upstream_name):

        server = Server(port=8001, server_names=['webportal-app'],
                        params={'error_page': '500 502 503 504  /50x.html'} )

        location = Location('/', params={'proxy_pass': 'http://%s' % upstream_name,
                                         'proxy_set_header': 'Host rds.et.letv.com',
                                         'proxy_redirect': 'off',
                                         'index':'index.html index.htm'})

        server.add_location(location=location)

        location = Location('= /50x.html', params={'root': '/usr/share/nginx/html'})
        server.add_location(location=location)

        return server

    def enable(self):
        files = os.listdir(self.man.sites_available)

        for _file in files:
            self.man.enable_server(_file)

        self.invokeCommand._runSysCmd(options.reload_nginx)

    def disable(self):

        files = os.listdir(self.man.sites_available)

        for _file in files:
            self.man.disable_server(_file)

        self.invokeCommand._runSysCmd(options.reload_nginx)
