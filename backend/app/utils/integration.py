import requests
from fastapi import HTTPException

api_url = "https://tstfastapi.azurewebsites.net/"

async def get_furniture(id : int):

    login_response = requests.post(api_url + '/token/', json={'username': 'duke', 'password': 'password'})

    if login_response.status_code == 200:
        access_token = login_response.json().get("access_token")
        header = {"Authorization": f"Bearer {access_token}"}
        furniture = requests.post(api_url + '/furniture/{id}', headers={header})
        if furniture.status_code == 200:
            return furniture.json()
        else:
            raise HTTPException(furniture.status_code)
    else:
        raise HTTPException(login_response.status_code, detail="Failed to login to furniture service")

async def get_furniture_model(id : int):

    login_response = requests.post(api_url + '/token/', json={'username': 'duke', 'password': 'password'})

    if login_response.status_code == 200:
        access_token = login_response.json().get("access_token")
        header = {"Authorization": f"Bearer {access_token}"}
        model = requests.post(api_url + '/model/{id}', headers={header})
        if model.status_code == 200:
            return model
        else:
            raise HTTPException(model.status_code)