# authkeyman
A simple command-line tool to make managing your `~/.ssh/authorized_keys` file easier.

- [authkeyman](#authkeyman)
  - [Features](#features)
  - [Install](#install)
  - [Uninstall](#uninstall)
  - [Usage](#usage)
    - [Add Keys](#add-keys)
    - [Remove Keys](#remove-keys)
    - [List Keys](#list-keys)
    - [Perform Actions on Other Users](#perform-actions-on-other-users)


## Features
- Add keys to your `authorized_keys` file.
- Remove keys from your `authorized_keys` file by key comment.
- Add and remove keys from other users when running as `root`.


## Install
If you don't need to manage other users' `authorized_keys` files,
then simply install with `pipx`:
```bash
pipx install authkeyman
```

Otherwise, install the tool system-wide by running this command:
```bash
curl -L https://raw.githubusercontent.com/TacticalLaptopBag/authkeyman/refs/heads/main/curl-install.sh | sudo bash
```


## Uninstall
If you installed with `pipx`, simply use that to uninstall:
```bash
pipx uninstall authkeyman
```

If you installed using the `curl-install.sh` script, use this command:
```bash
curl -L https://raw.githubusercontent.com/TacticalLaptopBag/authkeyman/refs/heads/main/curl-uninstall.sh | sudo bash
```


## Usage

### Add Keys
Add keys to the `authorized_keys` file:
```bash
authkeyman add "ssh-ed25519 XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX your-key-name"
```

Note that the key is wrapped in quotes.

You can also add multiple keys at once by stringing them together:
```bash
authkeyman add "ssh-ed25519 ... key1" "ssh-ed25519 ... key2" ...
```


### Remove Keys
Remove keys from the `authorized_keys` file by using its comment:
```bash
authkeyman remove your-key-name
```

You can remove multiple keys at once:
```bash
authkeyman remove key1 key2
```

You can also use partial comments and `authkeyman` will prompt you
if the matching key is the one you want to remove:
```bash
authkeyman remove key-name
```
```
No keys found commented with 'key-name', but a similar key was found:
your-key-name

Would you like to use this one instead? (y/N):
```

If multiple keys match, it will ask you to make a decision:
```bash
authkeyman remove key
```
```
No keys found commented with 'key', but these similar keys were found:
[0]: key1
[1]: key2

Which one would you like to use instead? (Default 0, make a selection 0-1): 
```

Running this command with `-y` will skip the prompt and remove the key.
If multiple keys match, it will delete the first key that matches.


### List Keys
Lists all key comments in the `authorized_keys` file:
```bash
authkeyman list
```
```
Keys in /home/user/.ssh/authorized_keys:
key1
key2
```


### Perform Actions on Other Users
You can run all of these commands on other users
when running `authkeyman` as `root` and specifying the `--user` flag:
```bash
sudo authkeyman --user user1 add "ssh-ed25519 ... user1s-key"
```

You can add additional `--user` flags to specify multiple users:
```bash
sudo authkeyman --user user1 --user user2 add "ssh-ed25519 ... users-key"
```
Note that the `--user` flags must come directly after `authkeyman`
and cannot come after a subcommand.
