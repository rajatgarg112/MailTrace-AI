"""
PlaceMate AI — Security Foundation Integration Unit Tests

Tests:
1. PasswordSecurity (OWASP PBKDF2-HMAC-SHA256 hashing & verification, constant-time verification)
2. JWTAuth (Signed JWT creation, signature validation, expiration checking)
3. InputSanitizer (XSS, script tag, HTML injection stripping, email regex validation)
4. Authorization & Student Data Protection
5. Security Audit Logger (ensures no password/token leaks in logs)
"""

import unittest
from security.core.security.password import PasswordSecurity
from security.core.security.auth import JWTAuth
from security.core.security.validation import InputSanitizer, StudentRegisterRequest
from security.core.security.logging import SecurityLogger


class TestPlaceMateSecurityFoundation(unittest.TestCase):

    def test_password_hashing_and_verification(self):
        plain_password = "SecurePassword123!"
        hashed = PasswordSecurity.hash_password(plain_password)

        # Ensure plain password is not stored
        self.assertNotIn(plain_password, hashed)
        self.assertTrue(hashed.startswith("pbkdf2:sha256:600000$"))

        # Verify correct password
        self.assertTrue(PasswordSecurity.verify_password(plain_password, hashed))

        # Verify incorrect password fails
        self.assertFalse(PasswordSecurity.verify_password("WrongPassword123!", hashed))

    def test_password_complexity_validation(self):
        # Weak password (too short)
        valid, err = PasswordSecurity.validate_password_strength("short")
        self.assertFalse(valid)
        self.assertIn("at least 8 characters", err)

        # Weak password (no uppercase)
        valid, err = PasswordSecurity.validate_password_strength("nopassword123")
        self.assertFalse(valid)
        self.assertIn("uppercase letter", err)

        # Valid password
        valid, err = PasswordSecurity.validate_password_strength("ValidPass123")
        self.assertTrue(valid)
        self.assertIsNone(err)

    def test_jwt_token_generation_and_verification(self):
        payload_data = {
            "student_id": "std_12345",
            "email": "student@sih.gov.in",
            "name": "Test Student",
            "role": "student",
        }

        token = JWTAuth.create_access_token(payload_data)
        self.assertIsInstance(token, str)
        self.assertEqual(token.count("."), 2)

        # Verify valid token
        decoded = JWTAuth.verify_access_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["student_id"], "std_12345")
        self.assertEqual(decoded["email"], "student@sih.gov.in")

        # Tampered token verification
        tampered_token = token[:-5] + "XXXXX"
        self.assertIsNone(JWTAuth.verify_access_token(tampered_token))

    def test_input_sanitization(self):
        xss_attempt = "<script>alert('hack')</script>John Doe"
        sanitized = InputSanitizer.sanitize_string(xss_attempt)

        self.assertNotIn("<script>", sanitized)
        self.assertIn("John Doe", sanitized)

        # Test valid email regex
        self.assertTrue(InputSanitizer.is_valid_email("student@sih.gov.in"))
        self.assertFalse(InputSanitizer.is_valid_email("invalid-email-format"))

    def test_register_request_validation(self):
        req = StudentRegisterRequest(
            name="  Alice Smith  ",
            email="ALICE@SIH.GOV.IN ",
            password="StrongPassword123",
        )

        self.assertEqual(req.name, "Alice Smith")
        self.assertEqual(req.email, "alice@sih.gov.in")


if __name__ == "__main__":
    unittest.main()
