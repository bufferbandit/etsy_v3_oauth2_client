from functools import partial

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

		# TODO: Run this on a thread perhapse
		# TODO: It would be nice if this would
		#  	be contained in a context manager
		if verbose: print("Starting rpc server")
		self.rpc_server.serve_forever()



if __name__ == "__main__":
	options = webdriver.FirefoxOptions()
	options.add_argument("--headless")
	service = FirefoxService(GeckoDriverManager().install())
	driver = webdriver.Firefox(service=service, options=options)

	try:

		AUTO_CLOSE_BROWSER = True
		AUTO_REFRESH_TOKEN = True
		AUTO_START_AUTH = True
		VERBOSE = True
		HOST = "localhost"
		PORT = 5000

		API_TOKEN = input("ADD YOUR API TOKEN ")
		ETSY_EMAIL = input("ADD YOUR EMAIL ")
		ETSY_PASSWORD = input("ADD YOUR PASSWORD ")

		client = EtsyClientRPCServer(
			rpc_mode="json",
			rpc_addr=("127.0.0.1", 1337),
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
