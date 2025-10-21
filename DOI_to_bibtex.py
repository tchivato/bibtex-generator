import re
import requests
import time
import os

# Configuración
ARCHIVO_ORIGINAL = r"C:\Users\tchiv\Desktop\evoluci.bib"
ARCHIVO_SALIDA = "referencias_crossref.bib"
ARCHIVO_PROGRESO = "procesados.txt"

# Leer contenido original
with open(ARCHIVO_ORIGINAL, "r", encoding="utf-8") as f:
    bib_content = f.read()

# Extraer DOIs únicos
dois = sorted(set(re.findall(r"10\\.\\d{4,9}/[-._;()/:A-Za-z0-9]+", bib_content)))
print(f"Total de DOI encontrados: {len(dois)}")

# Cargar progreso previo si existe
procesados = set()
if os.path.exists(ARCHIVO_PROGRESO):
    with open(ARCHIVO_PROGRESO, "r", encoding="utf-8") as f:
        procesados = set(line.strip() for line in f if line.strip())

# Definir función para obtener el BibTeX
def get_bibtex_from_crossref(doi):
    url = f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex"
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return f"% Error {response.status_code} para DOI {doi}"
    except Exception as e:
        return f"% Error obteniendo {doi}: {e}"

# Procesar DOIs pendientes
with open(ARCHIVO_SALIDA, "a", encoding="utf-8") as salida, open(ARCHIVO_PROGRESO, "a", encoding="utf-8") as progreso:
    for i, doi in enumerate(dois, 1):
        if doi in procesados:
            print(f"[{i}/{len(dois)}] Saltado (ya procesado): {doi}")
            continue

        bib_entry = get_bibtex_from_crossref(doi)
        salida.write(bib_entry + "\n\n")
        progreso.write(doi + "\n")

        procesados.add(doi)
        print(f"[{i}/{len(dois)}] Procesado: {doi}")
        time.sleep(1)

print(f"Completado. Archivo final generado: {ARCHIVO_SALIDA}")
print("Puedes volver a ejecutar el script, y reanudará automáticamente donde se detuvo.")
