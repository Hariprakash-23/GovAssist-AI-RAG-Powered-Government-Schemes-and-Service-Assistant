import json
from pathlib import Path


class CSCLocator:

    def __init__(self):

        path = Path("app/database/csc_centers.json")

        with open(path, encoding="utf-8") as file:

            self.data = json.load(file)

    def search(self, city):

        city = city.lower()

        results = []

        for center in self.data:

            if center["city"].lower() == city:

                results.append(center)

        return results