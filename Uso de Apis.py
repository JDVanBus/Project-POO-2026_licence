'''
Desarrollo Primer Contacto con webscrapping usando:

requests
BeautifulSoup


'''

import requests
import re
from bs4 import BeautifulSoup

#  Paso 1: Obtener el URl

URL = "https://scrapepark.org/courses/spanish/"

respuesta = requests.get(URL)

#  Paso 2: Uso de BeautifulSoup para parsear el còdigo
if respuesta.status_code == 200:
    soup = BeautifulSoup(respuesta.text, 'html.parser')
else:
    print(f"Error al acceder a la página: {respuesta.status_code}")

#  Paso 3: Uso de operaciones bàsicas
#   Mètodo Find

h2 = soup.find_all('h2', limit = 20)

for i in h2:
    print(i.get_text(strip= True))

print(" ")
# Hallar a partir de los atributos de las etiquetas css

divs = soup.find_all('div', class_='heading-container heading-center', limit= 20)

for div in divs:
    print(div.get_text(strip = True))
    print("  ")

print(" ")

src_todos = soup.find_all(src = True)

for element in src_todos:
    src_value = element.get('src')
    if isinstance(src_value, str) and src_value.endswith(".jpg"):
        print(element)


print(" ")
# Parsear estrucuras más complejas

TABLA = soup.find_all('iframe')[0]['src']

request_tabla = requests.get(f"{URL}/{TABLA}")

soup_tabla = BeautifulSoup(request_tabla.text, 'html.parser')

soup_tabla.find('table')

productos_faltantes_etiquetas = soup_tabla.find_all(['th', 'td'], attrs={'style':'color: red;'})
productos_faltantes = [talle.text for talle in productos_faltantes_etiquetas]

print(productos_faltantes)


print(" ")

divs = soup.find_all('div', class_='detail-box')
productos = []
precios = []

for div in divs:
  h5_tag = div.h5
  h6_tag = div.h6
  if (h5_tag is not None) and (h6_tag is not None):
    h5_text = h5_tag.get_text()
    if 'Patineta' in h5_text:
      producto = h5_tag.get_text(strip=True)
      precio = h6_tag.get_text(strip=True).replace('$', '')
      # Agregar filtros
      print(f'producto: {producto:<16} | precio: {precio}')
      productos.append(producto)
      precios.append(precio)


print(" ")

# Editar enlaces
URL_BASE = "https://scrapepark.org/courses/spanish/contact"

for num in range(1,3):
  URL_FINAL = f"{URL_BASE}{num}"
  print(URL_FINAL)
  r = requests.get(URL_FINAL)
  soup = BeautifulSoup(r.text, "html.parser")
  if soup.h5 is not None:
    print(soup.h5.get_text())
  else:
    print("No se encontró h5")


print(" ")

# Usar Regular expressions para buscar datos que no sabemos donde están

telefonos = soup.find_all(string=re.compile(r"\d+-\d+-\d+"))
telefonos

strings_a_buscar = ["MENÚ", "©", "carpincho", "Patineta"]

for string in strings_a_buscar:
  try:
    resultado = soup.find(string=re.compile(rf"{string}"))
    if resultado is not None:
      print(resultado)
    else:
      print(f"El string '{string}' no fue encontrado")
  except AttributeError:
    print(f"El string '{string}' no fue encontrado")

# Almacenamiento de datos

productos.insert(0, "productos")
precios.insert(0, "precios")
datos = dict(zip(productos, precios))