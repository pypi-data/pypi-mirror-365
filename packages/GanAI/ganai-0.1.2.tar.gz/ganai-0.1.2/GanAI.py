from enums import TTSModelVersionEnum
from endpoints import users, sfx, tts

class GanAI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://os.gan.ai"
        self.headers = {
            "Ganos-Api-Key": f"{self.api_key}",
            "Content-Type": "application/json",
        }

    def update_headers(self, headers: dict):
        self.headers.update(headers)

    def get_credit_info(self):
        return users.get_credit_info(self.base_url, self.headers)

    def account_details(self):
        return users.get_account_details(self.base_url, self.headers)

    def sound_effect(self, prompt: str, creativity=0.7, duration=10, num_variants=4):
        return sfx.generate_sound_effect(
            self.base_url, self.headers, prompt, creativity, duration, num_variants
        )

    def text_to_speech(self, text: str, voice_id="en-US", version=TTSModelVersionEnum.V1):
        return tts.generate_tts(
            self.base_url, self.headers, text, voice_id, version.value
        )
