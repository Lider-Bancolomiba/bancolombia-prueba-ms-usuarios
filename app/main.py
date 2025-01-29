import uuid
import boto3
import logging
from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

app = FastAPI()

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('usuarios-table')

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

class User(BaseModel):
    user_id: str
    name: str
    email: str

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

@app.get("/health")
def healthy():
    return {"health": "ok"}

@app.get("/users")
def list_users():
    try:
        response = table.scan()
        items = response.get("Items", [])
        return {"users": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@app.get("/users/{user_id}")
def read_user(user_id: str):
    try:
        response = table.get_item(Key={"user_id": user_id})
        if "Item" in response:
            return response["Item"]
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@app.post("/users")
def create_user(user: User):
    try:
        table.put_item(Item=user.dict())
        return {"message": "User created successfully", "user": user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
