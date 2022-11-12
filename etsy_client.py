import socketserver
import urllib.parse
import http.server
import webbrowser
import threading
import requests
import logging
import hashlib
import urllib
import pprint
import base64
import random
import signal
import string
import sched
import time
import json
import os

AUTO_REFRESH_TOKEN = False
AUTO_CLOSE = True
VERBOSE = True
HOST = "localhost"
PORT = 5000

API_TOKEN = "YOUR_API_TOKEN"
contexts = ["email_r", "shops_r", "profile_r", "transactions_r"]


class EtsyOAuth2Client:
	def __init__(self, api_token, host, port, contexts,
	             auto_close_browser=True, auto_refresh_token=False, verbose=True):
		# Construct and initialize the variables needed for the OAuth flow
		self.auto_close_browser = auto_close_browser
		self.api_token = api_token
		self.host = host
		self.port = port
		self.contexts = contexts
		self.verbose = verbose

		self.refresh_token_timer = None
		self.auto_refresh_token = auto_refresh_token

		# Generate attributes needed for the OAuth flow
		self.contexts_urlencoded = "%20".join([context + "_r" if not context.endswith("_r") else context for context in contexts])
		self.base_url = f"http://{self.host}:{self.port}"
		self.code_verifier = self.base64_url_encode(os.urandom(32))
		self.state = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(7 - 1))
		self.code_challenge = self.base64_url_encode(hashlib.sha256(self.code_verifier.encode("utf-8")).digest())
		self.redirect_uri = self.base_url + "/callback"

	@classmethod
	def base64_url_encode(self, inp):
		return base64.b64encode(inp) \
			.decode("utf-8") \
			.replace("+", "-") \
			.replace("/", "_") \
			.replace("=", "")


	@property
	def auto_refresh_token(self):
		return self._auto_refresh_token

	@auto_refresh_token.setter
	def auto_refresh_token(self, value):
		if not value and self.refresh_token_timer is not None:
			if self.verbose: print("Cancelling refresh token timer")
			self.refresh_token_timer.cancel()
		self.refresh_token_timer = None
		self._auto_refresh_token = value

	def open_oauth_request(self):
		auth_url = f"https://www.etsy.com/oauth/connect" \
		           f"?response_type=code" \
		           f"&redirect_uri={self.redirect_uri}" \
		           f"&scope={self.contexts_urlencoded}" \
		           f"&client_id={self.api_token}" \
		           f"&state={self.state}" \
		           f"&code_challenge={self.code_challenge}" \
		           f"&code_challenge_method=S256"

		if self.verbose: print("Opening browser to authenticate url: " + auth_url)
		webbrowser.open(auth_url)


	def receive_oauth_callback(self):
		parent_context = self
		tokens = {}
		class OAuthServerHandler(http.server.BaseHTTPRequestHandler):
			def log_message(self, format, *args): pass
			def do_GET(self):
				nonlocal tokens
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()

				query_parameters = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
				parent_context.code = query_parameters["code"][0]
				parent_context.state = query_parameters["state"][0]

				res = requests.post("https://api.etsy.com/v3/public/oauth/token",
				        headers={"Content-Type": "application/json"}, json={
						"grant_type": "authorization_code",
						"client_id": parent_context.api_token,
						"redirect_uri": parent_context.redirect_uri,
						"code": parent_context.code,
						"code_verifier": parent_context.code_verifier
					})
				tokens = res.json()
				message = "Successfully retrieved tokens" if res.status_code == 200 \
					else "Failed to retrieve tokens"
				if parent_context.verbose: print(message, res.status_code, tokens)
				self.wfile.write(bytes(
					f"<html>"
						f"<body " + ("onload=window.top.close()" if {parent_context.auto_close_browser} else "") + ">"
							f"<h1>{message}</h1>"
							f"<p>{res.status_code}</p>"
							f"<pre>{json.dumps(tokens, indent=4)}</pre>"
						f"</body>"
					f"</html>", "utf-8"))
				self.server.server_close()
				return
		try:http.server.HTTPServer((self.host, self.port), OAuthServerHandler).serve_forever()
		except OSError:pass # For some strange reason something still tries to write to the socket after closing server
		return tokens


	def get_access_token(self):
		self.open_oauth_request()
		tokens = self.receive_oauth_callback()
		self.access_token = tokens["access_token"]
		self.refresh_token = tokens["refresh_token"]
		self.expires_in = tokens["expires_in"]

	def stop_auto_refreshing_token(self):
		self.auto_refresh_token = False

	def start_auto_refreshing_token(self):
		if self.refresh_token_timer: self.refresh_token_timer.cancel()
		self.refresh_token_timer = threading.Timer(int(self.expires_in), function=self.get_refresh_token)
		self.refresh_token_timer.start()
		if self.verbose: print("New timer started with interval", self.refresh_token_timer.interval)

	def get_refresh_token(self):
		res = requests.post("https://api.etsy.com/v3/public/oauth/token",
		    headers={"Content-Type": "application/json"}, json={
				"grant_type": "refresh_token",
				"client_id": self.api_token,
				"refresh_token": self.refresh_token
			})
		tokens = res.json()

		self.access_token = tokens["access_token"]
		self.refresh_token = tokens["refresh_token"]
		self.expires_in = tokens["expires_in"]

		if self.verbose: print("Succesfully refreshed token", self.access_token, self.refresh_token, self.expires_in)
		if self.auto_refresh_token:
			self.start_auto_refreshing_token()


if __name__ == "__main__":
	print(AUTO_REFRESH_TOKEN)
	client = EtsyOAuth2Client(API_TOKEN, HOST, PORT, contexts, AUTO_CLOSE, AUTO_REFRESH_TOKEN, VERBOSE)

	print("Getting access token")
	client.get_access_token()

	print("Getting refresh token")
	client.get_refresh_token()

	print("Refreshing is threaded and non blockingly running in the background")
	client.start_auto_refreshing_token()

	input()

	input("Press enter to stop refreshing")
	client.start_auto_refreshing_token()

	print("Stopped refreshing")
