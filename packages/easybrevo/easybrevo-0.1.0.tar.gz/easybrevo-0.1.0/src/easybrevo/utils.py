import base64


def encode_file_to_base64(file_path) -> str:
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
        encoded = base64.b64encode(file_bytes).decode('utf-8')
    return encoded
