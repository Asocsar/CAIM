import re


class Novels:
	characters = set()

	def __init__(self, text):
		self.text = text


	def clean(self):
		texto_entrada = self.text

		texto_entrada = texto_entrada.replace('Ô', '')
		texto_entrada = texto_entrada.replace("n't", '')
		texto_entrada = texto_entrada.replace('_', '')
		texto_entrada = texto_entrada.replace("'s", '')
		texto_entrada = re.sub("^\d+\s|\s\d+\s|\s\d+$", "", texto_entrada)
		texto_splited = texto_entrada.split(' ')
		texto_splited = list(filter(lambda x: len(list(x)) > 1 or x.upper() == 'I', texto_splited))

		texto_splited = list(filter(lambda x: len(x) == len([s for s in x if s.isalpha()]), texto_splited))

		texto_splited = ' '.join(list(texto_splited))

		if "mustn't" in texto_splited:
			print(texto_splited)

		return texto_splited


def noDigits(word: str) -> bool:
	for c in word:
		if c.isdigit():
			return False
	return True


def noRepeating(word: str) -> bool:
	char: chr = word[0]
	count: int = 0
	for c in word:
		if c == char:
			count += 1
			if count >= 3:
				return False
		else:
			char = c
			count = 0
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
		filteredText = list(filter(lambda word: len(word) > 1 or word == "a" or word == "i" or word == "A" or word == "I",
															 filteredText))
		filteredText = list(filter(noDigits, filteredText))
		filteredText = list(filter(noRepeating, filteredText))
		filteredText = list(filter(lambda w: w.isprintable(), filteredText))
		self.text = ' '.join(filteredText)
		return self.text


class Arxiv:

	def __init__(self, text):
		self.text = text
