import requests

from enum import Enum

class TTSModelVersionEnum(Enum):
    V1 = "v1"
    V2 = "v2"
    
class GanAI:
    def __init__(self,api_key:str):
        self.api_key = api_key
        self.base_url = "https://os.gan.ai"
        self.headers = {
            "Ganos-Api-Key": f"{self.api_key}",
            "Content-Type": "application/json",
        }
     
    def ping(self):
        return "We are live, let's build something amazing!"
    
    def get_credit_info(self):
        """Get credit info."""
        url = f"{self.base_url}/v1/users/credits"
        headers = self.headers
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}")
    
    def account_details(self):
        """Get account details."""
        url = f"{self.base_url}/v1/users/detail"
        headers = self.headers
        response = requests.get(url, headers=headers)
        print(response.json())
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}")
    
    def update_headers(self,headers:dict):
        self.headers.update(headers)
        
    def sound_effect(self,prompt:str,creativity:float=0.7,duration:int=10, num_variants:int=4):
        """Generate sound effect using given prompt.
        Args:
            prompt (str): The text to convert to audio.
            creativity (float, optional): creativity of the sound effect. Defaults to 0.7.
            duration (int, optional): duration in seconds of the sound effect. Defaults to 10.
            num_variants (int, optional): number of variants of the sound effect. Defaults to 4.

        Returns:
            bytes: The binary audio content (e.g., MP3 or WAV).
        """
        url = f"{self.base_url}/v1/sfx/generate"
        headers = self.headers
        data = {
            "prompt": prompt,
            "creativity": creativity,
            "duration": duration,
            "num_variants": num_variants,
        }
        response = requests.post(url, headers=headers, json=data)
        print(response.json())
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Error: {response.status_code}")
    
    def text_to_speech(self,text:str,voice_id:str="en-US",version:TTSModelVersionEnum=TTSModelVersionEnum.V1):
        """Generate text to speech using given text and voice id.
        Args:
            text (str): The text to convert to audio.
            voice_id (str, optional): Voice ID. Defaults to "en-US".
            version (TTSModelVersionEnum, optional): API version. Defaults to V1.

        Returns:
            bytes: The binary audio content (e.g., MP3 or WAV).
        """
        url = f"{self.base_url}/v1/tts/generate"
        headers = self.headers
        data = {
            "text": text,
            "voice_id": voice_id,
            "version": version.value,
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Error: {response.status_code}")
    
    
           