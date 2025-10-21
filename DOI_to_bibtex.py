import requests
import time
import os
from tkinter import Tk, filedialog

# ==== Selección manual del archivo de DOI ====
Tk().withdraw()
archivo_dois = filedialog.askopenfilename(
    title="Selecciona el archivo TXT con los DOI (uno por línea)",
    filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
)
if not archivo_dois:
    print("No se ha seleccionado ningún archivo. El programa se cerrará.")
    exit()

print(f"Archivo de DOI seleccionado: {archivo_dois}")

ARCHIVO_SALIDA = "referencias_crossref.bib"
ARCHIVO_PROGRESO = "procesados.txt"

# ==== Cargar DOIs y eliminar repetidos ====
with open(archivo_dois, "r", encoding="utf-8") as f:
    dois = sorted(set(line.strip() for line in f if line.strip()))

print(f"Se encontraron {len(dois)} DOI únicos.")

# ==== Cargar progreso previo si existe ====
procesados = set()
if os.path.exists(ARCHIVO_PROGRESO):
    with open(ARCHIVO_PROGRESO, "r", encoding="utf-8") as f:
        procesados = set(line.strip() for line in f if line.strip())

# ==== Función para obtener BibTeX desde CrossRef ====
def get_bibtex_from_crossref(doi):
    url = f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex"
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            return r.text.strip()
        else:
            return f"% Error {r.status_code} para DOI {doi}"
    except Exception as e:
        return f"% Error obteniendo {doi}: {e}"

# ==== Procesar DOIs ====
if dois:
    with open(ARCHIVO_SALIDA, "a", encoding="utf-8") as salida, open(ARCHIVO_PROGRESO, "a", encoding="utf-8") as progreso:
        for i, doi in enumerate(dois, 1):
            if doi in procesados:
                print(f"[{i}/{len(dois)}] Saltado (ya procesado): {doi}")
                continue

            bib_entry = get_bibtex_from_crossref(doi)
            salida.write(bib_entry + "\n\n")
            progreso.write(doi + "\n")

            print(f"[{i}/{len(dois)}] Procesado: {doi}")
            time.sleep(1)
else:
    print("No se detectaron DOI válidos. Verifica el formato del archivo TXT.")

print(f"Proceso completado. Archivo generado: {ARCHIVO_SALIDA}")
