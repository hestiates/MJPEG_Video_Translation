class VideoHandler:
	def __init__(self, filename):
		self.filename = filename
		try:
			self.file = open(filename, 'rb')
		except:
			raise IOError
		self.frameNum = 0
		
	def nextFrame(self):
		"""Get next frame."""
		data = self.file.read(5)
		if data:
			frameLength = int(data)
			print(frameLength)
			data = self.file.read(frameLength)
			self.frameNum += 1
		return data

	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum
