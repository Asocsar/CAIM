
class Clean_novels:
    characters = set()

    def __init__(self, text):
        self.text = text

    def clean(self):
        texto_entrada = self.text

        texto_entrada = texto_entrada.replace('_', '')
        texto_entrada = texto_entrada.replace('Ô', '')

        texto_splited = texto_entrada.split(' ')
        texto_splited = list(filter(lambda x: len(x) > 1 or x.upper() == 'I', texto_splited))
        texto_splited = ' '.join(filter(lambda x: len(x) == len([s for s in x if s.isalpha()]) , texto_splited))
        


        return texto_splited

class Clean_news:

    def __init__(self, text):
        self.text = text



class Clean_axiv:


    def __init__(self, text):
        self.text = text