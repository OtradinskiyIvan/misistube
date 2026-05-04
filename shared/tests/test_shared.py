import io
import json
import logging
import unittest
from datetime import timedelta

import shared.config as config_module
import shared.exceptions as exceptions_module
import shared.logger as logger_module
import shared.security as security_module
from pydantic import SecretStr


class TestShared(unittest.TestCase):
    def test_config_base_settings_model_config(self):
        self.assertEqual(config_module.BaseSettings.model_config["extra"], "ignore")
        self.assertTrue(config_module.BaseSettings.model_config["case_sensitive"])

    def test_config_base_settings_validation(self):
        class TestSettings(config_module.BaseSettings):
            DATABASE_URL: str
            S3_ENDPOINT: str
            S3_ACCESS_KEY: SecretStr
            S3_SECRET_KEY: SecretStr
            S3_BUCKET_NAME: str

        settings = TestSettings(
            APP_NAME="misistube-test",
            DATABASE_URL="postgresql://user:pass@localhost:5432/testdb",
            S3_ENDPOINT="http://localhost:9000",
            S3_ACCESS_KEY="access-key",
            S3_SECRET_KEY="secret-key",
            S3_BUCKET_NAME="test-bucket",
        )

        self.assertEqual(settings.APP_NAME, "misistube-test")
        self.assertEqual(settings.DATABASE_URL, "postgresql://user:pass@localhost:5432/testdb")
        self.assertEqual(settings.S3_ENDPOINT, "http://localhost:9000")
        self.assertEqual(settings.S3_ACCESS_KEY.get_secret_value(), "access-key")
        self.assertEqual(settings.S3_SECRET_KEY.get_secret_value(), "secret-key")
        self.assertEqual(settings.S3_BUCKET_NAME, "test-bucket")

    def test_config_base_settings_missing_required(self):
        class TestSettings(config_module.BaseSettings):
            DATABASE_URL: str
            S3_ENDPOINT: str
            S3_ACCESS_KEY: SecretStr
            S3_SECRET_KEY: SecretStr
            S3_BUCKET_NAME: str

        with self.assertRaises(Exception):
            TestSettings(APP_NAME="missing-fields")

    def test_exceptions_attributes(self):
        error = exceptions_module.AppBaseError("boom", code="TEST_CODE", status_code=418)
        self.assertEqual(error.message, "boom")
        self.assertEqual(error.code, "TEST_CODE")
        self.assertEqual(error.status_code, 418)

        infra = exceptions_module.InfrastructureError("infra")
        self.assertEqual(infra.code, "INFRA_ERROR")
        self.assertEqual(infra.status_code, 500)

        auth = exceptions_module.AuthenticationError()
        self.assertEqual(auth.message, "Invalid credentials")
        self.assertEqual(auth.code, "AUTH_FAILED")
        self.assertEqual(auth.status_code, 401)

        validation = exceptions_module.ValidationAppError("bad request")
        self.assertEqual(validation.code, "VALIDATION_ERROR")
        self.assertEqual(validation.status_code, 400)

    def test_logger_json_formatter_and_correlation_id(self):
        logger = logger_module.get_logger("shared_test_logger", level="DEBUG")

        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logger_module.JSONFormatter())
        logger.logger.handlers.clear()
        logger.logger.addHandler(handler)
        logger.logger.propagate = False

        logger_module.correlation_id_var.set("test-correlation-id")
        logger.info("test message")

        output = stream.getvalue().strip()
        self.assertTrue(output)

        parsed = json.loads(output)
        self.assertEqual(parsed["service"], "shared_test_logger")
        self.assertEqual(parsed["correlation_id"], "test-correlation-id")
        self.assertEqual(parsed["message"], "test message")
        self.assertEqual(parsed["level"], "INFO")
        self.assertIn("timestamp", parsed)
        self.assertIn("module", parsed)

    def test_security_hash_and_verify_password(self):
        raw_password = "MyS3cretP@ss"
        hashed = security_module.hash_password(raw_password)
        self.assertIsInstance(hashed, str)
        self.assertTrue(security_module.verify_password(raw_password, hashed))
        self.assertFalse(security_module.verify_password("wrong-pass", hashed))

    def test_security_create_and_decode_jwt(self):
        secret = "s" * 32
        subject = "user123"
        token = security_module.create_jwt_token(subject, secret, expires_minutes=1)
        decoded = security_module.decode_jwt_token(token, secret)

        self.assertEqual(decoded["sub"], subject)
        self.assertIn("exp", decoded)
        self.assertIn("iat", decoded)

    def test_security_decode_jwt_invalid_secret(self):
        secret = "s" * 32
        another_secret = "o" * 32
        token = security_module.create_jwt_token("user123", secret, expires_minutes=1)

        with self.assertRaises(Exception):
            security_module.decode_jwt_token(token, another_secret)


if __name__ == "__main__":
    unittest.main()
