
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_password_hashing():
    password = "ContohPasswordAman123!"

    hashed = hash_password(password)

    print("[1] PASSWORD HASHING")
    print("Hash berhasil dibuat:", bool(hashed))
    print("Hash menggunakan Argon2:", hashed.startswith("$argon2"))

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("PasswordSalah123!", hashed)

    print("Password verification: PASSED")


def test_jwt():
    user_id = 1

    print("\n[2] JWT")

    token = create_access_token(user_id)

    print("JWT berhasil dibuat:", bool(token))

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == str(user_id)

    print("JWT verification: PASSED")

    invalid_payload = decode_access_token("token-tidak-valid")

    assert invalid_payload is None

    print("Invalid token rejection: PASSED")


if __name__ == "__main__":
    test_password_hashing()
    test_jwt()

    print("\nSemua security tests berhasil!")
