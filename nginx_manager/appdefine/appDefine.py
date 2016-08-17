#-*- coding: utf-8 -*-
import os

from tornado.options import define

join=os.path.join
dirname=os.path.dirname

base_dir=os.path.abspath(dirname(dirname(__file__)))

define('port', default=8888, type=int, help='app listen port')
define('debug', default=False, type=bool, help='is debuging?')
define('sitename', default="nginx manager", help='site name')
define('domain', default="letv.com", help='domain name')

define('send_email_switch', default=True, type=bool, help='the flag of if send error email')
define('admins', default=("zhoubingzheng <zhoubingzheng@letv.com>", "dengliangju <dengliangju@le.com>",
                          "liujinliu <liujinliu@le.com>", "wangyiyang <wangyiyang@le.com>"), help='admin email address')
define('smtp_host', default="mail.letv.com", help='smtp host')
define('smtp_port', default=587, help='smtp port')
define('smtp_user', default="mcluster", help='smtp user')
define('smtp_password', default="Mcl_20140903!", help='smtp password')
define('smtp_from_address', default='mcluster@letv.com', help='smtp from address')
define('smtp_duration', default=10000, type=int, help='smtp duration')
define('smtp_tls', default=False, type=bool, help='smtp tls')

define("nginx_manager_property", default=join(base_dir, "config", "nginx_manager.property"), help="nginx manager config file")
define("data_node_property", default=join(base_dir, "config", "dataNode.property"), help="data componentNode config file")
define("cluster_property", default=join(base_dir, "config", "cluster.property"), help="cluster config file")
define("nginx_service_cnf", default="/etc/nginx/nginx.conf", help="nginx configuration file")
define("nginx_extend_cnf_dir", default="/etc/nginx/conf.d/", help="extended directory")
define("base_dir", default=base_dir, help="project base dir")

define("alarm_serious", default="tel:sms:email", help="alarm level is serious")
define("alarm_general", default="sms:email", help="alarm level is general")
define("alarm_nothing", default="nothing", help="no alarm")

define("start_nginx", default="service nginx start", help="start nginx")
define("stop_nginx", default="service nginx stop", help="stop nginx")
define("reload_nginx", default="service nginx reload", help="reload nginx")
