import sys
from functools import partial

from pysc import event_stop
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from webdriver_manager.firefox import GeckoDriverManager
from etsy_client import EtsyOAuth2Client
from selenium.webdriver.support import expected_conditions as EC

import os

from etsy_selenium_client import EtsyOAuth2ClientSelenium



def get_input(prompt):
    # Check if the input is provided as a command line argument
    if len(sys.argv) > 1:
        return sys.argv.pop(1)

    # Check if the input is available in the environment variables
    env_variable = os.getenv(prompt.upper())
    if env_variable:
        return env_variable

    # If the input is still not available, ask for user input
    return input(prompt)


class EtsyClientRPCServer(EtsyOAuth2ClientSelenium):
	def __init__(self, rpc_mode="json", rpc_addr=None, rpc_server=None,verbose=True, *args, **kwargs):
		if rpc_server:
			self.rpc_server = rpc_server
		else:
			if rpc_mode == "xml":
				if verbose: print("Selected xml rpc server")
				from xmlrpc.server import SimpleXMLRPCServer
				self.rpc_server = SimpleXMLRPCServer(rpc_addr)
			elif rpc_mode == "json":
				if verbose: print("Selected json rpc server")
				from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
				self.rpc_server = SimpleJSONRPCServer(rpc_addr)


		super().__init__(
			register_reference_function=self.rpc_server.register_function,
			prefix="", verbose=verbose,
			*args, **kwargs
		)

		@event_stop
		def stop():
			self.rpc_server.server_close()
			if self.driver:
				self.driver.quit()
			exit()


		# TODO: Run this on a thread perhapse
		# TODO: It would be nice if this would
		#  	be contained in a context manager
		try:
			if verbose: print("Starting rpc server at ", *rpc_addr)
			self.rpc_server.serve_forever()
		finally:
			if verbose: print("Closed rpc server at ", *rpc_addr)
			self.rpc_server.server_close()



if __name__ == "__main__":

	HEADLESS = True
	AUTO_CLOSE_BROWSER = True
	AUTO_REFRESH_TOKEN = True
	AUTO_START_AUTH = True
	VERBOSE = True
	HOST = "localhost"
	PORT = 5000

	API_TOKEN = get_input("ADD YOUR API TOKEN: ")
	ETSY_EMAIL = get_input("ADD YOUR EMAIL: ")
	ETSY_PASSWORD = get_input("ADD YOUR PASSWORD: ")
	RPC_ADDRESS_HOST = get_input("RPC ADDRESS HOST: ") or "localhost"
	RPC_ADDRESS_PORT = int(get_input("RPC ADDRESS PORT: ")) or 1337
	RPC_SERVER_MODE = get_input("RPC SERVER MODE: ") or "json"




	options = webdriver.FirefoxOptions()
	if HEADLESS: options.add_argument("--headless")
	service = FirefoxService(GeckoDriverManager().install())
	driver = webdriver.Firefox(service=service, options=options)

	try:

		client = EtsyClientRPCServer(
			rpc_mode=RPC_SERVER_MODE,
			rpc_addr=(RPC_ADDRESS_HOST, int(RPC_ADDRESS_PORT)),
			api_token=API_TOKEN,
			email=ETSY_EMAIL, password=ETSY_PASSWORD,
			host=HOST, port=PORT,
			auto_close_browser=AUTO_CLOSE_BROWSER,
			auto_refresh_token=AUTO_REFRESH_TOKEN,
			verbose=VERBOSE, auto_start_auth=AUTO_START_AUTH,
			reference_file_path=os.path.join(
				os.path.dirname(__file__), "./", "api_reference.json"),
			driver=driver
		)
		print(client.ping())


	finally:driver.quit()
