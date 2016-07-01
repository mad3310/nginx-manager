'''
Created on Mar 14, 2015

@author: root
'''
from abc import abstractmethod

class AbstractOpers(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    @abstractmethod   
    def create(self):
        raise NotImplementedError, "Cannot call abstract method"
        
    @abstractmethod   
    def start(self):
        raise NotImplementedError, "Cannot call abstract method"
    
    @abstractmethod    
    def stop(self):
        raise NotImplementedError, "Cannot call abstract method"
    
    @abstractmethod    
    def reload(self):
        raise NotImplementedError, "Cannot call abstract method"