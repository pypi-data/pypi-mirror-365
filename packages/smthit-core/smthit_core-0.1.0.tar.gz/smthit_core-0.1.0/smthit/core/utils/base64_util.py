import base64


def base_encode(text: str):
    encoded_bytes = base64.b64encode(text.encode('utf-8'))
    encoded_str = encoded_bytes.decode('ascii')
    return encoded_str


def base_decode(text: str):
    decoded_bytes = base64.b64decode(text)
    decoded_text = decoded_bytes.decode('utf-8')
    return decoded_text


if __name__ == '__main__':
    encode_str = base_encode('Hello, world!!')
    print(encode_str)
    print(base_decode(encode_str))

