from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
import nova
from word2number_es import w2n

options = Options()
options.add_experimental_option("detach", True)

options.add_argument(r"--user-data-dir=C:\Users\yourusername\AppData\Local\Microsoft\Edge\User Data")
options.add_argument("--profile-directory=Default")

driver = webdriver.Edge(options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 30)

limite_correo = 5

def main():
    while True:
        n = str(nova.reconocerVoz()).lower()
        print(n)

        if "nova" in n:
            nova.Hablar("Sí, escuchando...")
            print("Escuchando")
            n = str(nova.reconocerVoz()).lower()
                
            if n != "none":
                if any(l in n for l in ("abrir, abre, abra, abro, revisar, revisa, reviso")) and "gmail" in n:
                    nova.Hablar("Bien, abriendo Gmail")
                    inicio_gmail()
                    correos_principales = get_correos_principales()
                    mostrar_correos(correos_principales)

                elif all(l in n for l in ("lista", "correos")):
                    nova.Hablar("Bien, obteniendo correos principales")
                    nova.Hablar("Espere un momento...")
                    correos_principales = get_correos_principales()
                    mostrar_correos(correos_principales)                    
                
            else:
                nova.Hablar("No se entendió lo que dijo")


def inicio_gmail():
    driver.get("https://mail.google.com/mail/")
    time.sleep(3)

def get_list_correos():
    correos = driver.find_elements(By.XPATH, '//tr[contains(@class, "zA")]')
    return correos

def mostrar_correos(correos_principales):
    nova.Hablar(f"Tienes {len(correos_principales)} disponibles:")
    print(f"Tienes {len(correos_principales)} disponibles")

    n = ""

    while n.isnumeric() == False:
        nova.Hablar("¿Cuántos correos quieres ver?")
        n = str(nova.reconocerVoz()).lower()
        print(n)

        try:
            n = w2n.word_to_num(n)

            if n >= len(correos_principales) or n < 1:
                raise ValueError
        
            else:
                limite_correo = n
                print(n)
                break

        except ValueError:
            nova.Hablar("Ese número no es válido")

    for n, correo in enumerate(correos_principales, start=1):
        print(f"{n}. De {correo['remitente']}: {correo['titulo']} \
        \n {correo['cuerpo']} \
        \n Fecha: {correo['fecha']} \n")

        nova.Hablar(f"{n}. De {correo['remitente']}: {correo['titulo']} \
        \n {correo['cuerpo']} \
        \n Fecha: {correo['fecha']} \n")

        if n == limite_correo:
            break
    
    while True:
        try:
            n = "none"

            while n == "none":
                nova.Hablar("¿Cuál correo deseas leer? ")
                n = str(nova.reconocerVoz()).lower()
                    
            #Lo de abajo es para poder extraer el numero del video que quiere el usuario para usarlo mas adelante
            if "número" in n:
                n = n.split()
                for i in range(len(n)-1):
                    if "número" in n[i]:
                        n = n[i+1]
                        break
                    
            try: 
                n = w2n.word_to_num(n)
                    
            except ValueError:
                continue

            if type(n) == int:
                if n > limite_correo or n < 1:
                    raise ValueError
                    
            else:
                    raise ValueError
                    
            break
                
        except ValueError:
            nova.Hablar("Ese correo no es válido, por favor intente con otro")

    nova.Hablar(f"Bien, elegiste el correo: {correos_principales[n-1]['titulo']} \
        \n {correos_principales[n-1]['cuerpo']}")

    seleccionar_correo(n-1)
    leer_correo_abierto()

def seleccionar_correo(n):
    get_list_correos()[n].click()

def leer_correo_abierto():
    dict_correo_abierto = get_contenido_correo_abierto()

    print(f"De {dict_correo_abierto['remitente']}, \
         en la fecha de: {dict_correo_abierto['fecha']}. \n \
         {dict_correo_abierto['contenido']}")
    
    nova.Hablar(f"De {dict_correo_abierto['remitente']}, \
         en la fecha de: {dict_correo_abierto['fecha']}. \n \
         {dict_correo_abierto['contenido']}")
    
    btn_inbox()

def get_contenido_correo_abierto():
    time.sleep(3)
    correo_abierto = driver.find_elements(By.XPATH, '//div[contains(@id, "avWBGd-")]')

    txt_correo_abierto = str(correo_abierto[2].text)

    txt_correo_abierto = re.sub(r'[^A-Za-z0-9áéíóúÁÉÍÓÚñÑ@¡!¿?/.,;:\n ]+', '', txt_correo_abierto)

    txt_correo_abierto = txt_correo_abierto.split("\n", maxsplit=3)

    dict_correo_abierto = {
        "remitente" : txt_correo_abierto[0],
        "fecha" : txt_correo_abierto[1],
        "contenido" : str(txt_correo_abierto[3])
    }

    return dict_correo_abierto

def get_correos_principales():
    correos_principales = []

    for i in range(len(get_list_correos())):
        texto = str(get_list_correos()[i].text)

        texto = re.sub(r'[^A-Za-z0-9áéíóúÁÉÍÓÚñÑ@¡!¿?/.,;:\n ]+', '', texto) # ^ quita todos los signos especiales

        texto = texto.split('\n')

        if len(texto) == 5:
            texto.pop(2)

            dict_correos = {
            "remitente" : texto[0],
            "titulo" : texto[1],
            "cuerpo" : texto[2],
            "fecha" : texto[3].strip(),
            }
        
        else:
            dict_correos = {
            "remitente" : texto[0],
            "titulo" : "",
            "cuerpo" : texto[1],
            "fecha" : texto[2].strip(),
            }

        correos_principales.append(dict_correos)

    return correos_principales

def btn_inbox():
    driver.get("https://mail.google.com/mail/u/0/#inbox")

if __name__ == "__main__":
    main()