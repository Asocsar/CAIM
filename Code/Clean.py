class Novels:
	characters = set()

	def __init__(self, text):
		self.text = text

	def clean(self):
		self.text = self.text.replace('_', '')


class News:

	def __init__(self, text: str):
		self.text = text

	def clean(self) -> str:
		print('Before: ' + self.text)
		filteredText = self.text.split()

		for i, word in enumerate(filteredText):
			isAValidWord = True
			for char in word:
				if char.isdigit():
					isAValidWord = False
			if not isAValidWord:
				del filteredText[i]
		self.text = ' '.join(filteredText)
		print('After: ' + self.text)
		return self.text


class Arxiv:

	def __init__(self, text):
		self.text = text
