# Utilizo 32 bits 

#función que pasa cadenas de caracteres a binario
def char_a_bin(texto):
    men_bin = ""
    for c in texto:
        men_bin += bin(ord(c))[2:].zfill(8) #pasa a ASCII y después a binario. Hay que quitar contenido y agregar un bit extra para limpiar el output de la función
    return men_bin

def agregar_padding(men_bin):
    longitud = len(men_bin)
    men_bin += "1"
    ceros = 32 - (len(men_bin) % 32)
    men_bin += "0" * ceros #agrego padding
    men_bin += bin(longitud)[2:].zfill(32) #agrego longitud de mensaje original
    return men_bin