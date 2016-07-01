#!/usr/bin/env python
#-*- coding: utf-8 -*-


from handlers.admin import AdminConf, AdminUser, AdminReset
from handlers.cluster import *  
from handlers.node import *
handlers = [
            (r"/admin/conf", AdminConf),
            (r"/admin/user", AdminUser),
            (r"/admin/reset", AdminReset),
            
            (r"/cluster", Cluster_Handler),
            (r"/cluster/sync", Sync_Handler),

            (r"/cluster/start", Cluster_Start_Handler),
            (r"/cluster/reload", Cluster_Reload_Handler),
            (r"/cluster/stop", Cluster_Stop_Handler),
            (r"/cluster/config", Cluster_Config_Handler),
            (r"/cluster/enable",  Cluster_Enable_Handler),
            (r"/cluster/disable",  Cluster_Disable_Handler),
            
            (r"/cluster/node", Node_Handler),
            (r"/cluster/node/enable", Node_Enable_Handler),
            (r"/cluster/node/disable", Node_Disable_Handler),
            (r"/cluster/node/start", Node_Start_Handler),
            (r"/cluster/node/stop", Node_Stop_Handler),
            (r"/cluster/node/reload", Node_Reload_Handler),
            (r"/cluster/node/config", Node_Config_Handler),
]
