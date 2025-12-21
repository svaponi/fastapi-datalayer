from app.auth.utils import hash_password, verify_hashed_password


def test_hash_and_verify_password():
    _hashed = hash_password("secret")
    assert verify_hashed_password("secret", _hashed)
    assert not verify_hashed_password("nope", _hashed)
