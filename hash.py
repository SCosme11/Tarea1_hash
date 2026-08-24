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
    ceros = 32 - (longitud % 32)
    men_bin += "0" * ceros #agrego padding
    men_bin += bin(longitud)[2:].zfill(32) #agrego longitud de mensaje original
    return men_bin

def procesar(men_bin, rondas):
    h = "01101010000010011110011001100111" #estado interno inicial h0, primeros 32 bits parte fraccionaria raíz de 2
    for i in range(0, len(men_bin), 32):
        bloque = men_bin[i:i+32]
        h_num = int(h, 2)
        m_num = int(bloque, 2) #convertimos a números para que sean más sencillas las operaciones
        for j in range(rondas):
            # 1. Suma modular usando la ronda (j)
            mezcla = (h_num + m_num + j) % 2**32
            # 2. XOR con la constante
            mezcla = mezcla ^ 0x55555555 #01010101
            
            # 3. Rotación de 3 posiciones
            mezcla = ((mezcla << 3) % 2**32) | (mezcla >> 29)
            
            # 4. Actualizamos el bloque para la siguiente ronda
            m_num = mezcla
        h_num = (h_num + mezcla) % 2**32
        h = bin(h_num)[2:].zfill(32)
    resultado_final = hex(h_num)[2:].zfill(8)
    return resultado_final

def mi_hash(texto):
    binario_inicial = char_a_bin(texto)
    binario_con_padding = agregar_padding(binario_inicial)
    return procesar(binario_con_padding, 8)

hash_1 = mi_hash("gato")
hash_2 = mi_hash("pato")

print("Hash de 'gato':", hash_1)
print("Hash de 'pato':", hash_2)