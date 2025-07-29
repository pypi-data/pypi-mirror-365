from pathlib import Path
from typing import Optional

from authkeyman.authorized_key import AuthorizedKey


class AuthorizedKeysFile:
    def __init__(self, path: Path, user: Optional[str] = None):
        self.path = path
        self.keys: list[AuthorizedKey] = []
        self.user = user

        try:
            path.parent.mkdir(mode=0o775, exist_ok=True)
            path.touch(mode=0o600, exist_ok=True)

            with open(path, "r") as file:
                lines = file.readlines()
                for line in lines:
                    key = AuthorizedKey.from_line(line)
                    if key is None:
                        print(f"Failed to parse key in {path}:")
                        print(line)
                        exit(1)
                    self.keys.append(key)
        except PermissionError:
            print("Insufficient permissions!")
            if user is None:
                print(f"Try checking the permissions on your home directory.")
            else:
                print(f"You must run as sudo when adding keys to other users.")
            exit(1)

    def get_key_from_comment(self, comment: str) -> Optional[AuthorizedKey]:
        comment = comment.lower()
        for key in self.keys:
            if key.comment.lower() == comment:
                return key
        return None

    def save(self):
        with open(self.path, "w") as file:
            for key in self.keys:
                file.write(f"{key}\n")
        return None

    def __str__(self) -> str:
        string = ""
        for key in self.keys:
            string += str(key) + "\n"
        return string


