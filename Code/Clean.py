class Novels:
	characters = set()

	def __init__(self, text):
		self.text = text

	def clean(self):
		self.text = self.text.replace('_', '')


def noDigits(word: str) -> bool:
	for c in word:
		if c.isdigit():
			return False
	return True

class News:

	def __init__(self, text: str):
		self.text = text

	def clean(self) -> str:
		filteredText = filter(noDigits, self.text.split())
		self.text = ' '.join(filteredText)
		return self.text


class Arxiv:

	def __init__(self, text):
		self.text = text
