import unittest

from backend import routes, util


class RoutesTest(unittest.TestCase):
    def test_use_token_no_token(self) -> None:
        self.assertFalse(util.use_token(routes.LoginRequest()))
        self.assertFalse(util.use_token(routes.LoginRequest(username="username")))
        self.assertFalse(util.use_token(routes.LoginRequest(password="password")))
        self.assertFalse(
            util.use_token(
                routes.LoginRequest(username="username", password="password")
            )
        )

    def test_use_token(self) -> None:
        self.assertFalse(
            util.use_token(routes.LoginRequest(token="token", username="username"))
        )
        self.assertFalse(
            util.use_token(routes.LoginRequest(token="token", password="password"))
        )
        self.assertFalse(
            util.use_token(
                routes.LoginRequest(
                    token="token", username="username", password="password"
                )
            )
        )
        self.assertTrue(util.use_token(routes.LoginRequest(token="token")))
