import requests
from exceptions import GanAIRequestError
import typer

app = typer.Typer()

@app.command()
def get_credit_info(base_url, headers):
    url = f"{base_url}/v1/users/credits"
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json()
    raise GanAIRequestError(response.status_code)

@app.command()
def get_account_details(base_url, headers):
    url = f"{base_url}/v1/users/detail"
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json()
    raise GanAIRequestError(response.status_code)
