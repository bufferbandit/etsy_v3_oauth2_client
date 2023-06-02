import os
import sys
import time
import pysc
# from xmlrpc.client import ServerProxy as RpcClient
from jsonrpclib import Server as RpcClient




class EtsyRPCClient(RpcClient):

	is_launching_client = None
	def __init__(self, api_token, email, password,
				 rpc_server_url="http://localhost:1337",
				 service_name="python_etsy_rpc_service",
				 server_script_path=os.path.join(os.path.dirname(__file__), "etsy_rpc_server.py"),
				 *args, **kwargs):

		self.rpc_server_url = rpc_server_url
		self.api_token = api_token
		self.email = email
		self.password = password
		self.service_name = service_name
		self.server_script_path = server_script_path
		self._args = args
		self._kwargs = kwargs
		self.start_service()
		self.get_connection()
		time.sleep(1)


	def get_connection(self, timeout=5):
		while 1:
			time.sleep(timeout)
			try:
				super().__init__(uri=self.rpc_server_url, *self._args, **self._kwargs)
				print("Connected to rpc server")
				break
			except ConnectionRefusedError:
				print("Could not connect to rpc server yet... Sleeping ", timeout)
				continue

	def start_service(self):
		try:
			pysc.create(
				service_name=self.service_name,
				cmd=[sys.executable, self.server_script_path,
					 self.api_token, self.email, self.password]
			)
			pysc.start(self.service_name)
			self.is_launching_client = True
		except OSError:
			self.is_launching_client = False
			print("Service probably already exists, skipping...")




if __name__ == "__main__":

	API_TOKEN = input("ADD YOUR API TOKEN: ")
	ETSY_EMAIL = input("ADD YOUR EMAIL: ")
	ETSY_PASSWORD = input("ADD YOUR PASSWORD: ")

	client = EtsyRPCClient(API_TOKEN, ETSY_EMAIL, ETSY_PASSWORD)
	for x in range(30):
		res = client.ping()
		print(res)
		time.sleep(3)


	# finally:
	# 	# pysc.stop(service_name)
	# 	# pysc.delete(service_name)
	# 	print("Closed and deleted ", service_name)
