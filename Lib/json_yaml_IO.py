import json
import yaml
import os
import markdown

def read_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    return data

def write_text(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(data)

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def read_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data

def write_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def write_yaml(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, allow_unicode=True, indent=4)

def read_file(file_path):
    if file_path.endswith('.json'):
        return read_json(file_path)
    elif file_path.endswith('.yaml'):
        return read_yaml(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

def json_to_text(json_content):
    text_content = json.dumps(json_content, ensure_ascii=False, indent=4)
    text_content = json.loads(text_content)
    text_content_type = type(text_content)
    print(text_content_type)
    return text_content

if __name__ == "__main__":
    file_path = 'JOEY TSENG（曾卓毅）BA.json'
    json_content = read_json(file_path)
    print(json_content)
