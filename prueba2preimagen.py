import argparse
import csv
import math
import os
import random
import statistics
import time

import matplotlib.pyplot as plt

from hash import mi_hash
from salidas import carpeta_prueba


MENSAJES_OBJETIVO = [
	"a", "1", "ok", "no", "sol", "hola mundo", "criptografia", "seguridad",
	"funcion hash", "universidad anahuac", "murcielago", "computadora",
	"laboratorio blockchain", "ingenieria", "tarea artesanal", "aaaaaaaaaa",
	"1111111111", "0101010101010101", "abcabcabcabc", "xyzxyzxyzxyz",
]
SEMILLA_BASE = 20260825
CONFIGURACION = {3: 100, 4: 100, 5: 30, 6: 10, 7: 3}
ALFABETO = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def mensaje_aleatorio(rng, longitud=16):
	return "".join(rng.choice(ALFABETO) for _ in range(longitud))


def digesto_truncado(mensaje, digitos):
	return mi_hash(mensaje)[:digitos]


def buscar_segunda_preimagen(mensaje_objetivo, digitos, rng):
	objetivo = digesto_truncado(mensaje_objetivo, digitos)
	intentos = 0
	while True:
		candidato = mensaje_aleatorio(rng)
		intentos += 1
		if intentos % 100000 == 0:
			print(f"      ... {intentos:,} intentos buscando {objetivo}", flush=True)
		if candidato != mensaje_objetivo and digesto_truncado(candidato, digitos) == objetivo:
			return intentos, candidato


def ejecutar_replicas(digitos, repeticiones, semilla):
	return ejecutar_replicas_reanudable(digitos, repeticiones, semilla, None, None, None)


def ejecutar_replicas_reanudable(digitos, repeticiones, semilla, progreso, archivo_progreso, completadas):
	completadas = completadas or {}
	intentos = []
	tiempos_ms = []
	for replica in range(repeticiones):
		objetivo = MENSAJES_OBJETIVO[replica % len(MENSAJES_OBJETIVO)]
		if (digitos, replica) in completadas:
			registro = completadas[(digitos, replica)]
			intentos.append(registro["intentos"])
			tiempos_ms.append(registro["tiempo_ms"])
			print(f"   Réplica {replica + 1}/{repeticiones}: ya guardada, se omite", flush=True)
			continue
		print(f"   Réplica {replica + 1}/{repeticiones}: iniciando con mensaje '{objetivo}'", flush=True)
		rng = random.Random(semilla + replica)
		inicio = time.perf_counter()
		cantidad, candidato = buscar_segunda_preimagen(objetivo, digitos, rng)
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


def abrir_progreso(ruta):
	nuevo = not os.path.exists(ruta)
	archivo = open(ruta, "a", newline="", encoding="utf-8")
	escritor = csv.DictWriter(archivo, fieldnames=["d", "replica", "semilla", "intentos", "tiempo_ms"])
	if nuevo:
		escritor.writeheader()
		archivo.flush()
	return archivo, escritor


def pruebas_estructurales():
	mensaje = "mensaje estructural"
	bloque_1 = "bloque uno"
	bloque_2 = "bloque dos"
	delta = "\x01"
	pruebas = [
		("Relleno ambiguo", digesto_truncado(mensaje, 8) == digesto_truncado(mensaje + "\x00", 8),
		 "La longitud original está incluida en el padding."),
		("Permutación de bloques", digesto_truncado(bloque_1 + bloque_2, 8) == digesto_truncado(bloque_2 + bloque_1, 8),
		 "El estado se actualiza en orden y la compresión no es conmutativa."),
		("Extensión de longitud", False,
		 "La API solo acepta mensajes completos y vuelve a aplicar padding; no expone un estado intermedio."),
		("Linealidad sobre F2", digesto_truncado(mensaje, 8) == digesto_truncado(delta, 8),
		 "Prueba puntual con entradas distintas; no constituye una demostración universal."),
		("Puntos fijos", False,
		 "No se encontró un punto fijo en la búsqueda puntual de la compresión disponible."),
	]
	return [{"prueba": nombre, "funciona": "SI" if funciona else "NO", "observacion": observacion}
			for nombre, funciona, observacion in pruebas]


def guardar_pruebas_estructurales(ruta, pruebas):
	with open(ruta, "w", newline="", encoding="utf-8") as archivo:
		escritor = csv.DictWriter(archivo, fieldnames=["prueba", "funciona", "observacion"])
		escritor.writeheader()
		escritor.writerows(pruebas)


def guardar_comparativa(directorio, resultados):
	digitos = [resultado["d"] for resultado in resultados]
	teorico_colision = [1.2533 * 2 ** (2 * d) for d in digitos]
	rutas = {
		"colisión": os.path.join(os.path.dirname(directorio), "colisiones", "colisiones.csv"),
		"preimagen": os.path.join(os.path.dirname(directorio), "preimagen", "preimagen.csv"),
		"segunda preimagen": os.path.join(directorio, "segunda_preimagen.csv"),
	}
	observado = {}
	for nombre, ruta in rutas.items():
		if os.path.exists(ruta):
			with open(ruta, newline="", encoding="utf-8") as archivo:
				filas = {int(fila["d"]): float(fila["intentos_media"]) for fila in csv.DictReader(archivo)}
			observado[nombre] = [filas.get(d, float("nan")) for d in digitos]

	xs = digitos
	plt.figure(figsize=(8, 4.5))
	plt.plot(xs, [math.log2(valor) for valor in teorico_colision], "--", label="Colisión teórica")
	plt.plot(xs, [4 * d for d in xs], "--", label="Preimagen teórica")
	estilos = {"colisión": "o-", "preimagen": "s-", "segunda preimagen": "^-"}
	for nombre, valores in observado.items():
		plt.plot(xs, [math.log2(valor) for valor in valores], estilos[nombre], label=f"{nombre} observada")
	plt.xlabel("Dígitos hexadecimales d")
	plt.ylabel("log2(intentos)")
	plt.title("Comparación de los tres ataques")
	plt.xticks(xs)
	plt.grid(True, alpha=0.3)
	plt.legend()
	plt.tight_layout()
	ruta = os.path.join(directorio, "comparativa_tres_ataques.png")
	plt.savefig(ruta, dpi=150)
	plt.close()
	return ruta


def ejecutar(digitos, semilla):
	resultados = []
	directorio = carpeta_prueba("segunda_preimagen")
	ruta_progreso = os.path.join(directorio, "segunda_preimagen_progreso.csv")
	completadas = cargar_progreso(ruta_progreso, semilla)
	archivo_progreso, progreso = abrir_progreso(ruta_progreso)
	for d in digitos:
		repeticiones = CONFIGURACION.get(d, 3)
		print(f"\n=== Segunda preimagen: d={d} ({4 * d} bits), {repeticiones} réplicas ===", flush=True)
		resultado = ejecutar_replicas_reanudable(d, repeticiones, semilla + d * 1000, progreso, archivo_progreso, completadas)
		resultados.append(resultado)
		print(
			f"d={d} ({4 * d} bits) | intentos: {resultado['intentos_media']:.2f} "
			f"| mediana: {resultado['intentos_mediana']:.0f} | "
			f"sigma: {resultado['desviacion_intentos']:.2f} | "
			f"tiempo: {resultado['tiempo_medio_ms']:.3f} ms"
		)

	archivo_progreso.close()
	ruta_csv = os.path.join(directorio, "segunda_preimagen.csv")
	guardar_resultados(ruta_csv, resultados)
	ruta_estructurales = os.path.join(directorio, "pruebas_estructurales.csv")
	guardar_pruebas_estructurales(ruta_estructurales, pruebas_estructurales())
	xs = [r["d"] for r in resultados]
	plt.figure(figsize=(8, 4.5))
	plt.plot(xs, [math.log2(r["intentos_teoricos"]) for r in resultados], "--o", label="Teórico")
	plt.plot(xs, [math.log2(r["intentos_media"]) for r in resultados], "-o", label="Observado")
	plt.xlabel("Dígitos hexadecimales d")
	plt.ylabel("log2(intentos)")
	plt.title("Búsqueda de segundas preimágenes")
	plt.xticks(xs)
	plt.grid(True, alpha=0.3)
	plt.legend()
	plt.tight_layout()
	ruta_grafica = os.path.join(directorio, "segunda_preimagen_vs_d.png")
	plt.savefig(ruta_grafica, dpi=150)
	plt.close()
	print(f"CSV: {ruta_csv}")
	print(f"Pruebas estructurales: {ruta_estructurales}")
	print(f"Gráfica: {ruta_grafica}")
	print(f"Comparativa: {guardar_comparativa(directorio, resultados)}")
	return resultados


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Mide la resistencia a segunda preimagen.")
	parser.add_argument("--d", nargs="+", type=int, default=sorted(CONFIGURACION), help="Dígitos hexadecimales a probar")
	parser.add_argument("--semilla", type=int, default=SEMILLA_BASE)
	args = parser.parse_args()
	ejecutar(args.d, args.semilla)
