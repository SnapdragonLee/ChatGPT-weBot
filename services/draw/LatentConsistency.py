import json
import time
import requests

from .ImageGenerator import ImageGenerator
from services.model import BotError


class LTCST(ImageGenerator):
    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://replicate.com/stability-ai/sdxl',
            'Content-Type': 'application/json',
            'Origin': 'https://replicate.com',
            'Connection': 'keep-alive',
        }

    def gen_image(self, prompt, count, height, width, *args, **kwargs):
        num_inference_steps = kwargs.get('num_inference_steps', 8)
        guidance_scale = kwargs.get('guidance_scale', 8)
        seed = kwargs.get('seed', None)
        try:
            # Check if count is within the valid range
            if count < 1 or count > 10:
                raise ValueError("Count must be between 1 and 4")

            # Check if width and height are within the valid range
            if width > 1024 or height > 1024:
                raise ValueError("Width and height must be 1024 or less")

            # Check if num_inference_steps is within the valid range
            if num_inference_steps < 1 or num_inference_steps > 50:
                raise ValueError("num_inference_steps must be between 1 and 50")

            # Check if guidance_scale is within the valid range
            if guidance_scale < 1 or guidance_scale > 10:
                raise ValueError("guidance_scale must be between 1 and 10")

            url = ("https://replicate.com/api/models/luosiallen/latent-consistency-model/versions/"
                   "553803fd018b3cf875a8bc774c99da9b33f36647badfd88a6eec90d61c5f62fc/predictions")

            payload = json.dumps({
                "inputs": {
                    "width": width,
                    "height": height,
                    "prompt": prompt,
                    "num_images": count,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "seed": seed
                }
            })

            response = self.session.post(url, headers=self.headers, cookies=self.cookie, data=payload)

            response.raise_for_status()

            json_response = response.json()
            uuid = json_response['uuid']
            image_url = self.get_image_url(uuid)

            return image_url

        except ValueError as e:
            err = BotError("LTCST_Error", e.__str__(), -1)
            return err

        except requests.exceptions.RequestException as e:
            err = BotError("LTCST_Error", f'Error occurred while making the request:{e.__str__()}', -3)
            return err

        except KeyError as e:
            err = BotError("LTCST_Error", f"Error occurred while processing the response: {e.__str__()}", -3)
            return err

        except Exception as e:
            err = BotError("LTCST_Error", f"An unexpected error occurred: {e.__str__()}", -9)
            return err

    def get_image_url(self, uuid):
        url = (f"https://replicate.com/api/models/luosiallen/latent-consistency-model/versions/"
               f"553803fd018b3cf875a8bc774c99da9b33f36647badfd88a6eec90d61c5f62fc/predictions/{uuid}")
        flag = False
        output = ''

        while flag is not True:
            response = self.session.get(url, headers=self.headers).json()
            if response['prediction']['status'] == "succeeded":
                flag = True
                output = response['prediction']['output_files']
            elif response['prediction']['status'] == "failed":
                err = BotError("LTCST_Error", response['prediction']['error'], -1)
                return err
            else:
                time.sleep(3)

        return output
