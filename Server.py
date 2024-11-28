import socket
import threading
from random import randint
from RTPPacker import RTPPacker
from VideoHandler import VideoHandler

class Server:
	SETUP = 'SETUP'
	PLAY = 'PLAY'
	PAUSE = 'PAUSE'
	TEARDOWN = 'TEARDOWN'

	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT

	OK_200 = 0
	FILE_NOT_FOUND_404 = 1
	CON_ERR_500 = 2

	clientInfo = {}

	def __init__(self, client_info):
		self.clientInfo = client_info

	def run(self):
		threading.Thread(target=self.recvRTSPRequest).start()

	def recvRTSPRequest(self):
		connSocket = self.clientInfo['rtspSocket'][0]
		while True:
			data = connSocket.recv(256)
			if data:
				print("Data received:\n" + data.decode("utf-8"))
				self.processRtspRequest(data.decode("utf-8"))

	def processRtspRequest(self, data):
		"""Process RTSP request sent from the client."""
		request = data.split('\n')
		line1 = request[0].split(' ')
		requestType = line1[0]

		filename = line1[1]
		seq = request[1].split(' ')

		if requestType == self.SETUP:
			if self.state == self.INIT:
				print("processing SETUP\n")

				try:
					self.clientInfo['videoStream'] = VideoHandler(filename)
					self.state = self.READY
				except IOError:
					self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])

				self.clientInfo['session'] = randint(100000, 999999)
				self.replyRtsp(self.OK_200, seq[1])
				self.clientInfo['rtpPort'] = request[2].split(' ')[3]

		elif requestType == self.PLAY:
			if self.state == self.READY:
				print("processing PLAY\n")
				self.state = self.PLAYING

				self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				self.replyRtsp(self.OK_200, seq[1])

				self.clientInfo['event'] = threading.Event()
				self.clientInfo['worker'] = threading.Thread(target=self.sendRtp)
				self.clientInfo['worker'].start()

		elif requestType == self.PAUSE:
			if self.state == self.PLAYING:
				print("processing PAUSE\n")

				self.state = self.READY
				self.clientInfo['event'].set()
				self.replyRtsp(self.OK_200, seq[1])

		elif requestType == self.TEARDOWN:
			print("processing TEARDOWN\n")

			self.clientInfo['event'].set()
			self.replyRtsp(self.OK_200, seq[1])
			self.clientInfo['rtpSocket'].close()

	def sendRtp(self):
		"""Send RTP packets over UDP."""
		while True:
			self.clientInfo['event'].wait(0.05)

			if self.clientInfo['event'].isSet():
				break

			data = self.clientInfo['videoStream'].nextFrame()
			if data:
				frameNumber = self.clientInfo['videoStream'].frameNbr()
				try:
					address = self.clientInfo['rtspSocket'][1][0]
					port = int(self.clientInfo['rtpPort'])
					self.clientInfo['rtpSocket'].sendto(self.makeRTP(data, frameNumber), (address, port))
				except:
					self.clientInfo['event'].set()
					self.clientInfo['rtpSocket'].close()

	def makeRTP(self, payload, frame_number):
		version = 2
		padding = 0
		extension = 0
		cc = 0
		marker = 0
		pt = 26
		seqnum = frame_number
		ssrc = 0

		rtpPacket = RTPPacker()

		rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)

		return rtpPacket.getPacket()

	def replyRtsp(self, code, seq):
		if code == self.OK_200:
			reply = 'RTSP/1.0 200 OK\nCSeq: ' + seq + '\nSession: ' + str(self.clientInfo['session'])
			connSocket = self.clientInfo['rtspSocket'][0]
			connSocket.send(reply.encode())

		elif code == self.FILE_NOT_FOUND_404:
			print("404 NOT FOUND")

		elif code == self.CON_ERR_500:
			print("500 CONNECTION ERROR")
