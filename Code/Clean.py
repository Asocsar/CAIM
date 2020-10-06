class Novels:
	characters = set()

	def __init__(self, text):
		self.text = text

	def clean(self):
		self.text = self.text.replace('_', '')


class News:

	def __init__(self, text):
		self.text = text


class Arxiv:

	def __init__(self, text):
		self.text = text
