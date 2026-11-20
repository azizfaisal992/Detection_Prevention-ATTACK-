"""Live integration checks for authenticated protected banking operations."""

import json
import socket
import unittest
import urllib.error
import urllib.request
from pathlib import Path

TCP_ADDRESS = ("127.0.0.1", 5002)
BRIDGE_URL = "http://127.0.0.1:8080"
SESSIONS_FILE = Path(__file__).parents[1] / "backend" / "data" / "sessions.json"
ACCOUNTS_FILE = Path(__file__).parents[1] / "backend" / "data" / "accounts.json"


def tcp_request(payload):
    with socket.create_connection(TCP_ADDRESS, timeout=3) as client:
        client.sendall((json.dumps(payload) + "\n").encode("utf-8"))
        return json.loads(client.makefile("r", encoding="utf-8").readline())


def http_post(path, payload):
    request = urllib.request.Request(
        f"{BRIDGE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=4) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


class SprintTwoIntegrationTests(unittest.TestCase):
    def test_invalid_password_is_denied(self):
        response = tcp_request({
            "action": "login",
            "username": "demo.rahim",
            "password": "incorrect-password",
        })
        self.assertEqual(response["status"], "error")
        self.assertEqual(response["code"], "INVALID_CREDENTIALS")
        self.assertNotIn("session_token", response)

    def test_valid_login_own_balance_and_logout(self):
        login = tcp_request({
            "action": "login",
            "username": "demo.rahim",
            "password": "Taka@2025",
        })
        self.assertEqual(login["status"], "ok")
        token = login["session_token"]
        try:
            balance = tcp_request({
                "action": "check_balance",
                "session_token": token,
            })
            self.assertEqual(balance["status"], "ok")
            self.assertEqual(balance["username"], "demo.rahim")
            self.assertEqual(balance["balance"], "248500.00")

            stored_sessions = json.loads(SESSIONS_FILE.read_text(encoding="utf-8"))
            self.assertNotIn(token, stored_sessions)
            self.assertNotIn(token, SESSIONS_FILE.read_text(encoding="utf-8"))
        finally:
            logout = tcp_request({"action": "logout", "session_token": token})
        self.assertEqual(logout["status"], "ok")

        denied = tcp_request({
            "action": "check_balance",
            "session_token": token,
        })
        self.assertEqual(denied["code"], "INVALID_SESSION")

    def test_account_identity_mismatch_is_denied(self):
        login = tcp_request({
            "action": "login",
            "username": "demo.rahim",
            "password": "Taka@2025",
        })
        token = login["session_token"]
        try:
            response = tcp_request({
                "action": "check_balance",
                "session_token": token,
                "username": "demo.nadia",
            })
            self.assertEqual(response["status"], "error")
            self.assertEqual(response["code"], "ACCESS_DENIED")
            self.assertNotIn("balance", response)
        finally:
            tcp_request({"action": "logout", "session_token": token})

    def test_http_bridge_banking_workflow(self):
        status, login = http_post("/api/login", {
            "username": "demo.nadia",
            "password": "Nadia@2025",
        })
        self.assertEqual(status, 200)
        token = login["session_token"]
        try:
            status, balance = http_post("/api/balance", {"session_token": token})
            self.assertEqual(status, 200)
            self.assertEqual(balance["username"], "demo.nadia")
            self.assertEqual(balance["balance"], "175250.50")
        finally:
            status, result = http_post("/api/logout", {"session_token": token})
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "ok")

    def test_protected_accounts_do_not_store_plaintext_passwords(self):
        contents = ACCOUNTS_FILE.read_text(encoding="utf-8")
        self.assertNotIn("Taka@2025", contents)
        self.assertNotIn("Nadia@2025", contents)
        accounts = json.loads(contents)
        self.assertTrue(all("password_hash" in account for account in accounts.values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
