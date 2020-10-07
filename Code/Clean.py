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

def noRepeats(word: str) -> bool
	return True

class News:

	def __init__(self, text: str):
		self.text = text

	def clean(self) -> str:

		filteredText = self.text.replace('_', ' ')
		filteredText = filteredText.replace(':', '')
		filteredText = filteredText.replace("n't", '')
		filteredText = filteredText.replace("'", ' ')
		filteredText = filteredText.replace('.', ' ').split()
		filteredText = filter(lambda word: len(word) > 1 or word == "a" or word == "i" or word == "A" or word == "I")
		filteredText = filter(noDigits, filteredText)
		filteredText = filter(noRepeats, filteredText)
		self.text = ' '.join(filteredText)
		return self.text


class Arxiv:

	def __init__(self, text):
		self.text = text
