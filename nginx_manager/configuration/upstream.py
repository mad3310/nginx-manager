'''
Created on Mar 31, 2015

@author: root
'''

class UpStream(object):
    def __init__(self, upstream, servers):
        super(UpStream, self).__init__()
        self.upstream = upstream
        self.servers = servers
    
    def __str__(self):
        rows = ['upstream %s{' % self.upstream]
        for server in self.servers:
            rows.append('    server %s;' % (server))
        rows.append('}')
        return '\n'.join(rows)
    
    def add_server(self, server):
        self.servers.append(server)