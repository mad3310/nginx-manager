'''
Created on Mar 15, 2015

@author: root
'''


class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
