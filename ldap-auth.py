#!/usr/bin/env python
import sys
sys.path.append( '/config/module/lib' )
import os
import argparse
import configparser
from ldap3 import Server, Connection, ALL, core

parser = argparse.ArgumentParser(description="Home Assistant LDAP authentication via CLI")
parser.add_argument('-m', '--meta', action='store_true', help='Enable meta to output credentials to stdout')
args = parser.parse_args()

config = configparser.ConfigParser()
config.read("/config/module/.env.ini")

if 'username' not in os.environ and 'password' not in os.environ:
    print("Need username and password environment variables!")
    exit(1)

config = configparser.ConfigParser()
config.read("/config/module/.env.ini")

def main():
    username = os.environ['username']
    password = os.environ['password']
    SERVER = config['LDAP']['host']
    USERDN = config['LDAP']['userdn'].format(os.environ['username'])
    BASEDN = config['LDAP']['basedn']
    FILTER = config['LDAP']['filter'].format(os.environ['username'])
    TIMEOUT = 3
    #SCOPE = "base"
    #ATTRS = ""

    server = Server(SERVER, get_info=ALL)
    try:
        conn = Connection(server, USERDN, password=username, auto_bind=True)
        if not args.meta:
            print("whoami: {}".format(conn.extend.standard.who_am_i()))
        search = conn.search(BASEDN, FILTER)
        if search:
            if args.meta:
                print("name = {}".format(username.capitalize()),"\ngroup = system-users")
            print("Success LDAP: Search", conn.entries)
            exit(0)
        else:
            print("Error LDAP: no access rights")
            exit(1)
    except core.exceptions.LDAPBindError as e:
        print(e)
        exit(1)

if __name__ == "__main__":
    main()
