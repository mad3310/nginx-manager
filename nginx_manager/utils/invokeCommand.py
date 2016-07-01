#!/usr/bin/env python
#-*- coding: utf-8 -*-

import subprocess

class InvokeCommand():
    
    def _runSysCmd(self,cmdStr):
        if cmdStr == "":
            return ("",0)
        p = subprocess.Popen(cmdStr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ret_str = p.stdout.read()
        retval = p.wait()
        return (ret_str.strip(),retval)

    def _runSysCmdnoWait(self,cmdStr):
        if cmdStr == "":
            return False
        try:
            p = subprocess.Popen(cmdStr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except Exception:
            return False
        if p.poll():
            return False
        else:
            return p    
   
if __name__ == "__main__":
    invokeCommand = InvokeCommand()
    sst_user_password = invokeCommand.runBootstrapScript()
    print sst_user_password
