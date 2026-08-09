import unittest

from app.routes.auth import hash_password, verify_password


class AuthModuleTests(unittest.TestCase):
    def test_password_hashing_and_verification(self):
        password = "SecurePass123!"
        hashed = hash_password(password)

        self.assertTrue(hashed.startswith("pbkdf2_sha256$"))
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrong-password", hashed))


if __name__ == "__main__":
    unittest.main()
