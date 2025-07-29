import requests
from exceptions import GanAIRequestError
import typer

app = typer.Typer()

@app.command()
def generate_tts(base_url, headers, text, voice_id, version):
    url = f"{base_url}/v1/tts/generate"
    data = {
        "text": text,
        "voice_id": voice_id,
        "version": version,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        return response.content
    raise GanAIRequestError(response.status_code)
