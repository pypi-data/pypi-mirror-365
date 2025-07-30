import os
import tempfile
from typing import Dict, Any

import requests
from volcengine.visual.VisualService import VisualService

try:
    from ..storage.tos_client import upload_to_tos
except (ImportError, ValueError):
    # This fallback is for running the script directly
    import sys
    import os

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from media_agent_mcp.storage.tos_client import upload_to_tos


def parse_seededit_response(response) -> Dict[str, Any]:
    """
    Parse the seededit API response and extract the image URL.
    
    :param response: The API response dictionary
    :return: JSON response with status, data (image URL), and message
    """
    try:
        # Handle both possible response formats
        if 'data' in response and 'image_urls' in response['data']:
            # Format 1: {'data': {'image_urls': [...]}}
            image_urls = response['data']['image_urls']
        elif 'image_urls' in response:
            # Format 2: {'image_urls': [...]}
            image_urls = response['image_urls']
        else:
            raise ValueError("No image_urls found in response")
        
        if not image_urls or len(image_urls) == 0:
            raise ValueError("Empty image_urls list")
        
        # Get the first URL and clean it
        url = image_urls[0]
        # Remove leading/trailing whitespace and backticks
        url = url.strip().strip('`').strip()
        
        return {
            "status": "success",
            "data": {"image_url": url},
            "message": "Image URL parsed successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": f"Failed to parse response: {e}"
        }


def seededit(image_url, prompt, charactor_keep=False, return_url=True, scale=1, seed=-1) -> Dict[str, Any]:
    """
    Perform image editing using the VisualService, then upload the result to TOS.

    :param image_url: URL of the input image.
    :param prompt: The editing prompt.
    :param charactor_keep: Whether to keep the main character in the image.
    :param return_url: Whether to return image URL or base64 string.
    :param scale: Text influence scale (0.1-1.0).
    :param seed: Random seed for reproducibility.
    :return: JSON response with status, data (TOS URL), and message.
    """
    try:
        visual_service = VisualService()

        # call below method if you don't set ak and sk in $HOME/.volc/config
        ak = os.getenv('VOLC_AK')
        sk = os.getenv('VOLC_SK')

        if not ak or not sk:
            return {
                "status": "error",
                "data": None,
                "message": "VOLC_AK and VOLC_SK environment variables must be set"
            }

        visual_service.set_ak(ak)
        visual_service.set_sk(sk)

        if charactor_keep == 'True' or charactor_keep == 'true':
            charactor_keep = True
        
        if return_url == 'False' or return_url == 'false':
            return_url = False

        form = {
            "req_key": "seed3l_single_ip" if charactor_keep else "seededit_v3.0",
            "image_urls": [image_url],
            'prompt': prompt,
            'return_url': return_url,
            'scale': scale,
            'seed': seed,
        }

        form_ = form.copy()
        form_['character_keep'] = charactor_keep

        print('[DEBUG]SeedEdit Request form:', form_)

        response = visual_service.cv_process(form)
        parsed_response = parse_seededit_response(response)

        if parsed_response['status'] == 'success':
            generated_image_url = parsed_response['data']['image_url']
            print('[DEBUG] Generated image URL:', generated_image_url)

            # Download the image from the URL
            try:
                image_response = requests.get(generated_image_url, stream=True)
                image_response.raise_for_status()  # Raise an exception for bad status codes
            except requests.exceptions.RequestException as e:
                return {"status": "error", "data": None, "message": f"Failed to download image: {e}"}

            # Create a temporary file to save the image
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                for chunk in image_response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            try:
                # Upload the temporary file to TOS
                tos_response = upload_to_tos(temp_file_path)
                # The URL is in tos_response['data']['url']
                # The final response should be compatible with other tools
                if tos_response['status'] == 'success':
                    return {
                        "status": "success",
                        "data": {"image_url": tos_response['data']['url']},
                        "message": "Image edited and uploaded to TOS successfully"
                    }
                else:
                    return tos_response
            finally:
                # Clean up the temporary file
                os.remove(temp_file_path)
        else:
            return parsed_response

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": f"Error in seededit: {str(e)}"
        }


if __name__ == '__main__':
    prompt = """
    Rahul, with dark hair and a beard, wearing a blue jacket over a white shirt, kneels w
ith fingers near a cracked phone; Nandini, in a purple and orange sari with long hair, kneels beside him, hands holding a loose pile of sketches. A sun-washe
d ochre watercolor of Gondal Ghar lies between them, Rahul's thumb brushing its damp edge. His shoulders are soft, gaze lifted to Nandini with a tentative ha
lf-smile. Nandini's defensive frown has melted; she tucks hair behind her ear slowly, revealing a shy dimple. Soft, warm light illuminates the scene, capturi
ng the eased tension in their quiet interaction."""

    print(seededit('https://ark-content-generation-v2-ap-southeast-1.tos-ap-southeast-1.volces.com/seedream-3-0-t2i/021753679562216e641ee46b93e8beaf1fb3bde23bbe0c62f9e10.jpeg?X-Tos-Algorithm=TOS4-HMAC-SHA256&X-Tos-Credential=AKLTYjg3ZjNlOGM0YzQyNGE1MmI2MDFiOTM3Y2IwMTY3OTE%2F20250728%2Fap-southeast-1%2Ftos%2Frequest&X-Tos-Date=20250728T051245Z&X-Tos-Expires=86400&X-Tos-Signature=744b267256cfd8dbceb74c84532be4aae9a126721cb31013b4547099826ced8c&X-Tos-SignedHeaders=host',
                   prompt=prompt,
                   charactor_keep=False))