import os
import sys
import time
import pysc

from jsonrpclib import Server as JSONRpcClient
from xmlrpc.client import ServerProxy as XMLRpcClient


class EtsyRPCBaseClient:
	is_launching_client = None

	def __init__(self, api_token, email, password,
				 rpc_address_host="localhost",
				 rpc_address_port=1337,
				 mode="json",
				 service_name="Python etsy api service",
				 launching_client_connect_timeout=5,
				 server_script_path=os.path.join(os.path.dirname(__file__), "etsy_rpc_server.py"),
				 try_install_service=True,
				 try_start_service=True,
				 try_stop_existing_service=False,
				 try_remove_existing_service=False,
				 *args, **kwargs):

		self.try_install_service = try_install_service
		self.try_start_service = try_start_service
		self.try_stop_existing_service = try_stop_existing_service
		self.try_remove_existing_service = try_remove_existing_service
		self.mode = mode
		self.rpc_address_host = rpc_address_host
		self.rpc_address_port = rpc_address_port
		self.rpc_server_url = "http://" + rpc_address_host + ":" + str(rpc_address_port)
		self.api_token = api_token
		self.email = email
		self.password = password
		self.service_name = service_name
		self.launching_client_connect_timeout = launching_client_connect_timeout
		self.server_script_path = server_script_path
		self._args = args
		self._kwargs = kwargs
		self.try_start_or_install_service()
		self.try_stop_or_remove_service()
		self.get_connection()
		if self.is_launching_client:
			time.sleep(launching_client_connect_timeout)

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

	def try_start_or_install_service(self):
		if self.try_install_service:
			try:
				pysc.create(
					service_name=self.service_name,
					cmd=[sys.executable, self.server_script_path,
						 self.api_token, self.email, self.password,
						 self.rpc_address_host, str(self.rpc_address_port), self.mode]
				)
				self.is_launching_client = True
				print("Service created")
			except OSError:
				self.is_launching_client = False
				print("Service probably already exists, skipping...")

		if self.try_start_service:
			try:
				pysc.start(self.service_name)
				print("Service started")
			except OSError:
				print("Could not start service")

	def try_stop_or_remove_service(self):
		if self.try_stop_existing_service:
			try:
				pysc.stop(self.service_name)
				print("Service stopped")
			except OSError:
				print("Could not stop service")

		if self.try_remove_existing_service:
			try:
				pysc.delete(self.service_name)
				print("Service deleted")
			except OSError:
				print("Could not delete service")





class EtsyRPCClientXML(EtsyRPCBaseClient, XMLRpcClient):
	pass


class EtsyRPCClientJSON(EtsyRPCBaseClient, JSONRpcClient):
	pass


if __name__ == "__main__":

	MODE = "json"

	if MODE == "json":
		Client = EtsyRPCClientJSON

	elif MODE == "xml":
		Client = EtsyRPCClientXML

	API_TOKEN = input("ADD YOUR API TOKEN: ")
	ETSY_EMAIL = input("ADD YOUR EMAIL: ")
	ETSY_PASSWORD = input("ADD YOUR PASSWORD: ")

	client = Client(API_TOKEN, ETSY_EMAIL, ETSY_PASSWORD,
					"localhost", 1337, MODE,
					launching_client_connect_timeout=20)
	for x in range(30):
		res = client.ping()
		print(res)
		time.sleep(3)
