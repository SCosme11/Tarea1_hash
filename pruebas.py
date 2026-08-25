from hash import *
import statistics
import random
import string
import time
import matplotlib.pyplot as plt
import numpy as np

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

def generar_aleatorio(longitud=10):
    letras = string.ascii_letters + string.digits
    return ''.join(random.choice(letras) for i in range(longitud))

def experimento_colisiones(d_max=6, repeticiones=100):
    resultados = []
    
    for d in range(3, d_max + 1):
        intentos_lista = []
        tiempos_lista = []
        
        for _ in range(repeticiones):
            hashes_vistos = {}
            intentos = 0
            inicio = time.perf_counter()
            
            while True:
                intentos += 1
                msg = generar_aleatorio()
                hash_completo = mi_hash(msg)
                hash_truncado = hash_completo[:d]
                
                if hash_truncado in hashes_vistos and hashes_vistos[hash_truncado] != msg:
                    fin = time.perf_counter()
                    intentos_lista.append(intentos)
                    tiempos_lista.append((fin - inicio) * 1000)
                    break
                
                hashes_vistos[hash_truncado] = msg
                
        # Estadísticas para este valor de d
        print(f"Colisión d={d} | Intentos Medios: {statistics.mean(intentos_lista):.2f} | Tiempo: {statistics.mean(tiempos_lista):.2f} ms")


def buscar_preimagen(objetivo_truncado, d, mensaje_original=None):
    intentos = 0
    inicio = time.perf_counter()
    
    while True:
        intentos += 1
        candidato = generar_aleatorio()
        
        # Evitar probar el mismo mensaje si es Segunda Preimagen
        if candidato == mensaje_original:
            continue
            
        hash_candidato = mi_hash(candidato)[:d]
        
        if hash_candidato == objetivo_truncado:
            fin = time.perf_counter()
            return intentos, (fin - inicio) * 1000

def experimento_preimagenes(d_max=5, repeticiones=100):
    for d in range(3, d_max + 1):
        # PARTE 4: Preimagen
        objetivo_preimagen = mi_hash("EquipoBlockchain")[:d] 
        intentos_pre, tiempos_pre = [], []
        
        # PARTE 5: Segunda Preimagen
        mensaje_fijo = "Contrato_Original_123"
        objetivo_segunda = mi_hash(mensaje_fijo)[:d]
        intentos_seg, tiempos_seg = [], []
        
        for _ in range(repeticiones):
            i_p, t_p = buscar_preimagen(objetivo_preimagen, d)
            intentos_pre.append(i_p)
            tiempos_pre.append(t_p)
            
            i_s, t_s = buscar_preimagen(objetivo_segunda, d, mensaje_original=mensaje_fijo)
            intentos_seg.append(i_s)
            tiempos_seg.append(t_s)
            
        print(f"Preimagen d={d} | Intentos: {statistics.mean(intentos_pre):.0f} | Tiempo: {statistics.mean(tiempos_pre):.2f} ms")
        print(f"2da Preimagen d={d} | Intentos: {statistics.mean(intentos_seg):.0f} | Tiempo: {statistics.mean(tiempos_seg):.2f} ms")

def generar_grafica_final(datos_colision, datos_preimagen, datos_seg_preimagen):
    # 'datos_...' deben ser diccionarios: { d: promedio_intentos }
    # Ejemplo: datos_colision = {3: 82, 4: 315, 5: 1250, 6: 5200}
    
    d_values = list(datos_colision.keys())
    
    # --- 1. Calcular Valores Empíricos (Observados) ---
    # Aplicamos log2 a los promedios de intentos que observaste
    y_colision_obs = [np.log2(datos_colision[d]) for d in d_values]
    y_pre_obs = [np.log2(datos_preimagen[d]) for d in d_values]
    y_seg_pre_obs = [np.log2(datos_seg_preimagen[d]) for d in d_values]
    
    # --- 2. Calcular Valores Teóricos ---
    # Colisión Teórica: E[Q] = 1.2533 * 2^(2d)  (Parte 3. Fundamento)
    y_colision_teo = [np.log2(1.2533 * (2**(2*d))) for d in d_values]
    
    # Preimagen / 2da Preimagen Teórica: E[Q] = 2^(4d) (Parte 4. Fundamento)
    # log2(2^(4d)) se simplifica directamente a 4d
    y_pre_teo = [4 * d for d in d_values] 
    
    # --- 3. Configurar la Gráfica ---
    plt.figure(figsize=(10, 6))
    
    # Curvas Teóricas (Líneas continuas / Punteadas finas)
    plt.plot(d_values, y_colision_teo, label='Colisión (Teórico)', color='navy', linestyle='-', marker='')
    plt.plot(d_values, y_pre_teo, label='Preimagen (Teórico: 4d)', color='darkred', linestyle='-', marker='')
    
    # Curvas Empíricas (Marcadores y líneas punteadas)
    plt.plot(d_values, y_colision_obs, label='Colisión (Observado)', color='blue', linestyle='--', marker='o')
    plt.plot(d_values, y_pre_obs, label='Preimagen (Observado)', color='red', linestyle='--', marker='s')
    plt.plot(d_values, y_seg_pre_obs, label='2da Preimagen (Observado)', color='green', linestyle=':', marker='^')
    
    # --- 4. Formato Requerido ---
    plt.title('Costo Computacional de Ataques vs. Longitud del Hash (d)')
    plt.xlabel('Dígitos hexadecimales (d)')
    plt.ylabel('$\log_2(\text{intentos})$') # LaTeX para el eje Y
    plt.xticks(d_values)
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend()
    
    # Mostrar y guardar
    plt.tight_layout()
    plt.savefig('grafica_final_ataques.png', dpi=300)
    plt.show()

# --- EJEMPLO DE USO (Reemplaza con tus datos reales) ---
datos_c = {3: 85, 4: 330, 5: 1290, 6: 5100, 7: 20600}
datos_p = {3: 4150, 4: 65100, 5: 1050000} # Detenido en d=5 por tiempo
datos_sp = {3: 4100, 4: 65900, 5: 1045000} 

generar_grafica_final(datos_c, datos_p, datos_sp)