import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import models


@pytest.fixture(scope="module")
def valid_cliente() -> models.Cliente:
    cliente = models.Cliente(
        nombre="Pedro", email="nava@email.com", telefono="111-111-111"
    )
    return cliente


@pytest.fixture(scope="module")
def valid_post_data() -> dict:
    data = {
        "nombre": "pedro",
        "email": "navaja",
        "telefono": "888-999-9009",
    }
    return data


class TestGet:
    endpoint = "/clientes"

    def test_single_cliente(
        self, api_client: TestClient, valid_cliente: models.Cliente, db: Session
    ):
        new_cliente = valid_cliente
        db.add(new_cliente)
        db.commit()
        db.refresh(new_cliente)
        response = api_client.get(
            self.endpoint, params={"cliente_id": new_cliente.cliente_id}
        )
        assert response.status_code == 200

    def test_multiple_clientes(self, api_client: TestClient, db: Session):
        cliente_1 = models.Cliente(
            nombre="Piter", email="pan@peter.com", telefono="111-111-111"
        )
        cliente_2 = models.Cliente(
            nombre="Memo", email="memo@jaria.com", telefono="111-111-111"
        )
        db.add_all([cliente_1, cliente_2])
        db.commit()
        request_params = {"limit": 20, "offset": 0}
        response = api_client.get(self.endpoint, params=request_params)
        data = response.json()
        assert response.status_code == 200
        assert data["total"] > 0

    def test_validation(self, api_client: TestClient):
        path = f"{self.endpoint}/string"
        response = api_client.get(path)
        assert response.status_code == 422

    def test_not_found(self, api_client: TestClient):
        cliente_id = 11111111111111
        path = f"{self.endpoint}/{cliente_id}"
        response = api_client.get(path)
        assert response.status_code == 404

    def test_authorized(self):
        pass

    def test_forbidden(self):
        pass

    def test_rate_limiting(self):
        pass


class TestPost:
    endpoint = "/clientes"

    def test_new_valid(self, api_client: TestClient, valid_post_data: dict):
        response = api_client.post(self.endpoint, json=valid_post_data)
        created_cliente = response.json()
        created_time = datetime.fromisoformat(created_cliente["created_at"])
        current_time = datetime.now()
        one_mintue = timedelta(minutes=1)
        assert response.status_code == 200
        assert current_time - created_time < one_mintue
