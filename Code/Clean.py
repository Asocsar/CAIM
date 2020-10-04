
class Clean_novels:
    characters = set()

    def __init__(self, text):
        self.text = text

    def clean(self):
        self.text = self.text.replace('_', '')

class Clean_news:

    def __init__(self, text):
        self.text = text



class Clean_axiv:


    def __init__(self, text):
        self.text = text