'''
Created on Mar 31, 2015

@author: root
'''
class Location(object):
    def __init__(self, location, params):
        super(Location, self).__init__()
        self.location = location
        self.params = params

    def __str__(self):
        rows = ['location %s {' % self.location]
        for k, v in self.params.items():
            rows.append('    %s %s;' % (k, v))
        rows.append('}')
        return '\n'.join(rows)