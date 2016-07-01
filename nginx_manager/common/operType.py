'''
Created on Mar 15, 2015

@author: root
'''
from common.enum import Enum
_oper_types = ['start', 'stop', 'reload', 'config', 'enable', 'disable']

OperType = Enum(_oper_types)