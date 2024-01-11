#!/usr/bin/env python
import sys
sys.path.append('{}/lib'.format(sys.path[0]))
import os
import json
import hashlib
import argparse
import configparser
from PIL import Image
from ldap3 import Server, Connection, SAFE_SYNC

parser = argparse.ArgumentParser(description="Home Assistant LDAP authentication via CLI")
parser.add_argument('-m', '--meta', action='store_true', help='Enable meta to output credentials to stdout')
parser.add_argument('-p', '--photo', action='store_true', help='Get and save photo')
parser.add_argument('-U', '--username', type=str, help='LDAP username')
parser.add_argument('-P', '--password', type=str, help='LDAP user password')
args = parser.parse_args()

config = configparser.ConfigParser()
if os.path.exists("{}/.env.ini".format(sys.path[0])):
    config.read("{}/.env.ini".format(sys.path[0]))
else:
    print("# Missing configuration file:", ENVFILE)
    exit(1)

if args.username and args.password:
    USER=args.username
    PASS=args.password
else:
    if 'username' in os.environ and 'password' in os.environ:
        USER = os.environ['username']
        PASS = os.environ['password']
    else:
        print("# Username and password environment variables not set!")
        exit(1)

SERVER = config['LDAP']['host']
USERDN = config['LDAP']['userdn'].format(USER)
BASEDN = config['LDAP']['basedn']
FILTER = config['LDAP']['filter'].format(USER)
ISACTIVE = config['LDAP']['isactive']
ISLOCAL = config['LDAP']['islocal']

def main():
#    person()
    if not args.meta:
        print("# Trying authentication for user [{}]".format(USER))

    auth = ldap()

    if args.photo:
        photo(auth[2])

    if args.meta:
        print("name=" + auth[0])
        print("is_active=" + ISACTIVE)
        print("group=" + auth[1])
        print("local_only=" + ISLOCAL)
        exit(0)
    else:
        print("# User [{}] successfully authenticated!".format(USER))
        exit(0)

def ldap():
    s = Server(SERVER)
    try:
        rtn = [None] * 4
        c = Connection(s, USERDN, PASS, client_strategy=SAFE_SYNC, auto_bind=True)
        _, _, res, _ = c.search(BASEDN, FILTER, attributes=["uid","memberof","displayName","jpegPhoto"])

        if res[0].get('attributes').get('uid'):
            rtn[0] = res[0].get('attributes').get('uid')[0]
        else:
            print("# User [{}] is not found!".format(USER))
            exit(1)

        if res[0].get('attributes').get('memberOf'):
            for i in res[0].get('attributes').get('memberOf'):
                match i[:i.find('cn=homeassistant')+16]:
                    case 'cn=system-users,cn=homeassistant' | 'cn=homeassistant':
                        rtn[1] = 'system-users'
                    case 'cn=system-admin,cn=homeassistant':
                        rtn[1] = 'system-admin'
                        break
        else:
            print("# User [{}] no access rights!".format(USER))
            exit(1)

        if res[0].get('attributes').get('displayName'):
            rtn[2] = res[0].get('attributes').get('displayName')
        else:
            rtn[2] = res[0].get('attributes').get('uid')[0]

        if res[0].get('attributes').get('jpegPhoto'):
            rtn[3] = res[0].get('attributes').get('jpegPhoto')[0]

        return rtn
    except core.exceptions.LDAPBindError as e:
        print(e)
        exit(1)

def photo(img):
#    n = hashlib.md5(os.urandom(32)).hexdigest()
    n = "56592769585fa1a7339a84fcee38afab"
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

def person(i=None):
    if i is None:
        i = "/api/image/serve/" + hashlib.md5(os.urandom(32)).hexdigest() + "/512x512"
    p = {"id": "usertest","name":"test","user_id":"","device_trackers":[],"user_id":"null","picture":i}
    print(p)
################
#    async def async_create_person(hass, name, *, user_id=None, device_trackers=None):
#        """Create a new person."""
#        await hass.data[DOMAIN][1].async_create_item(
#            {
#                ATTR_NAME: "usertestq",
#                ATTR_USER_ID: "usertest1",
#                CONF_DEVICE_TRACKERS: device_trackers or [],
#            }
#        )

#    with open('/config/advanced/module/data.json', 'r+') as f:
#        d = json.load(f)
#        d['data']['items'].append(p)
#        f.seek(0)
#        json.dump(d, f, indent=4)
#        f.truncate()

if __name__ == "__main__":
    main()
