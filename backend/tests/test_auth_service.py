from app.core.auth.models import User, UserRole
from app.core.auth.service import create_access_token, decode_token, hash_password, verify_password


def test_password_hash_roundtrip():
    password = "VerySecurePass123"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_access_token_roundtrip():
    user = User(
        email="student@example.com",
        password_hash="hashed",
        full_name="Student Example",
        role=UserRole.STUDENT,
        locale="de",
        is_active=True,
    )

    token_response = create_access_token(user)
    payload = decode_token(token_response.access_token)

    assert token_response.token_type == "bearer"
    assert payload.role == UserRole.STUDENT.value
    assert payload.sub == str(user.id)