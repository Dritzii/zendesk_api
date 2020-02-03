import wmi
from socket import *
import sys
import os
import subprocess
import re
import requests


class machine_config():
    def __init__(self,ip=None,user=None,password=None):
        self.ip = ip
        self.user = user
        self.password = password
        try:
            print("Establishing connection to %s" %self.ip)
            self.connection = wmi.WMI(self.ip, user=self.user, password=self.password)
            print("Connection established")
        except Exception as e:
            print( "Your Username and Password of "+ getfqdn(self.ip)+" are wrong.")
            print(e,sys.stderr)

    def getdetails(self):
        print(self.ip + self.user + self.password)

    
    def get_disk(self):
        conn = self.connection
        for disk in conn.Win32_LogicalDisk():
            if disk.size != None:
                print(disk.Caption, "is {0:.2f}% free".format(
                100*float(disk.FreeSpace)/float(disk.Size)))

    def get_process(self):
        conn = self.connection
        for class_name in conn.classes:
            if 'Process' in class_name:
                print(class_name)

    def get_query(self):
        conn = self.connection
        for group in conn.Win32_Group():
            print(group.Caption)
            for user in group.associators(wmi_result_class="Win32_UserAccount"):
                print(" [+]", user.Caption)

    def get_methods(self):
        conn = self.connection.Win32_Process.methods.keys()
        print(conn)
    
    def get_properties(self):
        conn = self.connection.Win32_Process.properties.keys()
        print(conn)








if __name__ == "__main__":
    machine_config().get_properties()