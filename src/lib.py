from pathlib import Path
import time

class ImageEntry:
    """"""
    def __init__(self, path: Path):
        self.path = path
        self.creation_time = path.stat().st_ctime
        self.num_reveals = 0

    def age(self):
        """Get age in seconds."""
        return time.time() - self.creation_time

    @property
    def name(self):
        return self.path.name

    def increment_reveals(self):
        self.num_reveals += 1

    def __repr__(self) -> str:
        return f'ImageEntry({self.name})'

    def __eq__(self, other) -> bool:
        return self.path == other.path

    def __ne__(self, other) -> bool:
        return self.path != other.path

    def __lt__(self, other) -> bool:
        return self.age() < other.age()
        
    def __le__(self, other) -> bool:
        return self.age() <= other.age()

    def __gt__(self, other) -> bool:
        return self.age() > other.age()
        
    def __ge__(self, other) -> bool:
        return self.age() >= other.age()

    def __hash__(self) -> int:
        return self.path.__hash__()