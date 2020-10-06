class CleanNews:
	text = ""
	def __init__(self, text):
		self.text = text

	def clean(text):
		filtered = {}
		filteredText = text.split(' ')
		# Insert operation for a document with fields' path' and 'text'
		# ldocs.append({'_op_type': 'index', '_index': index, 'path': f, 'text': text})
		for i, word in enumerate(filteredText):
			isAValidWord = True
			for char in word:
				if char.isdigit():
					isAValidWord = False
			if not isAValidWord:
				del filteredText[i]
		print(f'')