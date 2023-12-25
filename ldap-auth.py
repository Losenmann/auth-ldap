#!/usr/bin/env python
import sys
sys.path.append('{}/lib'.format(sys.path[0]))
import os
import hashlib
import argparse
import configparser
from PIL import Image
from ldap3 import Server, Connection, ALL, core

parser = argparse.ArgumentParser(description="Home Assistant LDAP authentication via CLI")
parser.add_argument('-m', '--meta', action='store_true', help='Enable meta to output credentials to stdout')
parser.add_argument('-p', '--photo', action='store_true', help='Get and save photo')
args = parser.parse_args()

config = configparser.ConfigParser()
if os.path.exists("{}/.env.ini".format(sys.path[0])):
    config.read("{}/.env.ini".format(sys.path[0]))
else:
    print("# Missing configuration file:", ENVFILE)
    exit(1)

if 'username' not in os.environ and 'password' not in os.environ:
    print("# Username and password environment variables not set!")
    exit(1)

USER = os.environ['username']
PASS = os.environ['password']
SERVER = config['LDAP']['host']
USERDN = config['LDAP']['userdn'].format(USER)
ISLOCAL = config['LDAP']['ISLOCAL']

def main():
    if not args.meta:
        print("# Trying authentication for user [{}]".format(USER))

    auth = ldap()
    photo(auth[2])

    if args.meta:
        print("name=" + auth[0])
        print("group=" + auth[1])
        print("local_only=" + ISLOCAL)
        exit(0)
    else:
        print("# User [{}] successfully authenticated!".format(USER))
        exit(0)

def ldap():
    s = Server(SERVER, get_info=ALL)
    try:
        rtn = [None] * 3
        c = Connection(s, USERDN, password=PASS, auto_bind=True)

        """ Get user """
        user = c.search(config['LDAP']['basedn_user'], config['LDAP']['filter_user'], attributes=['givenName','jpegPhoto'])
        if user:
            rtn[0] = c.response[0].get('attributes', {}).get('givenName', '')[0]
            rtn[2] = c.response[0].get('attributes', {}).get('jpegPhoto', '')[0]
        else:
            print("# User [{}] is not found!".format(USER))
            exit(1)

        """ Get user group """
        group = c.search(config['LDAP']['basedn_group'], config['LDAP']['filter_group'], attributes=['cn'])
        if group:
            rtn[1] = c.response[0].get('attributes', {}).get('cn', '')[0]
        else:
            print("# User [{}] no access rights!".format(USER))
            exit(1)
        return rtn
    except core.exceptions.LDAPBindError as e:
        print(e)
        exit(1)

def photo(img):
    n = hashlib.md5(os.urandom(32)).hexdigest()
    os.makedirs("/config/image/{}".format(n), exist_ok=True)

    """ Saving the original image """
    f = open("/config/image/{}/original".format(n), "wb")
    f.write(img)
    f.close()

    """ Creating and saving a thumbnail """
    i = Image.open("/config/image/{}/original".format(n))
    wpercent = (512 / float(i.size[0]))
    hsize = int((float(i.size[1]) * float(wpercent)))
    i = i.resize((512, hsize), Image.Resampling.LANCZOS)
    i.save("/config/image/{}/512x512".format(n), "JPEG")

if __name__ == "__main__":
    main()
