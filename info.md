# Home Assistant Auth LDAP
Python script for Homeassistant that will add LDAP authentication
## How it works
- Includes a [Home Assistant](https://www.home-assistant.io/docs/authentication/providers/#command-line)

## Installation
1. Copy the Python script in to your `/config/python_scripts` directory or install via HACS.
2. Set file execution permissions: `chmod +x /config/python_scripts/auth-ldap.py`

After each update, you must re-set execution rights. The easiest way is to create automation for setting rights at startup Home Assistant

## Script arguments
 key | type | example | description |
 :-- | :--: | :-----: | :---------- |
`-h` | boolean | - | Get help information
`-m` | boolean | - | Enable meta to output credentials to stdout<br>(Defaults to False)
`-U` | string  | - | LDAP username
`-P` | string  | - | LDAP user password
`-s` | string  | `-s 'example.com'` | LDAP server
`-u` | string  | `-u 'uid={},ou=people,dc=example,dc=com'` | LDAP USER DN
`-b` | string  | `-b 'ou=people,dc=example,dc=com'` | LDAP BASE DN
`-f` | string  | `-f '(uid={})'` | LDAP FILTER
`-a` | string  | `-a 'givenName' -a 'memberof'` | Get an array of attributes
`-i` | boolean | - | Deactivate user account<br>(Defaults to True)
`-l` | boolean | - | Access only from local network<br>(Defaults to False)

`{}` - is replaced by the username

Connection and search data can be read from the [.env.ini](https://github.com/Losenmann/ha-auth-ldap/blob/master/.env.ini) configuration file located next to the module.

## Usage
The module can be used as part of Home Assistant or separately via the CLI

- To use the module as part of Home Assistant, you need to edit the configuration: `/config/configuration.yaml`
```
homeassistant:
  auth_providers:
    - type: command_line
      command: /config/python_scripts/auth-ldap.py
      args: ["-m", "-s", "example.com", "-u", "uid={},ou=people,dc=example,dc=com", "-b", "ou=people,dc=example,dc=com", "-f", "(uid={})", -a "givenName" -a "memberof"]
      meta: true
```
When used as part of Home Assistant, there is no need to pass username(key -U) and password(key -P)
- Use via CLI

`auth-ldap.py -U 'username' -P 'password' -s 'example.com' -u 'uid={},ou=people,dc=example,dc=com' -b 'ou=people,dc=example,dc=com' -f '(uid={})' -a givenName -a memberof`

If authentication is successful, return code is 0 otherwise 1

## Additional information
The LDAP server must support the `memberof` module. There should be an entry in the configuration: `olcModuleload: memberof.so`. In Alpine Linux, the module can be installed like this: `apk add openldap-overlay-memberof`

The structure of the LDAP tree should look like this:
```
cn=system-admin,cn=homeassistant,dc=example,dc=com
cn=system-users,cn=homeassistant,dc=example,dc=com
```

Users can be added to a parent group:
```
cn=homeassistant,dc=example,dc=com
```
In this case, members of the parent group will have rights `system-users`

Prospective users must have the following attributes:
- uid
- givenName
- memberof

If the `givenName` attribute is missing, then the login will be used as the username
