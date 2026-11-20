"""Sprint 1 live integration checks.

Run while the original server, protected server, and HTTP bridge are running.
These checks use real loopback TCP and HTTP connections.
"""

import json
import socket
import unittest
import urllib.error
import urllib.request


class SprintOneIntegrationTests(unittest.TestCase):
    def test_original_lab_vulnerability_is_preserved(self):
        with socket.create_connection(("127.0.0.1", 5001), timeout=2) as client:
            request = {
                "action": "check_balance",
                "username": "AKib",
            }
            client.sendall((json.dumps(request) + "\n").encode("utf-8"))
            response = json.loads(
                client.makefile("r", encoding="utf-8").readline()
            )
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["balance"], "50000")

    def test_direct_tcp_status(self):
        with socket.create_connection(("127.0.0.1", 5002), timeout=2) as client:
            client.sendall(b'{"action":"status"}\n')
            response = json.loads(
                client.makefile("r", encoding="utf-8").readline()
            )
        self.assertEqual(response["status"], "ok")
        self.assertTrue(response["tcp_connected"])

    def test_http_bridge_reaches_tcp_server(self):
        with urllib.request.urlopen(
            "http://127.0.0.1:8080/api/status",
            timeout=3,
        ) as response:
            payload = json.load(response)
        self.assertEqual(response.status, 200)
        self.assertTrue(payload["tcp_connected"])

    def test_http_bridge_rejects_unknown_path(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(
                "http://127.0.0.1:8080/api/not-allowed",
                timeout=3,
            )
        self.assertEqual(caught.exception.code, 404)

    def test_malformed_tcp_message_is_handled(self):
        with socket.create_connection(("127.0.0.1", 5002), timeout=2) as client:
            client.sendall(b"not-json\n")
            response = json.loads(
                client.makefile("r", encoding="utf-8").readline()
            )
        self.assertEqual(response["code"], "INVALID_REQUEST")


if __name__ == "__main__":
    unittest.main(verbosity=2)

