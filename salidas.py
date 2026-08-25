import os

RAIZ = os.path.dirname(os.path.abspath(__file__))
DIR_OUTPUTS = os.path.join(RAIZ, "outputs")

PRUEBAS = ("avalancha", "colisiones", "preimagen", "segunda_preimagen")


def carpeta_prueba(nombre):
    if nombre not in PRUEBAS:
        raise ValueError(f"Prueba desconocida: {nombre}. Usa una de {PRUEBAS}")
    ruta = os.path.join(DIR_OUTPUTS, nombre)
    os.makedirs(ruta, exist_ok=True)
    return ruta
