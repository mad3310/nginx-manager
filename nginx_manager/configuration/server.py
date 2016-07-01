'''
Created on Mar 31, 2015

@author: root
'''

import logging

class Server(object):
    def __init__(self, port, server_names, params):
        super(Server, self).__init__()
        self.port = port
        self.server_names = server_names
        self.locations = []
        self.params = params

    def add_location(self, location):
        logging.info('server add location:%s' % str(location))
        logging.info('location type :%s' % type(location))
        self.locations.append(location)

    def __str__(self):
        rows = ['server{', '    listen %s;' % self.port]
        if self.server_names:
            rows.append('    server_name %s;' % ' '.join(self.server_names))
        if 'root' in self.params:
            rows.append('    root %s;' % self.params.pop('root'))

        for location in self.locations:
            rows.append(str(location))

        for k, v in self.params.items():
            rows.append('    %s %s;' % (k, v))

        rows.append('}')
        return '\n'.join(rows)