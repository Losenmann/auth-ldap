# Home Assistant Auth LDAP
Python script for Homeassistant that will add LDAP authentication
## How it works
- Includes a [Home Assistant](https://www.home-assistant.io/docs/authentication/providers/#command-line)

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

Connection and search data can be read from the [.env.ini](.env.ini) configuration file located next to the module.

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
- Use via CLI

`auth-ldap.py -U 'username' -P 'password' -s openldap -u 'uid={},ou=people,dc=example,dc=com' -b 'ou=people,dc=example,dc=com' -f '(uid={})' -a givenName -a memberof`

If authentication is successful, return code is 0 otherwise 1
