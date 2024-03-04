#!/usr/bin/env python
import sys
sys.path.append( '/config/module/lib' )
import os
import argparse
import configparser
import radius

parser = argparse.ArgumentParser(description="Home Assistant RADIUS authentication via CLI")
parser.add_argument('-m', '--meta', action='store_true', help='Enable meta to output credentials to stdout')
args = parser.parse_args()

config = configparser.ConfigParser()
config.read("/config/module/.env.ini")

radius_client = radius.Radius(config['RADIUS']['client'],host=config['RADIUS']['host'],port=int(config['RADIUS']['port']))

def main():
    username = os.environ['username']
    password = os.environ['password']

    try:
        if not args.meta:
            print("# Trying authentication for user [{}]".format(username))
        result = radius_client.authenticate(username, password)
    except:
        print("# Error during authentication!")
        exit(1)

    if result:
        if args.meta:
            print("name={}".format(username.capitalize()))
            print("group=system-users")
            print("local_only=true")
        else:
            print("# User [{}] successfully authenticated!".format(username))
        exit(0)
    else:
        print("# Authentication failed for user [{}].".format(username))
        exit(1)

if __name__ == "__main__":
    main()
