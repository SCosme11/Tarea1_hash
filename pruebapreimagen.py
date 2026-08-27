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


SEMILLA_BASE = 20260825
CONFIGURACION = {3: 50, 4: 50, 5: 10, 6: 5, 7: 1} #cambié número de intentos por el costo computacional
ALFABETO = string.ascii_letters + string.digits


def mensaje_aleatorio(rng, longitud=16):
	return "".join(rng.choice(ALFABETO) for _ in range(longitud))


def digesto_truncado(mensaje, digitos):
	return mi_hash(mensaje)[:digitos]


def buscar_preimagen(digitos, objetivo, rng):
	intentos = 0
	while True:
		mensaje = mensaje_aleatorio(rng)
		intentos += 1
		if intentos % 100000 == 0:
			print(f"      ... {intentos:,} intentos buscando {objetivo}", flush=True)
		if digesto_truncado(mensaje, digitos) == objetivo:
			return intentos, mensaje


def ejecutar_replicas(digitos, repeticiones, semilla):
	return ejecutar_replicas_reanudable(digitos, repeticiones, semilla, None, None, None)


def ejecutar_replicas_reanudable(digitos, repeticiones, semilla, progreso, archivo_progreso, completadas):
	completadas = completadas or {}
	intentos = []
	tiempos_ms = []
	for replica in range(repeticiones):
		if (digitos, replica) in completadas:
			registro = completadas[(digitos, replica)]
			intentos.append(registro["intentos"])
			tiempos_ms.append(registro["tiempo_ms"])
			print(f"   Réplica {replica + 1}/{repeticiones}: ya guardada, se omite", flush=True)
			continue
		print(f"   Réplica {replica + 1}/{repeticiones}: iniciando", flush=True)
		rng = random.Random(semilla + replica)
		objetivo = digesto_truncado(f"objetivo-preimagen-{digitos}-{replica}", digitos)
		inicio = time.perf_counter()
		cantidad, mensaje = buscar_preimagen(digitos, objetivo, rng)
		intentos.append(cantidad)
		print(f"   Réplica {replica + 1}/{repeticiones}: encontrada en {cantidad:,} intentos", flush=True)
		tiempos_ms.append((time.perf_counter() - inicio) * 1000)
		if progreso is not None:
			progreso.writerow({"d": digitos, "replica": replica, "semilla": semilla + replica,
				"intentos": cantidad, "tiempo_ms": tiempos_ms[-1]})
			archivo_progreso.flush()
	media_teorica = 2 ** (4 * digitos)
	return {
		"d": digitos,
		"n_bits": 4 * digitos,
		"intentos_teoricos": media_teorica,
		"intentos_media": statistics.mean(intentos),
		"intentos_mediana": statistics.median(intentos),
		"desviacion_intentos": statistics.stdev(intentos) if len(intentos) > 1 else 0.0,
		"tiempo_medio_ms": statistics.mean(tiempos_ms),
		"repeticiones": repeticiones,
		"error_relativo": abs(statistics.mean(intentos) - media_teorica) / media_teorica,
	}


def guardar_resultados(ruta, resultados):
	campos = ["d", "n_bits", "intentos_teoricos", "intentos_media", "intentos_mediana",
			  "desviacion_intentos", "tiempo_medio_ms", "repeticiones", "error_relativo"]
	with open(ruta, "w", newline="", encoding="utf-8") as archivo:
		escritor = csv.DictWriter(archivo, fieldnames=campos)
		escritor.writeheader()
		escritor.writerows({campo: resultado[campo] for campo in campos} for resultado in resultados)


def cargar_progreso(ruta, semilla):
	completadas = {}
	if os.path.exists(ruta):
		with open(ruta, newline="", encoding="utf-8") as archivo:
			for fila in csv.DictReader(archivo):
				if int(fila["semilla"]) == semilla + int(fila["d"]) * 1000 + int(fila["replica"]):
					completadas[(int(fila["d"]), int(fila["replica"]))] = {
						"intentos": int(fila["intentos"]), "tiempo_ms": float(fila["tiempo_ms"])
					}
	return completadas


def abrir_progreso(ruta, semilla):
	nuevo = not os.path.exists(ruta)
	archivo = open(ruta, "a", newline="", encoding="utf-8")
	escritor = csv.DictWriter(archivo, fieldnames=["d", "replica", "semilla", "intentos", "tiempo_ms"])
	if nuevo:
		escritor.writeheader()
		archivo.flush()
	return archivo, escritor


def ejecutar(digitos, semilla):
	resultados = []
	directorio = carpeta_prueba("preimagen")
	ruta_progreso = os.path.join(directorio, "preimagen_progreso.csv")
	completadas = cargar_progreso(ruta_progreso, semilla)
	archivo_progreso, progreso = abrir_progreso(ruta_progreso, semilla)
	for d in digitos:
		repeticiones = CONFIGURACION.get(d, 3)
		print(f"\n=== Preimagen: d={d} ({4 * d} bits), {repeticiones} réplicas ===", flush=True)
		resultado = ejecutar_replicas_reanudable(d, repeticiones, semilla + d * 1000, progreso, archivo_progreso, completadas)
		resultados.append(resultado)
		print(
			f"d={d} ({4 * d} bits) | intentos: {resultado['intentos_media']:.2f} "
			f"| mediana: {resultado['intentos_mediana']:.0f} | "
			f"sigma: {resultado['desviacion_intentos']:.2f} | "
			f"tiempo: {resultado['tiempo_medio_ms']:.3f} ms"
		)

	archivo_progreso.close()
	ruta_csv = os.path.join(directorio, "preimagen.csv")
	guardar_resultados(ruta_csv, resultados)
	xs = [r["d"] for r in resultados]
	plt.figure(figsize=(8, 4.5))
	plt.plot(xs, [math.log2(r["intentos_teoricos"]) for r in resultados], "--o", label="Teórico")
	plt.plot(xs, [math.log2(r["intentos_media"]) for r in resultados], "-o", label="Observado")
	plt.xlabel("Dígitos hexadecimales d")
	plt.ylabel("log2(intentos)")
	plt.title("Búsqueda de preimágenes")
	plt.xticks(xs)
	plt.grid(True, alpha=0.3)
	plt.legend()
	plt.tight_layout()
	ruta_grafica = os.path.join(directorio, "preimagen_vs_d.png")
	plt.savefig(ruta_grafica, dpi=150)
	plt.close()
	print(f"CSV: {ruta_csv}")
	print(f"Gráfica: {ruta_grafica}")
	return resultados


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Mide la resistencia a preimagen del hash artesanal.")
	parser.add_argument("--d", nargs="+", type=int, default=sorted(CONFIGURACION), help="Dígitos hexadecimales a probar")
	parser.add_argument("--semilla", type=int, default=SEMILLA_BASE)
	args = parser.parse_args()
	ejecutar(args.d, args.semilla)
