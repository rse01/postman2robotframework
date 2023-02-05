import json
import re

class PostmanParser:
    def __init__(self, collection_file):
        with open(collection_file, 'r') as file:
            self.collection = json.load(file)

        self.library = {
            "name": "",
            "variables": set(),
            "items": []
        }

    def get_library_from_collection(self):
        if self.collection["info"]["schema"] != "https://schema.getpostman.com/json/collection/v2.1.0/collection.json":
            raise Exception("The schema of the collection is invalid, expecting v2.1.0")

        self.library["name"] = self.collection["info"]["name"]
        self.library["items"] = self.get_keywords_from_items(self.collection["item"])
        return self.library

    def get_keywords_from_items(self, items):
        keywords = []
        keyword_names = set()

        for item in items:
            if "item" in item:
                new_keywords = self.get_keywords_from_items(item["item"])
                for keyword in new_keywords:
                    if keyword["def_name"] not in keyword_names:
                        keywords.append(keyword)
                        keyword_names.add(keyword["def_name"])
            else:
                request = item["request"]
                keyword = {
                    "def_name": item["name"].replace(" ", "_"),
                    "method": request["method"],
                    "url": request["url"]["raw"],
                    "header": {header["key"]: header["value"] for header in request["header"]},
                    "body": self.get_body(item),
                    "documentation": request.get("description", ""),
                    "variables": []
                }

                keyword["url"], vars = self.prepare_variables(keyword["url"])
                keyword["body"], vars_ = self.prepare_variables(keyword["body"])
                keyword["variables"] = keyword["variables"] + vars + vars_

                keywords.append(keyword)
                keyword_names.add(keyword["def_name"])

        return keywords

    def prepare_variables(self, s):
        vars = []
        pattern = re.compile(r'{{(.*?)}}')
        if s and pattern.search(s):
            for match in re.finditer(pattern, s):
                s = s.replace(match.group(0), "${" + match.group(1) + "}")
                vars.append(match.group(1))

            self.library["variables"].update(vars)

        return s, vars

    def get_body(self, item):
        if "body" in item["request"]:
            body = item["request"]["body"]
            if body["mode"] == "raw":
                return body["raw"]
            elif body["mode"] == "urlencoded":
                return "&".join(param
