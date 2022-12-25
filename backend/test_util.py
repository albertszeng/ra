import unittest

from backend import routes, util


class RoutesTest(unittest.TestCase):
    def test_use_token_no_token(self) -> None:
        self.assertFalse(util.use_token(routes.LoginOrRegisterRequest()))
        self.assertFalse(
            util.use_token(routes.LoginOrRegisterRequest(username="username"))
        )
        self.assertFalse(
            util.use_token(routes.LoginOrRegisterRequest(password="password"))
        )
        self.assertFalse(
            util.use_token(
                routes.LoginOrRegisterRequest(username="username", password="password")
            )
        )

    def test_use_token(self) -> None:
        self.assertFalse(
            util.use_token(
                routes.LoginOrRegisterRequest(token="token", username="username")
            )
        )
        self.assertFalse(
            util.use_token(
                routes.LoginOrRegisterRequest(token="token", password="password")
            )
        )
        self.assertFalse(
            util.use_token(
                routes.LoginOrRegisterRequest(
                    token="token", username="username", password="password"
                )
            )
        )
        self.assertTrue(util.use_token(routes.LoginOrRegisterRequest(token="token")))
