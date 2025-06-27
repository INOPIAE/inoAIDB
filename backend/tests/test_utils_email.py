import pytest
from unittest.mock import patch, MagicMock
from app.utils.email import send_email
from app.config import settings

@patch("utils.email.smtplib.SMTP_SSL")
def test_send_email_success(mock_smtp_ssl):
    mock_server = MagicMock()
    mock_smtp_ssl.return_value.__enter__.return_value = mock_server

    send_email(
        to="test@example.com",
        subject="Test Betreff",
        body="Test Inhalt"
    )

    mock_smtp_ssl.assert_called_once()
    mock_server.login.assert_called_once_with(settings.sender_email, settings.smtp_password)
    mock_server.sendmail.assert_called_once()
