#!/usr/bin/env python
import sys
sys.path.append('{}/lib'.format(sys.path[0]))
import os
import json
import argparse
import configparser
from ldap3 import Server, Connection, ALL, core

parser = argparse.ArgumentParser(description="Home Assistant LDAP authentication via CLI")
parser.add_argument('-m', '--meta', action='store_true', help='Enable meta to output credentials to stdout')
args = parser.parse_args()

ENVFILE = "{}/.env.ini".format(sys.path[0])
config = configparser.ConfigParser()
if os.path.exists(ENVFILE):
    config.read(ENVFILE)
else:
    print("# Missing configuration file:", ENVFILE)
    exit(1)

if 'username' not in os.environ and 'password' not in os.environ:
    print("# Username and password environment variables not set!")
    exit(1)

username = os.environ['username']
password = os.environ['password']

SERVER = config['LDAP']['host']
USERDN = config['LDAP']['userdn'].format(username)
BASEDN = config['LDAP']['basedn']
FILTER = config['LDAP']['filter'].format(username)
ATTRIB = config['LDAP']['attrib']
ISLOCAL = config['LDAP']['ISLOCAL']

def main():
    s = Server(SERVER, get_info=ALL)
    try:
        if not args.meta:
            print("# Trying authentication for user [{}]".format(username))

        c = Connection(s, USERDN, password=password, auto_bind=True)
        search = c.search(BASEDN, FILTER, attributes=ATTRIB)

        if search:
            if args.meta:
                print("name={}".format(username.capitalize()))
                print("group={}".format(json.loads(c.entries[0].entry_to_json())['attributes'][ATTRIB][0]))
                print("local_only={}".format(ISLOCAL))
                exit(0)
            else:
                print("# User [{}] successfully authenticated!".format(username))
                exit(0)
        else:
            if args.meta:
                exit(1)
            else:
                print("# User [{}] no access rights!".format(username))
                exit(1)
    except core.exceptions.LDAPBindError as e:
        print(e)
        exit(1)

if __name__ == "__main__":
    main()
