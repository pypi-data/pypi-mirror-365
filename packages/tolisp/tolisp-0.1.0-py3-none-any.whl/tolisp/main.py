import sys
import os
import json
import yaml
import re
import urllib.request

def to_sexpr(data, tag):
    if isinstance(data, dict):
        return "(" + " ".join(f"({tag}:{key} {to_sexpr(value, tag)})" for key, value in data.items()) + ")"
    elif isinstance(data, list):
        if all(isinstance(i, dict) and 'part_no' in i for i in data):
            return "(" + " ".join(f"({tag}:item {to_sexpr(item, tag)})" for item in data) + ")"
        else:
            return "(" + " ".join(to_sexpr(item, tag) for item in data) + ")"
    elif isinstance(data, str):
        if re.match(r"^\d{4}-\d{2}-\d{2}$", data):
            y, m, d = map(int, data.split("-"))
            return f"(make-date {y} {m} {d})"
        escaped = data.replace('"', '\\"')
        return f'"{escaped}"'
    elif isinstance(data, (int, float)):
        return str(data)
    elif isinstance(data, bool):
        return "true" if data else "false"
    elif data is None:
        return "nil"
    else:
        return f"\"{str(data)}\""

def is_url(path):
    return path.startswith("http://") or path.startswith("https://")

def fetch_from_url(url):
    with urllib.request.urlopen(url) as response:
        content_type = response.headers.get("Content-Type", "")
        raw = response.read().decode("utf-8")
        return raw, content_type

def main():
    if len(sys.argv) != 2:
        print("Usage: tolisp <.yaml | .json | URL>")
        sys.exit(1)

    input_source = sys.argv[1]

    try:
        if is_url(input_source):
            print(f"Fetching file from URL...")
            raw_data, content_type = fetch_from_url(input_source)

            if input_source.endswith(".json") or "json" in content_type:
                data = json.loads(raw_data)
                result = to_sexpr(data, tag="json")
            elif input_source.endswith(".yaml") or "yaml" in content_type:
                data = yaml.safe_load(raw_data)
                result = to_sexpr(data, tag="yaml")
            else:
                print(f"Error: Unsupported file type. Please provide a .yaml or .json file.")
                sys.exit(1)
        else:
            if not os.path.isfile(input_source):
                print(f"Error: file not found!")
                sys.exit(1)

            with open(input_source, 'r', encoding='utf-8') as f:
                if input_source.endswith(".json"):
                    data = json.load(f)
                    result = to_sexpr(data, tag="json")
                elif input_source.endswith(".yaml") or input_source.endswith(".yml"):
                    data = yaml.safe_load(f)
                    result = to_sexpr(data, tag="yaml")
                else:
                    print(f"Error: Unsupported file type. Please provide a .yaml or .json file.")
                    sys.exit(1)

        
        with open("output.lisp", "w", encoding='utf-8') as out:
            out.write(result + "\n")

        print("S-expression written to output.lisp")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
