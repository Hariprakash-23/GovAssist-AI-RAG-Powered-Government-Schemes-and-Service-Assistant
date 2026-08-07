import json
from pathlib import Path


class JSONLoader:

    def __init__(self, folder):

        self.folder = Path(folder)

    def load(self, filename):

        path = self.folder / filename

        if not path.exists():

            raise FileNotFoundError(path)

        with open(path, encoding="utf-8") as file:

            return json.load(file)

    def save(self, filename, data):

        path = self.folder / filename

        with open(path, "w", encoding="utf-8") as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )