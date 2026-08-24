from hash import *
import statistics
import random
import string

def medir_avalancha_un_mensaje(mensaje, rondas):
    mensaje_bin = char_a_bin(mensaje)
    hash_original = procesar(agregar_padding(mensaje_bin), rondas)
    
    K = len(mensaje_bin)
    distancias = []
    
    for i in range(K):
        # Voltear un solo bit
        nuevo_bit = "0" if mensaje_bin[i] == "1" else "1"
        mensaje_alterado = mensaje_bin[:i] + nuevo_bit + mensaje_bin[i+1:]
        
        # Generar nuevo hash
        hash_nuevo = procesar(agregar_padding(mensaje_alterado), rondas)
        
        # Contar distancia de Hamming
        dhamming = 0
        for b1, b2 in zip(hash_original, hash_nuevo):
            if b1 != b2:
                dhamming += 1
        distancias.append(dhamming)
        
    return distancias

mensajes = [
    # Mensajes muy cortos
    "a", "1", "ok", "no", "sol",
    # Textos en español
    "hola mundo", "criptografia", "seguridad", "funcion hash", "universidad anahuac",
    "murcielago", "computadora", "laboratorio blockchain", "ingenieria", "tarea artesanal",
    # Mensajes con alta repetición
    "aaaaaaaaaa", "1111111111", "0101010101010101", "abcabcabcabc", "xyzxyzxyzxyz",
    # Cadenas aleatorias
    "qWeRtY321", "zXcMbV98", "a1b2c3d4e5", "p0LqWe9R", "mKjIuHyG",
    # Mensajes largos
    "Este es un mensaje mucho mas largo para probar el relleno",
    "El efecto avalancha es crucial para garantizar la seguridad",
    "Buscando colisiones y preimagenes en un hash artesanal truncado",
    "Un pequeño cambio en la entrada debe cambiar la mitad de la salida",
    "Fin de la lista de treinta mensajes de prueba para el experimento"
] 
resultados_av = []

for rondas in range(1, 9):
    distancias_ronda = []
    
    for msg in mensajes:
        distancias_msg = medir_avalancha_un_mensaje(msg, rondas)
        distancias_ronda.extend(distancias_msg)
        
    # Calcular porcentajes (dividiendo entre n=32 bits de salida)
    porcentajes = [(d / 32) * 100 for d in distancias_ronda]
    
    # Calcular estadísticas requeridas por la rúbrica
    promedio = statistics.mean(porcentajes)
    desviacion = statistics.stdev(porcentajes) if len(porcentajes) > 1 else 0
    minimo = min(distancias_ronda)
    maximo = max(distancias_ronda)
    
    print(f"Rondas: {rondas} | AV: {promedio:.2f}% | Min: {minimo} | Max: {maximo}")