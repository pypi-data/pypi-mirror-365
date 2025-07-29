import requests
from exceptions import GanAIRequestError
import typer

app = typer.Typer()

@app.command()
def generate_sound_effect(base_url, headers, prompt, creativity, duration, num_variants):
    url = f"{base_url}/v1/sfx/generate"
    data = {
        "prompt": prompt,
        "creativity": creativity,
        "duration": duration,
        "num_variants": num_variants,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        return response.content
    raise GanAIRequestError(response.status_code)
