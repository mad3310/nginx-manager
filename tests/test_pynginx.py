import unittest
from configuration.configOpers import ConfigOpers
from configuration.server import Server
from configuration.location import Location
from configuration.serverParser import ServerParser
from configuration.upstream import UpStream
from utils.exceptions import NginxConfigurationException
import os.path
from _pytest.monkeypatch import monkeypatch as mp
import subprocess


class NginxConfigurationTest(unittest.TestCase):
    test_files_dir = os.path.join(os.path.dirname(__file__), 'files')

    def setUp(self):
        self.monkeypatch = mp()

    def tearDown(self):
        self.monkeypatch.undo()

    def _mock_sites_directories(self, manager):
        self.monkeypatch.setattr(manager, 'sites_available', os.path.join(self.test_files_dir, 'available'))
        self.monkeypatch.setattr(manager, 'sites_enabled', os.path.join(self.test_files_dir, 'enabled'))
        self.monkeypatch.setattr(manager, 'upstream_file_path', os.path.join(self.test_files_dir, 'enabled','upstream.conf'))

    def _make_manager_init_pass(self):
        def mockreturn_nginx_path(path):
            return True

        def mockreturn_nginx_binary(subprocess):
            return '/argh/mrmr/giberish'

        self.monkeypatch.setattr(os.path, 'exists', mockreturn_nginx_path)
        self.monkeypatch.setattr(subprocess, 'Popen', mockreturn_nginx_binary)

    def test_fail_if_no_configuration_file(self):
        def mockreturn_nginx_path(path):
            return False

        self.monkeypatch.setattr(os.path, 'exists', mockreturn_nginx_path)

        self.assertRaises(NginxConfigurationException, ConfigOpers, base_conf_location='/etc/nginx/')

    def test_config_file_exists(self):
        self._make_manager_init_pass()

        man = ConfigOpers('/etc/nginx/')
        self.assertEqual('/etc/nginx/', man.conf_path)

    def test_server_to_string(self):
        server = Server(port=1231, server_names=['example.com', 'example.net'],
                        params={'client_max_body_size': '20M',
                                'root': '/opt/mysite/',
                                'error_page': '500 502 /media/500.html'})

        location = Location('/media', params={'proxy_pass_header': 'Server',
                                              'proxy_set_header': 'Host $http_host',
                                              'proxy_redirect': 'off'})
        server.add_location(location=location)

        server_str = str(server)
        self.assertEqual(True, server_str.find('location /media{')>0)
        self.assertEqual(True, server_str.find('client_max_body_size 20M;')>0)
        self.assertEqual(True, server_str.find('root /opt/mysite/;')>0)
        self.assertEqual(True, server_str.find('error_page 500 502 /media/500.html;')>0)
        self.assertEqual(True, server_str.find('1231;')>0)
        self.assertEqual(True, server_str.find('server_name example.com example.net;')>0)
        
    def test_location_to_string(self):
        location = Location('/media', params={'proxy_pass_header': 'Server',
                                         'proxy_set_header': 'Host $http_host',
                                         'proxy_redirect': 'off'})

        location_str = str(location)
        self.assertEqual(True, location_str.find('proxy_pass_header Server;')>0)
        self.assertEqual(True, location_str.find('proxy_set_header Host $http_host;')>0)
        self.assertEqual(True, location_str.find('proxy_redirect off;')>0)
        self.assertEqual(True, location_str.find('location /media{')>=0)

    def test_parser(self):
        with open(os.path.join(self.test_files_dir, 'available', 'server')) as f:
            parser = ServerParser()
            conf = f.read()
            server = parser.parse(conf)
            self.assertEqual(80, server.port)
            self.assertEqual(True, server.server_names[0].find('example.com')>=0)
#             self.assertIn('example.com', server.server_names)
            self.assertEqual(6, len(server.locations))
            location = [x for x in server.locations if x.location == '/robots.txt'][0]
            
            self.assertEqual(True, location.params.get('allow')=='all')
#             self.assertIn('allow', location.params)
            self.assertEqual(True, location.params.get('alias').find('/opt/example/robots.txt')==0)
#             self.assertIn('/opt/example/robots.txt', location.params.get('alias'))


    def test_write_and_read_upstream(self):
        try:
            self._make_manager_init_pass()
            man = ConfigOpers('/etc/nginx/')
            
            self._mock_sites_directories(man)
            
            new_server = '10.200.91.158:33333'
            
            servers_list = [
                "10.200.91.156:33333",
                "10.200.91.157:33333"
            ]
            upstream = UpStream('newupstream',servers_list)
            
            upstream.add_server(new_server)
            
            self.assertEqual(True, str(upstream).find(new_server)>=0)
        
            man.save_upstream(upstream)
            
            upstream_dict = man.get_server_from_upstream('newupstream')
            
            self.assertEqual('newupstream', upstream_dict.get('upstream'))
            
            upstream = upstream_dict.get('servers')
            self.assertEqual('10.200.91.156:33333', upstream.servers[0])
            self.assertEqual('10.200.91.157:33333', upstream.servers[1])
            self.assertEqual('10.200.91.158:33333', upstream.servers[2])
        finally:
            if os.path.exists(man.upstream_file_path):
                os.remove(man.upstream_file_path)
        
        

    def test_get_server_by_name(self):
        self._make_manager_init_pass()
        man = ConfigOpers('/etc/nginx')

        #Revert the monkeypatch making os.path.exists always return True
        self.monkeypatch.undo()
        self._mock_sites_directories(man)

        server = man.get_server_by_name(name='server')
        self.assertFalse(server['enabled'])

        server = man.get_server_by_name(name='server2')
        self.assertTrue(server['enabled'])

        self.assertRaises(NginxConfigurationException, man.get_server_by_name, name='nonexists')

        man.load()
        server = man.get_server_by_name(name='server')
        self.assertFalse(server['enabled'])
        self.assertEqual(80, server['server'].port)

    def test_save_enable_disable_server(self):

        def mockreturn_realpaths():
            return [os.path.join(self.test_files_dir, 'available', 'new_server')]

        try:
            server = Server(port=80, server_names=['example2.com'], params={'root': '/opt/example2/'})
            self._make_manager_init_pass()
            man = ConfigOpers('/etc/nginx')
            self.monkeypatch.undo()
            self._mock_sites_directories(man)
            man.save_server(server, 'new_server')

            new_file_path = os.path.join(man.sites_available, 'new_server')
            new_file_link_path = os.path.join(man.sites_enabled, 'new_server')
            self.assertTrue(os.path.exists(new_file_path))

            #make the parser pass on this new file
            parser = ServerParser()
            with open(new_file_path) as f:
                parser.parse(f.read())

            self.assertFalse(os.path.exists(new_file_link_path))
            man.enable_server('new_server')
            self.assertTrue(os.path.exists(new_file_link_path))
            self.assertTrue(os.path.islink(new_file_link_path))
            self.monkeypatch.setattr(man, '_list_sites_enabled_link_realpaths', mockreturn_realpaths)
            man.disable_server('new_server')
            self.assertFalse(os.path.exists(new_file_link_path))

        finally:
            if os.path.exists(new_file_link_path):
                os.unlink(new_file_link_path)
            if os.path.exists(new_file_path):
                os.remove(new_file_path)

    def test_load_configuration(self):

        def mockreturn_realpaths():
            return [os.path.join(self.test_files_dir, 'available', 'server')]

        self._make_manager_init_pass()
        man = ConfigOpers('/etc/nginx/')

        self._mock_sites_directories(man)
        man.load()
        self.assertNotEqual(None, man.configuration)
        self.assertEqual(False, man.configuration['server']['enabled'])
        self.assertEqual(80, man.configuration['server']['server'].port)

        self.monkeypatch.setattr(man, '_list_sites_enabled_link_realpaths', mockreturn_realpaths)
        man.load()
        self.assertEqual(True, man.configuration['server']['enabled'])

        self.assertEqual(2, len(man.configuration.keys()))
        self.assertEqual(True, man.configuration['server2']['enabled'])
    
    
    

        
