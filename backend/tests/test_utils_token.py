import pytest
import secrets
from unittest import mock
from app.utils.token import generate_unique_token
from app.models import PaymentToken


def test_generate_unique_token_creates_token(db):
    token = generate_unique_token(db, PaymentToken)
    assert isinstance(token, str)
    assert len(token) >= 32  # token_urlsafe kann länger als 32 sein

def test_generate_unique_token_avoids_duplicates(db):
    duplicate = secrets.token_urlsafe(32)
    db.add(PaymentToken(token=duplicate))
    db.commit()

    with mock.patch("secrets.token_urlsafe", side_effect=[duplicate, "unique_token_123"]):
        token = generate_unique_token(db, PaymentToken)
        assert token == "unique_token_123"

def test_generate_unique_token_raises_after_max_attempts(db):
    db.add(PaymentToken(token="dupe_token"))
    db.commit()

    with mock.patch("secrets.token_urlsafe", return_value="dupe_token"):
        with pytest.raises(Exception, match="Failed to generate unique token"):
            generate_unique_token(db, PaymentToken, max_attempts=5)
