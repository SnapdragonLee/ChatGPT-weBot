import random
import requests


def r_hex(length: int):
    hex_chars = "0123456789abcdef"
    random_hex = "".join(random.choice(hex_chars) for _ in range(length))
    return random_hex


class ImageGenerator:
    def __init__(self, ):
        self.cookie = {
            'replicate_anonymous_id': f'{r_hex(8)}-{r_hex(4)}-'
                                      f'{r_hex(4)}-{r_hex(4)}-{r_hex(12)}',
        }
        self.session = requests.session()
        self.headers = {}

    def gen_image(self, prompt, count, height, width, *args, **kwargs):
        pass

    def get_image_url(self, uuid):
        pass
