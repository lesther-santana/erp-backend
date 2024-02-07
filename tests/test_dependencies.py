from app.endpoints.dependencies.password import Argon2Hashser
from app.endpoints.dependencies.auth import create_token, decode_token


class TestPasswordHasher:
    def test_create_hash(self):
        password = "coconutLemonade"
        hashed_password = Argon2Hashser.create_hash(password)
        assert isinstance(hashed_password, str)
        assert hashed_password != password

    def test_valid_password(self):
        password = "cococococ"
        hashed_password = Argon2Hashser.create_hash(password)
        assert Argon2Hashser.verify(hashed_password, password)

    def test_invalid_password(self):
        password = "coconutLemonade"
        other_password = "foobarbaz"
        other_password_hash = Argon2Hashser.create_hash(other_password)
        assert not Argon2Hashser.verify(other_password_hash, password)


class TestToken:
    def test_create_valid_token(self):
        token = create_token("cococococo", exp_time_delta=1)
        assert token

    def test_decode_valid_token(self):
        sub = "asafasfasasf"
        token = create_token(sub, exp_time_delta=15)
        parsed_token = decode_token(token.access_token)
        assert sub == parsed_token.get("sub")
