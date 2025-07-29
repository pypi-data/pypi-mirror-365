import yaml

def load_model_params(yaml_file_path: str) -> dict:
    with open(yaml_file_path, 'r') as f:
        params = yaml.safe_load(f)
    return params