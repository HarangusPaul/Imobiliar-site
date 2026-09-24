from core.security import generate_numeric_code, hash_secret, mask_phone, secrets_match


def test_generated_code_has_requested_length_and_is_numeric():
    code = generate_numeric_code(6)
    assert len(code) == 6 and code.isdigit()


def test_hashed_secret_round_trips_and_is_salt_scoped():
    hashed = hash_secret("123456", salt="otp:+40721234567")
    assert secrets_match("123456", hashed, salt="otp:+40721234567")
    assert not secrets_match("123456", hashed, salt="otp:+40700000000")
    assert "123456" not in hashed


def test_mask_phone_hides_the_middle():
    assert mask_phone("+40721234567") == "+40*******67"
