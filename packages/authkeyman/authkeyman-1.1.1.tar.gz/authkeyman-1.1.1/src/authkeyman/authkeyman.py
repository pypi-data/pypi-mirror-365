from pathlib import Path
import os
from argparse import ArgumentParser
from typing import Optional

from authkeyman.authorized_key import AuthorizedKey
from authkeyman.authorized_keys_file import AuthorizedKeysFile


def _get_auth_keys_files(users: Optional[list[str]]) -> list[AuthorizedKeysFile]:
    keys_location = ".ssh/authorized_keys"
    auth_keys_files: list[AuthorizedKeysFile] = []
    if users is None:
        auth_keys_path = Path.home() / keys_location
        auth_keys_file = AuthorizedKeysFile(auth_keys_path)
        auth_keys_files.append(auth_keys_file)
    else:
        for user in users:
            home_dir = os.path.expanduser(f"~{user}")
            if home_dir[0] == "~":
                print(f"User '{user}' does not exist.")
                exit(1)
            auth_keys_path = Path(home_dir) / keys_location
            auth_keys_file = AuthorizedKeysFile(auth_keys_path, user)
            auth_keys_files.append(auth_keys_file)
    return auth_keys_files


def _find_keys_from_comment_contents(
    auth_keys_file: AuthorizedKeysFile,
    comment_content: str,
)-> list[AuthorizedKey]:
    found_keys = []
    for key in auth_keys_file.keys:
        if comment_content in key.comment:
            found_keys.append(key)
    return found_keys


def _get_key_from_comment_contents(
    auth_keys_file: AuthorizedKeysFile,
    comment_content: str,
    use_first_match: bool = False,
) -> Optional[AuthorizedKey]:
    found_keys = _find_keys_from_comment_contents(auth_keys_file, comment_content)
    if len(found_keys) == 0:
        return None

    if use_first_match and len(found_keys) > 0:
        return found_keys[0]

    if len(found_keys) == 1:
        print(f"No keys found commented with '{comment_content}', but a similar key was found:")
        print(found_keys[0].comment)
        print()
        response = input("Would you like to use this one instead? (y/N): ")
        confirm = len(response) > 0 and response.lower()[0] == "y"
        return found_keys[0] if confirm else None

    if len(found_keys) > 1:
        print(f"No keys found commented with '{comment_content}', but these similar keys were found:")
        for i, key in enumerate(found_keys):
            print(f"[{i}]: {key.comment}")
        print()
        response = input(f"Which one would you like to use instead? (Default 0, make a selection 0-{len(found_keys)-1}): ")
        try:
            response_idx = int(response) if len(response) > 0 else 0
            return found_keys[response_idx]
        except (ValueError, IndexError):
            print("Invalid response.")
            return None
    return None


def cmd_add(args):
    auth_keys_files = _get_auth_keys_files(args.user)
    for auth_keys_file in auth_keys_files:
        for new_key_line in args.key:
            new_key = AuthorizedKey.from_line(new_key_line)
            if new_key is None:
                print("Invalid key provided. You may need to wrap your key in quotes.")
                exit(1)
            if auth_keys_file.get_key_from_comment(new_key.comment) is not None:
                if auth_keys_file.user is None:
                    print(f"Key '{new_key.comment}' already exists.")
                else:
                    print(f"Key '{new_key.comment}' already exists for user '{auth_keys_file.user}'.")
                continue
            auth_keys_file.keys.append(new_key)
        auth_keys_file.save()
    return None


def _find_keys(
    auth_keys_files: list[AuthorizedKeysFile],
    desired_comments: list[str],
    confirm: bool = False
) -> dict[AuthorizedKeysFile, list[AuthorizedKey]]:
    comment_map: dict[str, str] = {}
    found_keys: dict[AuthorizedKeysFile, list[AuthorizedKey]] = {}
    for auth_keys_file in auth_keys_files:
        for desired_comment in desired_comments:
            if desired_comment in comment_map:
                desired_comment = comment_map[desired_comment]

            key = auth_keys_file.get_key_from_comment(desired_comment)
            if key is None:
                key = _get_key_from_comment_contents(auth_keys_file, desired_comment, confirm)
                if key is not None:
                    comment_map[desired_comment] = key.comment

            if key is None:
                if auth_keys_file.user is None:
                    print(f"Cannot find key with comment '{desired_comment}'")
                else:
                    print(f"Cannot find key with comment '{desired_comment}' for user '{auth_keys_file.user}'")
                continue

            if auth_keys_file not in found_keys:
                found_keys[auth_keys_file] = []
            found_keys[auth_keys_file].append(key)
    return found_keys


def cmd_remove(args):
    auth_keys_files = _get_auth_keys_files(args.user)
    found_keys = _find_keys(auth_keys_files, args.key_comment, args.y)
    for auth_key_file in found_keys:
        for key in found_keys[auth_key_file]:
            auth_key_file.keys.remove(key)
        auth_key_file.save()
    return None


def cmd_list(args):
    auth_keys_files = _get_auth_keys_files(args.user)
    for i, auth_keys_file in enumerate(auth_keys_files):
        if len(auth_keys_file.keys) == 0:
            print(f"No keys in {auth_keys_file.path}")
            continue

        print(f"Keys in {auth_keys_file.path}:")
        for key in auth_keys_file.keys:
            print(key.comment)
        # Separate each authorized_keys list by a newline
        if i != len(auth_keys_files) - 1:
            print()
    return None

            
def main() -> int:
    parser = ArgumentParser(
        prog="authkeyman",
        description="Quickly manage your authorized public SSH keys",
    )
    parser.add_argument(
        "-u", "--user",
        action="append",
        help="Specify another user to work on. You must run as sudo to use this option. You can specify this option multiple times to specify more than one user."
    )

    subparsers = parser.add_subparsers(
        required=True,
    )

    add_parser = subparsers.add_parser(
        "add",
        help="Add SSH keys to authorized_keys"
    )
    add_parser.add_argument(
        "key",
        nargs="+",
        help="Public key or keys to add to authorized_keys"
    )
    add_parser.set_defaults(func=cmd_add)

    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove SSH keys from authorized_keys"
    )
    remove_parser.add_argument(
        "key_comment",
        nargs="+",
        help="Public key comment or key comments to remove from authorized_keys"
    )
    remove_parser.add_argument(
        "-y",
        help="Automatically confirm key deletion on partial match",
        action="store_true"
    )
    remove_parser.set_defaults(func=cmd_remove)

    list_parser = subparsers.add_parser(
        "list",
        help="Lists all keys from authorized_keys"
    )
    list_parser.set_defaults(func=cmd_list)
    
    args = parser.parse_args()
    if args.func is not None:
        args.func(args)

    return 0


if __name__ == "__main__":
    main()
