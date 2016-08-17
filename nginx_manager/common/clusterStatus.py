'''
Created on Mar 15, 2015

@author: root
'''
from common.enum import Enum
_cluster_status = ['STARTED', 'STOP', 'STARTED_PART']

ClusterStatus = Enum(_cluster_status)
