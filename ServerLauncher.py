import socket
import sys
from Server import Server

class ServerLauncher:

	def main(self):
		try:
			SERVER_PORT = int(sys.argv[1])
		except:
			print("[Usage: ServerLauncher.py Server_port]\n")

		rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		rtspSocket.bind(('', SERVER_PORT))
		rtspSocket.listen(5)

		while True:
			clientInfo = {'rtspSocket': rtspSocket.accept()}
			Server(clientInfo).run()


if __name__ == "__main__":
	(ServerLauncher()).main()
