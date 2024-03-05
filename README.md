# homeassistant-auth-cli
Python script for Homeassistant that will add LDAP authentication
## How it works

## Installation
Copy the Python script in to your `/config/python_scripts` directory or install via HACS.

## Script arguments
key | required | type | example | description
-- | -- | -- | -- | --
`-h` | False | boolean | - | Help
`-m` | True | boolean | - | Enable meta to output credentials to stdout
`-U` | True | string | - | LDAP username
`-P` | True | string | - | LDAP user password
`-s` | True | string | 'example.com' | Set LDAP server
`-u` | True | string | 'uid={},ou=people,dc=example,dc=com' | Set LDAP USER DN
`-b` | True | string | 'ou=people,dc=example,dc=com' | Set LDAP BASE DN
`-f` | True | string | '(uid={})' | Set LDAP FILTER
`-a` | True | string | -a 'givenName' -a 'memberof' | Set LDAP an array of attributes
`-i` | False | boolean | - | Deactivate user account (Defaults to True)
`-l` | False | boolean | - | The user can only login from the local network if the key is passed (Defaults to False)

`{}` - is replaced by the username

## Usage
To use the module, you need to edit the Home Assistant configuration
```
*
homeassistant:
  auth_providers:
    - type: command_line
      command: /config/python_scripts/auth-ldap.py
      args: ["-m", "-s", "example.com", "-u", "uid={},ou=people,dc=example,dc=com", "-b", "ou=people,dc=example,dc=com", "-f", "(uid={})", -a "givenName" -a "memberof"]
      meta: true
*
```
