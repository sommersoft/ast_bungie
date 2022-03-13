import json
from pathlib import Path
import re

class SchemaType:
    def __init__(self, **schema):
        self._type = schema.get("type")
        self._format = schema.get("format", None)
        self._items = schema.get("items", None)
        self.description = schema.get("description", '""')
        self._raw = schema

    def __repr__(self):
        sig_line = ", ".join(
            [
                f"{key}={val}" for key,val in self.schema().items()
            ]
        )
        return f"SchemaType({sig_line})"

    @property
    def type(self):
        return self._type

    @property
    def format(self):
        return self._format

    @property
    def items(self):
        return self._items

    def schema(self):
        completed_schema = {
            "type": self.type,
            "description": self.description,
        }
        if self.type != "array":
            completed_schema.update({
                "format": self.format,
            })
        else:
            completed_schema.update({
                "items": self.items
            })

        return completed_schema


class BNetSchema:
    def __init__(self):
        self.source_path = Path(".") / "openapi.json"
        with open(self.source_path) as source_file:
            self.source = json.load(source_file)

    @staticmethod
    def parameters(params):
        """Processes a Parameters object supplied by `params`."""
        processed = []
        for param in params:
            new_param = {
                "name": param["name"],
                "in": param["in"],
                "schema": SchemaType(**param["schema"]),
                "description": param.get("description", param["name"]),
                "required": param.get("required", "false"),
                "deprecated": param.get("deprecated", "false"),

            }
            processed.append(new_param)

        return processed

    def paths(self, roots=["Destiny2"]):
        """Retrieves API paths. Can be filtered via `root` (Default is 'Destiny2')."""
        path_map = {}
        for api_path, data in self.source["paths"].items():
            path_root, path_method = data["summary"].split(".")
            if path_root in roots:
                data["path"] = api_path
                data["py_method"] = re.sub(
                    r"([a-z])([A-Z])",
                    r"\1_\2",
                    path_method
                ).lower()
                get_or_post = "get" if data.get("get", False) else "post"
                data[get_or_post]["parameters"] = BNetSchema.parameters(
                    data[get_or_post]["parameters"]
                )
                path_map.update({
                    data["summary"]: data,
                })

        return path_map

    def component(self, ref):
        """Retrieves the component referenced by `ref`."""
        _, ref_type, ref_name = ref.rsplit("/", 2)
        return self.source["components"][ref_type][ref_name]
