import socketserver
import urllib.parse
import http.server
import webbrowser
import requests
import logging
import hashlib
import urllib
import pprint
import base64
import random
import signal
import string
import json
import os

PORT = 5000
AUTO_CLOSE = True
VERBOSE = False
API_TOKEN = "YOUR_API_TOKEN"
contexts = ["email_r", "shops_r", "profile_r", "transactions_r"]
contexts_urlencoded = "%20".join([context + "_r" if not context.endswith("_r") else context for context in contexts])




class EtsyOAuth:
	def __init__(self, api_token, host, port, contexts, autoclose=True, verbose=True):
		# Construct and initialize the variables needed for the OAuth flow
		self.api_token = api_token
		self.host = host
		self.port = port
		self.contexts = contexts
		self.autoclose = autoclose
		self.verbose = verbose

		# Generate attributes needed for the OAuth flow
		self.contexts_urlencoded = "%20".join([context + "_r" if not context.endswith("_r") else context for context in contexts])
		self.base_url = f"http://{self.host}:{self.port}"
		self.code_verifier = self.base64_url_encode(os.urandom(32))
		self.state = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(7 - 1))
		self.code_challenge = self.base64_url_encode(hashlib.sha256(self.code_verifier.encode("utf-8")).digest())
		self.redirect_uri = self.base_url + "/callback"

	def base64_url_encode(self, inp):
		return base64.b64encode(inp) \
			.decode("utf-8") \
			.replace("+", "-") \
			.replace("/", "_") \
			.replace("=", "")

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

	def run_oauth_server(self):
		parent_context = self
		class OAuthServerHandler(http.server.BaseHTTPRequestHandler):
			def log_message(self, format, *args): pass
			def do_GET(self):
				global tokens
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
						f"<body " + ("onload=window.top.close()" if {parent_context.autoclose} else "") + ">"
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

if __name__ == "__main__":
	client = EtsyOAuth(API_TOKEN, "localhost", PORT, contexts, AUTO_CLOSE, VERBOSE)
	client.open_oauth_request()
	tokens = client.run_oauth_server()
	print(tokens)
