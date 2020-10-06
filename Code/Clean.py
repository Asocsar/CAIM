
import re 

class Clean_novels:
    characters = set()

    def __init__(self, text):
        self.text = text

    def clean(self):
        texto_entrada = self.text

        texto_entrada = texto_entrada.replace('_', '')
        texto_entrada = texto_entrada.replace('Ô', '')
        texto_entrada = texto_entrada.replace("n't", '')
        texto_entrada = texto_entrada.replace("'s", '')
        texto_entrada = re.sub("^\d+\s|\s\d+\s|\s\d+$", "", texto_entrada)
        texto_splited = texto_entrada.split(' ')
        texto_splited = list(filter(lambda x: len(list(x)) > 1 or x.upper() == 'I', texto_splited))

        texto_splited = list(filter(lambda x: len(x) == len([s for s in x if s.isalpha()]) , texto_splited))
        


        texto_splited = ' '.join(list(texto_splited))

        if "mustn't" in texto_splited:
            print(texto_splited)


        return texto_splited

class Clean_news:

    def __init__(self, text):
        self.text = text



class Clean_axiv:


    def __init__(self, text):
        self.text = text