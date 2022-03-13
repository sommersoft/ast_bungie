from pprint import pprint
from . import parse_api

if __name__ == "__main__":
    foo = parse_api.BNetSchema()
    bar = foo.paths()

    #pprint(bar[list(bar)[0]])
    for item in bar.values():
        print(f"{item['summary'].split('.')[0]}.{item['py_method']}")
        print(" Parameters:")
        get_or_post = "get" if "get" in item else "post"
        if item[get_or_post]["parameters"]:
            for param in item[get_or_post]["parameters"]:
                print(f"   schema: {param['schema']}")
