# etsy-v3-oauth2-client

This project provides an Etsy v3 API client that utilizes OAuth2 for authentication. It offers various implementations catering to different use cases, building upon the simplest variant.

The available implementations are as follows:

* EtsyOAuth2Client in etsy_client.py:
    This is the foundational class responsible for handling the OAuth flow. Requires manual login.

* EtsyOAuth2ClientSelenium in etsy_selenium_client.py:
    This class utilizes Selenium to automate the process of filling in the username and password fields on the Etsy login page.

* EtsyClientRPCServer in etsy_rpc_server.py:
    This class starts a JSON|XML RPC server, eliminating the need to repeat the entire OAuth login and refresh process each and every time an Etsy API client is initialized.

* EtsyClientRPCServer in etsy_rpc_client_service.py:
    This class launches the RPC server (as a cross-platform service), enabling it to act as an RPC proxy object. This allows invoking RPC methods on the server service.
