'''
Created on Mar 13, 2015

@author: root
'''
import os
import subprocess

from utils.exceptions import NginxConfigurationException
from configuration.serverParser import ServerParser
from configuration.upstreamParser import UpstreamParser

class ConfigOpers(object):
    def __init__(self, base_conf_location):
        super(ConfigOpers, self).__init__()

        self.conf_path = base_conf_location
        self.nginx_conf_path = os.path.join(self.conf_path, 'nginx.conf')

        if not os.path.exists(self.nginx_conf_path):
            raise NginxConfigurationException('%s is not a valid nginx configuration root. nginx.conf file was not '
                                              'found at the specified location' % self.conf_path)

        self.sites_available = os.path.join(self.conf_path, 'sites-available')
        self.sites_enabled = os.path.join(self.conf_path, 'sites-enabled')
        
        self.upstream_file_path = os.path.join(self.sites_available, 'upstream.conf')

        if not os.path.exists(self.sites_available) or not os.path.exists(self.sites_enabled):
            raise NginxConfigurationException('Nginx configuration root does not contain a \'sites-available\' '
                                              'or \'sites-enabled\' directory')

        self.configuration = None

        self.nginx_binary_path = None
        self._find_nginx_exec()
        self.parser = ServerParser()
        
        self.upstream_parser = UpstreamParser()

    def load(self):
        """
        Loads all configuration files contained within {{conf_path}}/sites-available directory.

        File are loaded into a dictionary where keys are the names of the files and values are server dictionaries in
        format: {"enabled": true/false, "server": Server}
        """
        available_files = self._list_sites_available()
        enabled_link_realpaths = self._list_sites_enabled_link_realpaths()

        configuration = {}
        for available_file in available_files:
            file_path = os.path.join(self.sites_available, available_file)
            enabled = file_path in enabled_link_realpaths
            configuration[available_file] = self._read_config_file(file_path, enabled)

        enabled_files = self._list_sites_enabled_files()

        for enabled_file in enabled_files:
            file_path = os.path.join(self.sites_enabled, enabled_file)
            enabled = True
            configuration[enabled_file] = self._read_config_file(file_path, enabled)

        self.configuration = configuration

    def get_server_by_name(self, name):
        sites_enabled_path = os.path.join(self.sites_enabled, name)
        sites_available_path = os.path.join(self.sites_available, name)

        if self.configuration and name in self.configuration.keys():
            return self.configuration[name]
        elif os.path.exists(sites_available_path):
            enabled = sites_available_path in self._list_sites_enabled_link_realpaths()
            return self._read_config_file(sites_available_path, enabled=enabled)
        elif os.path.exists(sites_enabled_path) and \
                not os.path.islink(sites_enabled_path):
            return self._read_config_file(sites_enabled_path, enabled=True)
        else:
            raise NginxConfigurationException('Configuration file \'%s\' not found in sites-available or '
                                              'sites-enabled' % name)

    def save_server(self, server, name):
        file_path = os.path.join(self.sites_available, name)
        try:
            existing_server = self.get_server_by_name(name)
            enabled = existing_server['enabled']
        except NginxConfigurationException:
            enabled = False

        with open(file_path, 'w') as f:
            f.write(str(server))
            server_conf = {'enabled': enabled, 'server': server, 'conf_file': file_path}
            if self.configuration:
                self.configuration[name] = server_conf
            return server_conf

    def enable_server(self, name):
        server = self.get_server_by_name(name)
        if not server['enabled']:
            os.symlink(server['conf_file'], os.path.join(self.sites_enabled, name))
            server['enabled'] = True

    def disable_server(self, name):
        server = self.get_server_by_name(name)
        if server['enabled']:
            sites_enabled_link = os.path.join(self.sites_enabled, name)
            if not os.path.islink(sites_enabled_link):
                raise NginxConfigurationException('Server configuration file %s is not a link. In order to disable '
                                                  'server configuration in a file, the configuration should be placed'
                                                  ' inside the sites-available directory, with link being placed in '
                                                  'sites-enabled')
            os.unlink(sites_enabled_link)
            server['enabled'] = False
        else:
            raise NginxConfigurationException('Server is already disabled')
        
    def save_upstream(self, upstream):
        with open(self.upstream_file_path, 'w') as f:
            f.write(str(upstream))
            f.close()
        
    def get_server_from_upstream(self, upstream):
        if os.path.exists(self.upstream_file_path):
            return self._read_upstream_file(self.upstream_file_path, upstream)
        else:
            raise NginxConfigurationException('upstream \'%s\' not found in upstream.conf or ' % upstream)

    def reload(self):
        return subprocess.call([self.nginx_binary_path, '-s', 'reload'])
    
    def _read_upstream_file(self, file_path, upstream):
        with open(file_path) as f:
            return {'upstream': upstream, 'servers': self.upstream_parser.parse(f.read()),
                    'upstream_file': file_path}

    def _read_config_file(self, file_path, enabled):
        with open(file_path) as f:
#             return {'enabled': enabled, 'server': self.parser.parse(f.read()),
#                     'conf_file': file_path}
            return {'enabled': enabled, 'server': f.read(),
                    'conf_file': file_path}

    def _find_nginx_exec(self):
        try:
            #output = subprocess.Popen(['which', 'nginx'])
            _output = os.popen('which nginx')
            output = _output.read()
            self.nginx_binary_path = output.rstrip()
        except subprocess.CalledProcessError:
            pass

    def _list_sites_available(self):
        return [f for f in os.listdir(self.sites_available) if os.path.isfile(os.path.join(self.sites_available, f))]

    def _list_sites_enabled_link_realpaths(self):
        return [os.path.realpath(os.path.join(self.sites_enabled, f)) for f in os.listdir(self.sites_enabled)
                if os.path.islink(os.path.join(self.sites_enabled, f))]

    def _list_sites_enabled_files(self):
        return [f for f in os.listdir(self.sites_enabled)
                if os.path.isfile(os.path.join(self.sites_enabled, f))
                and not os.path.islink(os.path.join(self.sites_enabled, f))]
