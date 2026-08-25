from hash import *
import csv
import math
import os
import statistics
import time
import matplotlib.pyplot as plt
import numpy as np

N_BITS = 32
RONDAS_DETALLE = 8
RONDAS_MIN = 1
RONDAS_MAX = 14

def hash_a_bits(hash_hex):
    return bin(int(hash_hex, 16))[2:].zfill(N_BITS)

def etiqueta_mensaje(mensaje, max_len=28):
    texto = mensaje.replace("\n", " ")
    if len(texto) > max_len:
        return texto[: max_len - 3] + "..."
    return texto

def medir_avalancha_un_mensaje(mensaje, rondas):
    mensaje_bin = char_a_bin(mensaje)
    bits_original = hash_a_bits(procesar(agregar_padding(mensaje_bin), rondas))

    distancias = []
    for i in range(len(mensaje_bin)):
        nuevo_bit = "0" if mensaje_bin[i] == "1" else "1"
        mensaje_alterado = mensaje_bin[:i] + nuevo_bit + mensaje_bin[i + 1:]
        bits_nuevo = hash_a_bits(procesar(agregar_padding(mensaje_alterado), rondas))
        dhamming = sum(a != b for a, b in zip(bits_original, bits_nuevo))
        distancias.append(dhamming)
    return distancias

def stats_distancias(distancias):
    porcentajes = [(d / N_BITS) * 100 for d in distancias]
    return {
        "intentos": len(distancias),
        "delta_media": statistics.mean(distancias),
        "av": statistics.mean(porcentajes),
        "sigma_bits": statistics.stdev(distancias) if len(distancias) > 1 else 0.0,
        "sigma_pct": statistics.stdev(porcentajes) if len(porcentajes) > 1 else 0.0,
        "min": min(distancias),
        "max": max(distancias),
    }

def imprimir_tabla(filas):
    encabezado = (
        f"{'Mensaje':<32} {'Long.':>8} {'Intentos':>10} "
        f"{'dH medio':>10} {'% cambiado':>12} {'sigma':>10} {'[min, max]':>14}"
    )
    print(encabezado)
    print("-" * len(encabezado))
    for fila in filas:
        if fila["longitud"] == "-":
            long_txt = f"{'-':>8}"
        else:
            long_txt = f"{fila['longitud']:>6} b"
        print(
            f"{fila['mensaje']:<32} {long_txt} {fila['intentos']:>10} "
            f"{fila['delta_media']:>10.2f} {fila['av']:>11.2f}% "
            f"{fila['sigma_bits']:>10.2f} [{fila['min']:>2}, {fila['max']:>2}]"
        )

def pmf_binomial(n, p):
    return [math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k)) for k in range(n + 1)]

def guardar_csv(ruta, filas, campos):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(filas)

mensajes = [
    "a", "1", "ok", "no", "sol",
    "hola mundo", "criptografia", "seguridad", "funcion hash", "universidad anahuac",
    "murcielago", "computadora", "laboratorio blockchain", "ingenieria", "tarea artesanal",
    "aaaaaaaaaa", "1111111111", "0101010101010101", "abcabcabcabc", "xyzxyzxyzxyz",
    "qWeRtY321", "zXcMbV98", "a1b2c3d4e5", "p0LqWe9R", "mKjIuHyG",
    "Este es un mensaje mucho mas largo para probar el relleno",
    "El efecto avalancha es crucial para garantizar la seguridad",
    "Buscando colisiones y preimagenes en un hash artesanal truncado",
    "Un pequeño cambio en la entrada debe cambiar la mitad de la salida",
    "Fin de la lista de treinta mensajes de prueba para el experimento",
]

if __name__ == "__main__":
    N = len(mensajes)
    longitudes = [len(char_a_bin(m)) for m in mensajes]
    total_intentos = sum(longitudes)
    directorio = carpeta_prueba("avalancha")

    print("=" * 88)
    print("PARTE 2. Medicion del efecto avalancha")
    print("=" * 88)
    print(f"N (mensajes originales): {N}")
    print(f"n (bits de salida):      {N_BITS}")
    print(f"K por mensaje:           todos los bits de entrada (Lj variable)")
    print(f"Intentos totales (suma Lj): {total_intentos}")
    print(f"Evaluaciones de H:       {N * (RONDAS_MAX - RONDAS_MIN + 1) + total_intentos * (RONDAS_MAX - RONDAS_MIN + 1)}")
    print(f"Referencia teorica SAC:  E[dH] = n/2 = {N_BITS / 2:.0f} bits (50%)")
    print(f"                         sigma teorica Bin(n,1/2) = {math.sqrt(N_BITS * 0.5 * 0.5):.3f} bits")
    print()

    t0 = time.perf_counter()
    av_por_rondas = []
    distancias_detalle = None
    filas_detalle = None

    for rondas in range(RONDAS_MIN, RONDAS_MAX + 1):
        distancias_ronda = []
        filas_mensaje = []

        for msg in mensajes:
            distancias_msg = medir_avalancha_un_mensaje(msg, rondas)
            distancias_ronda.extend(distancias_msg)
            st = stats_distancias(distancias_msg)
            filas_mensaje.append({
                "mensaje": etiqueta_mensaje(msg),
                "longitud": len(char_a_bin(msg)),
                **st,
            })

        global_st = stats_distancias(distancias_ronda)
        av_por_rondas.append({
            "rondas": rondas,
            "intentos": global_st["intentos"],
            "delta_media": global_st["delta_media"],
            "av": global_st["av"],
            "sigma_bits": global_st["sigma_bits"],
            "sigma_pct": global_st["sigma_pct"],
            "min": global_st["min"],
            "max": global_st["max"],
        })

        print(
            f"Rondas: {rondas:2d} | AV: {global_st['av']:6.2f}% | "
            f"dH: {global_st['delta_media']:5.2f} bits | "
            f"sigma: {global_st['sigma_bits']:5.2f} | "
            f"Min: {global_st['min']:2d} | Max: {global_st['max']:2d} | "
            f"NxK: {global_st['intentos']}"
        )

        if rondas == RONDAS_DETALLE:
            distancias_detalle = distancias_ronda
            filas_detalle = filas_mensaje + [{
                "mensaje": "Global",
                "longitud": "-",
                **global_st,
            }]

    elapsed = time.perf_counter() - t0
    print(f"\nTiempo total del barrido: {elapsed:.2f} s")

    print()
    print("=" * 88)
    print(f"Tabla por mensaje (rondas = {RONDAS_DETALLE}, funcion de trabajo)")
    print("=" * 88)
    imprimir_tabla(filas_detalle)

    ruta_mensajes = os.path.join(directorio, "avalancha_por_mensaje.csv")
    ruta_rondas = os.path.join(directorio, "avalancha_por_rondas.csv")
    guardar_csv(
        ruta_mensajes,
        [
            {
                "mensaje": f["mensaje"],
                "longitud_bits": f["longitud"],
                "intentos": f["intentos"],
                "delta_media_bits": f"{f['delta_media']:.4f}",
                "porcentaje_cambiado": f"{f['av']:.4f}",
                "sigma_bits": f"{f['sigma_bits']:.4f}",
                "min": f["min"],
                "max": f["max"],
            }
            for f in filas_detalle
        ],
        ["mensaje", "longitud_bits", "intentos", "delta_media_bits",
         "porcentaje_cambiado", "sigma_bits", "min", "max"],
    )
    guardar_csv(
        ruta_rondas,
        [
            {
                "rondas": r["rondas"],
                "intentos": r["intentos"],
                "delta_media_bits": f"{r['delta_media']:.4f}",
                "AV_porcentaje": f"{r['av']:.4f}",
                "sigma_bits": f"{r['sigma_bits']:.4f}",
                "sigma_porcentaje": f"{r['sigma_pct']:.4f}",
                "min": r["min"],
                "max": r["max"],
            }
            for r in av_por_rondas
        ],
        ["rondas", "intentos", "delta_media_bits", "AV_porcentaje",
         "sigma_bits", "sigma_porcentaje", "min", "max"],
    )
    print(f"\nCSV: {ruta_mensajes}")
    print(f"CSV: {ruta_rondas}")

    # Gráfica AV vs rondas
    xs = [r["rondas"] for r in av_por_rondas]
    ys = [r["av"] for r in av_por_rondas]
    sigmas = [r["sigma_pct"] for r in av_por_rondas]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.errorbar(xs, ys, yerr=sigmas, fmt="-o", capsize=3, label="AV observado +/- sigma")
    ax.axhline(50, color="gray", linestyle="--", label="SAC ideal (50%)")
    ax.set_xlabel("Número de rondas")
    ax.set_ylabel("AV (% de bits modificados)")
    ax.set_title("Efecto avalancha en funcion del numero de rondas")
    ax.set_xticks(xs)
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    ruta_av = os.path.join(directorio, "avalancha_vs_rondas.png")
    fig.savefig(ruta_av, dpi=150)
    plt.close(fig)

    # Histograma vs Bin(n, 1/2)
    teorica = pmf_binomial(N_BITS, 0.5)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bins = np.arange(-0.5, N_BITS + 1.5, 1)
    ax.hist(
        distancias_detalle,
        bins=bins,
        density=True,
        alpha=0.7,
        label="Empírico",
        color="steelblue",
        edgecolor="white",
    )
    ax.plot(range(N_BITS + 1), teorica, "o-", color="crimson", label="Bin(32, 1/2)")
    ax.set_xlabel("Distancia de Hamming dH (bits)")
    ax.set_ylabel("Frecuencia relativa")
    ax.set_title(f"Distribucion de dH con {RONDAS_DETALLE} rondas (N={N}, intentos={len(distancias_detalle)})")
    ax.set_xticks(range(0, N_BITS + 1, 2))
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    ruta_hist = os.path.join(directorio, "avalancha_histograma.png")
    fig.savefig(ruta_hist, dpi=150)
    plt.close(fig)

    print(f"Grafica: {ruta_av}")
    print(f"Grafica: {ruta_hist}")
    print("\nListo.")
