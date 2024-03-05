#!/usr/bin/env python
import sys
import os
import json
import hashlib
import argparse
import configparser
from PIL import Image
try:
    from ldap3 import Server, Connection, core, ALL
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'ldap3'])
    from ldap3 import Server, Connection, core, ALL

parser = argparse.ArgumentParser(description="Home Assistant LDAP authentication via CLI")
parser.add_argument('-m', '--meta', action='store_true', help='Enable meta to output credentials to stdout')
parser.add_argument('-p', '--photo', action='store_true', help='Get and save photo')
parser.add_argument('-U', '--username', type=str, help='LDAP username')
parser.add_argument('-P', '--password', type=str, help='LDAP user password')
parser.add_argument('-s', '--server', type=str, help='Set LDAP server')
parser.add_argument('-u', '--userdn', type=str, help='Set USER DN')
parser.add_argument('-b', '--basedn', type=str, help='Set BASE DN')
parser.add_argument('-f', '--filter', type=str, help='Set FILTER')
parser.add_argument('-a', '--attrib', action='append', help='Set an array of attributes')
parser.add_argument('-i', '--active', action='store_false', help='Deactivate user account')
parser.add_argument('-l', '--local', action='store_true', help='The user can only login from the local network if the key is passed')
args = parser.parse_args()

data = [None] * 9
if args.username and args.password:
    data[0]=args.username
    data[1]=args.password
else:
    if 'username' in os.environ and 'password' in os.environ:
        data[0] = os.environ['username']
        data[1] = os.environ['password']
    else:
        print("# Username or password environment variables not set!")
        exit(1)

if os.path.exists("{}/.env.ini".format(sys.path[0])):
    config = configparser.ConfigParser()
    config.read("{}/.env.ini".format(sys.path[0]))

if args.server:
    data[2] = args.server
else:
    data[2] = config['LDAP']['server']
if args.userdn:
    data[3] = args.userdn.format(data[0])
else:
    data[3] = config['LDAP']['userdn'].format(data[0])
if args.basedn:
    data[4] = args.basedn
else:
    data[4] = config['LDAP']['basedn']
if args.filter:
    data[5] = args.filter.format(data[0])
else:
    data[5] = config['LDAP']['filter'].format(data[0])
if args.attrib:
    data[6] = args.attrib
else:
    data[6] = config['LDAP']['attrib']
if args.active != "":
    data[7] = args.active
else:
    data[7] = config['LDAP']['active']
if args.local != "":
    data[8] = args.local
else:
    data[8] = config['LDAP']['local']

def main():
#    person()
    if not args.meta:
        print("# Trying authentication for user [{}]".format(data[0]))

    auth = ldap(data)

    if args.photo and auth[2]:
        photo(auth[2])

    if args.meta:
        print("name=" + auth[0])
        print("is_active=" + str(data[7]))
        print("group=" + auth[1])
        print("local_only=" + str(data[8]))
        exit(0)
    else:
        print("# User [{}] successfully authenticated!".format(data[0]))
        exit(0)
    exit(0)

def ldap(data):
    s = Server(data[2], get_info=ALL)
    try:
        rtn = [None] * 3
        c = Connection(s, data[3], password=data[1], auto_bind=True)

        if c.search(data[4], data[5], attributes=data[6]):

            """ Get user """
            if len(c.response[0].get('attributes', {}).get('givenName', '')) > 0:
                rtn[0] = c.response[0].get('attributes', {}).get('givenName', '')[0]
            else:
                rtn[0] = data[0]

            """ Get user group """
            if len(c.response[0].get('attributes', {}).get('memberof', '')) > 0:
                for i in c.response[0].get('attributes', {}).get('memberof', ''):
                    if i.find('cn=homeassistant') >= 0:
                        match i.split(",")[0].replace("cn=",""):
                            case "homeassistant":
                                rtn[1] = "system-users"
                            case "system-users":
                                rtn[1] = "system-users"
                            case "system-admin":
                                rtn[1] = "system-admin"
                                break
                            case _:
                                rtn[1] = "system-users"
            else:
                print("# The user [{}] does not have enough rights!".format(data[0]))
                exit(1)

            """ Get user photo """
            if len(c.response[0].get('attributes', {}).get('jpegPhoto', '')) > 0:
                rtn[2] = c.response[0].get('attributes', {}).get('jpegPhoto', '')[0]
        else:
            print("# User [{}] is not found!".format(data[0]))
            exit(1)
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
    async def async_create_person(hass, name, *, user_id=None, device_trackers=None):
        """Create a new person."""
        await hass.data[DOMAIN][1].async_create_item(
            {
                ATTR_NAME: "usertestq",
                ATTR_USER_ID: "usertest1",
                CONF_DEVICE_TRACKERS: device_trackers or [],
            }
        )

#    with open('/config/advanced/module/data.json', 'r+') as f:
#        d = json.load(f)
#        d['data']['items'].append(p)
#        f.seek(0)
#        json.dump(d, f, indent=4)
#        f.truncate()

if __name__ == "__main__":
    main()
