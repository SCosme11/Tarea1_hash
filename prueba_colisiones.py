import argparse
import csv
import math
import os
import random
import string
import statistics
import time

import matplotlib.pyplot as plt

from hash import mi_hash
from salidas import carpeta_prueba


CONSTANTE_CUMPLEANOS = math.sqrt(math.pi / 2)
SEMILLA_BASE = 20260825
CONFIGURACION = {3: 100, 4: 100, 5: 50, 6: 20, 7: 10}
ALFABETO = string.ascii_letters + string.digits


def digesto_truncado(mensaje, digitos):
	return mi_hash(mensaje)[:digitos]


def mensaje_aleatorio(rng, longitud=16):
	return "".join(rng.choice(ALFABETO) for _ in range(longitud))


def buscar_colision(digitos, rng):
	vistos = {}
	intentos = 0
	while True:
		mensaje = mensaje_aleatorio(rng)
		digest = digesto_truncado(mensaje, digitos)
		intentos += 1
		if intentos % 10000 == 0:
			print(f"      ... {intentos:,} intentos", flush=True)
		anterior = vistos.get(digest)
		if anterior is not None and anterior != mensaje:
			return intentos, anterior, mensaje, digest
		vistos[digest] = mensaje


def ejecutar_replicas(digitos, repeticiones, semilla):
	intentos = []
	tiempos_ms = []
	ejemplos = []
	for replica in range(repeticiones):
		print(f"   Réplica {replica + 1}/{repeticiones}: iniciando", flush=True)
		rng = random.Random(semilla + replica)
		inicio = time.perf_counter()
		cantidad, mensaje_1, mensaje_2, digest = buscar_colision(digitos, rng)
		tiempos_ms.append((time.perf_counter() - inicio) * 1000)
		intentos.append(cantidad)
		print(f"   Réplica {replica + 1}/{repeticiones}: colisión en {cantidad:,} intentos", flush=True)
		if not ejemplos:
			ejemplos.append((mensaje_1, mensaje_2, digest))
	return {
		"d": digitos,
		"n_bits": 4 * digitos,
		"intentos_teoricos": CONSTANTE_CUMPLEANOS * (2 ** (2 * digitos)),
		"intentos_media": statistics.mean(intentos),
		"intentos_mediana": statistics.median(intentos),
		"desviacion_intentos": statistics.stdev(intentos) if len(intentos) > 1 else 0.0,
		"tiempo_medio_ms": statistics.mean(tiempos_ms),
		"repeticiones": repeticiones,
		"error_relativo": abs(statistics.mean(intentos) - CONSTANTE_CUMPLEANOS * (2 ** (2 * digitos))) / (CONSTANTE_CUMPLEANOS * (2 ** (2 * digitos))),
		"ejemplo": ejemplos[0],
	}


def guardar_resultados(ruta, resultados):
	campos = ["d", "n_bits", "intentos_teoricos", "intentos_media", "intentos_mediana",
			  "desviacion_intentos", "tiempo_medio_ms", "repeticiones", "error_relativo"]
	with open(ruta, "w", newline="", encoding="utf-8") as archivo:
		escritor = csv.DictWriter(archivo, fieldnames=campos)
		escritor.writeheader()
		for resultado in resultados:
			escritor.writerow({campo: resultado[campo] for campo in campos})


def ejecutar(digitos, semilla):
	resultados = []
	for d in digitos:
		repeticiones = CONFIGURACION.get(d, 10)
		print(f"\n=== Colisiones: d={d} ({4 * d} bits), {repeticiones} réplicas ===", flush=True)
		resultado = ejecutar_replicas(d, repeticiones, semilla + d * 1000)
		resultados.append(resultado)
		print(
			f"d={d} ({4 * d} bits) | intentos: {resultado['intentos_media']:.2f} "
			f"| mediana: {resultado['intentos_mediana']:.0f} | "
			f"sigma: {resultado['desviacion_intentos']:.2f} | "
			f"tiempo: {resultado['tiempo_medio_ms']:.3f} ms"
		)

	directorio = carpeta_prueba("colisiones")
	ruta_csv = os.path.join(directorio, "colisiones.csv")
	guardar_resultados(ruta_csv, resultados)

	xs = [r["d"] for r in resultados]
	plt.figure(figsize=(8, 4.5))
	plt.plot(xs, [math.log2(r["intentos_teoricos"]) for r in resultados], "--o", label="Teórico")
	plt.plot(xs, [math.log2(r["intentos_media"]) for r in resultados], "-o", label="Observado")
	plt.xlabel("Dígitos hexadecimales d")
	plt.ylabel("log2(intentos)")
	plt.title("Búsqueda de colisiones")
	plt.xticks(xs)
	plt.grid(True, alpha=0.3)
	plt.legend()
	plt.tight_layout()
	ruta_grafica = os.path.join(directorio, "colisiones_vs_d.png")
	plt.savefig(ruta_grafica, dpi=150)
	plt.close()

	print(f"CSV: {ruta_csv}")
	print(f"Gráfica: {ruta_grafica}")
	return resultados


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Mide la resistencia a colisiones del hash artesanal.")
	parser.add_argument("--d", nargs="+", type=int, default=sorted(CONFIGURACION), help="Dígitos hexadecimales a probar")
	parser.add_argument("--semilla", type=int, default=SEMILLA_BASE)
	args = parser.parse_args()
	ejecutar(args.d, args.semilla)
