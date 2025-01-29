import pytest
from fastapi.testclient import TestClient
from moto import mock_aws as mock_dynamodb
import boto3
from main import app, table, User

# Cliente de pruebas para FastAPI
client = TestClient(app)

# Configurar DynamoDB mockeado
@pytest.fixture(scope="function")
def setup_dynamodb():
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        # Crear tabla de DynamoDB mockeada
        table = dynamodb.create_table(
            TableName='usuarios-table',
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1}
        )

        yield table  # Proporciona la tabla mockeada a las pruebas

# Prueba: Verificar endpoint de salud
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"health": "ok"}

# Prueba: Crear un usuario exitosamente
def test_create_user(setup_dynamodb):
    user_data = {"user_id": "123", "name": "Juan Perez", "email": "juan@example.com"}
    response = client.post("/users", json=user_data)

    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"
    assert response.json()["user"] == user_data

# Prueba: Obtener un usuario existente
def test_get_user(setup_dynamodb):
    user_data = {"user_id": "123", "name": "Juan Perez", "email": "juan@example.com"}
    setup_dynamodb.put_item(Item=user_data)

    response = client.get(f"/users/{user_data['user_id']}")

    assert response.status_code == 200
    assert response.json() == user_data

# Prueba: Obtener un usuario que no existe
def test_get_user_not_found(setup_dynamodb):
    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# Prueba: Listar usuarios cuando la tabla está vacía
def test_list_users_empty(setup_dynamodb):
    response = client.get("/users")
    
    assert response.status_code == 200
    assert response.json() == {"users": []}

# Prueba: Listar usuarios con datos en la tabla
def test_list_users_with_data(setup_dynamodb):
    users = [
        {"user_id": "123", "name": "Juan Perez", "email": "juan@example.com"},
        {"user_id": "456", "name": "Ana Lopez", "email": "ana@example.com"}
    ]
    
    for user in users:
        setup_dynamodb.put_item(Item=user)

    response = client.get("/users")
    
    assert response.status_code == 200
    assert len(response.json()["users"]) == 2
    assert response.json()["users"] == users