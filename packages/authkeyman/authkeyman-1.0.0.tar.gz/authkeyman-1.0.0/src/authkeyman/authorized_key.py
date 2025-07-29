from typing import Optional


class AuthorizedKey:
    def __init__(self, key_type: str, key: str, comment: str):
        self.key_type = key_type
        self.key = key
        self.comment = comment

    @classmethod
    def from_line(cls, line: str) -> Optional["AuthorizedKey"]:
        line_split = line.split()
        if len(line_split) < 3:
            return None
        
        return cls(line_split[0], line_split[1], " ".join(line_split[2:]))

    def __str__(self) -> str:
        return f"{self.key_type} {self.key} {self.comment}"
