from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from word2number_es import w2n
import nova
import time

options = Options()
options.add_experimental_option("detach", True)

options.add_argument(r"--user-data-dir=C:\Users\yourusername\AppData\Local\Microsoft\Edge\User Data")
options.add_argument("--profile-directory=Default")

driver = webdriver.Edge(options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 30)
from selenium.webdriver.common.action_chains import ActionChains

list_videos = []

limite_videos = 3

def main():

    while True:
        n = str(nova.reconocerVoz()).lower()
        print(n)

        if "nova" in n:
            nova.Hablar("Sí, escuchando...")
            print("Escuchando...")
            n = str(nova.reconocerVoz()).lower()
            print(n)
            interpretar_instrucciones(n)

def interpretar_instrucciones(n):
        if any(l in n for l in ("muestra", "muéstrame", "dame")) and "videos" in n and \
        any(l in n for l in ("recomendados", "sugeridos")):
            nova.Hablar("Bien, espere un momento...")
            videos = obtener_videos_recomendados()
            mostrar_videos_recomendados(videos)

        elif any(l in n for l in ("buscar", "busca", "busco", "búscame", "busque")) and "video" in n:
            nova.Hablar("Diga el video que quiere buscar: ")
            print("Ingrese el video que quiere buscar: ")
            n = str(nova.reconocerVoz()).lower()
            print(n)
            videos = buscar_video(n)
            mostrar_videos_recomendados(videos)
        
        elif any(l in n for l in ("entra", "entrar", "abre", "abra", "abro")) and "youtube" in n:
            nova.Hablar("Bien, abriendo YouTube")
            videos = inicio_yt()
            mostrar_videos_recomendados(videos)

        elif any(l in n for l in ("pantalla completa", "fullscreen")):
            nova.Hablar("Se pondrá o quitará el video en pantalla completa")
            pantalla_completa()
        
        elif any(l in n for l in ("pausa", "páusalo", "reproducir", "reprodúcelo", "reproduce")):
            nova.Hablar("Se pausará o reproducirá el video")
            play_video()    

        else:
            nova.Hablar("No se entendió lo que dijo")

def mostrar_videos_recomendados(videos):
    global list_videos
    list_videos = []
 
    nova.Hablar(f"Hay {videos[len(videos)-1]} videos recomendados")

    n = ""
    
    while n.isnumeric() == False:
        nova.Hablar("¿Cuántos videos quieres ver?")
        n = str(nova.reconocerVoz()).lower()
        print(n)

        try:
            n = w2n.word_to_num(n)

            if n >= videos[len(videos)-1] or n < 1:
                raise ValueError
            
            else:
                global limite_videos
                limite_videos = n
                print(n)
                break

        except ValueError:
            nova.Hablar("Ese número no es válido")

    nova.Hablar(f"Bien, solo te mostraré los {limite_videos} primeros videos recomendados:")

    for i in range(limite_videos):
        print(f"{videos[i]["number"]}. {videos[i]["title"]}")
        nova.Hablar(f"{videos[i]["number"]}. {videos[i]["title"]}")

    while True:
        try:
            n = str("none")

            while n == "none":
                nova.Hablar("¿Cuál video quieres? ")
                n = str(nova.reconocerVoz()).lower()
                print(n)
            
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
                n = "none"
                continue

            if n > limite_videos or n < 1:
                raise ValueError
            
            else:
                break
        
        except ValueError:
            n = "none"
            nova.Hablar("Ese video no es válido, por favor intente con otro")

    n -= 1

    nova.Hablar(f"Bien, elegiste el video '{videos[n]["title"]}'")

    videos[n]["driver"].click()

def inicio_yt():
    driver.get("https://www.youtube.com")
    return obtener_videos_recomendados()

def buscar_video(busqueda):
    nova.Hablar(f"Ok, buscando videos de {busqueda}...")
    yt_search = f"https://www.youtube.com/results?search_query={busqueda}&sp=EgIQAQ%253D%253D"
    driver.get(yt_search)
    return mostrar_resultados_busqueda()

def obtener_videos_recomendados():
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, 900000);")

    videos = wait.until(EC.presence_of_all_elements_located(
    (By.XPATH, '//a[@class="ytLockupMetadataViewModelTitle"]')))

    n = 0
    i=1
    
    while n < len(videos):
        if videos[n].text != "":

            dict_videos = {
                "number" : i,
                "id" : n,
                "title" : videos[n].text,
                "driver" : videos[n]
            }

            list_videos.append(dict_videos)
            i+=1
        
        n+=1

    list_videos.append(i-1)

    driver.execute_script("window.scrollTo(0, 0);")

    return list_videos

def mostrar_resultados_busqueda():
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, 900000);")

    videos = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//a[@class="yt-simple-endpoint style-scope ytd-video-renderer"]')))

    n = 0
    i=1
    
    while n < len(videos):
        if videos[n].text != "":

            dict_videos = {
                "number" : i,
                "id" : n,
                "title" : videos[n].text,
                "driver" : videos[n]
            }

            list_videos.append(dict_videos)
            i+=1
        
        n+=1

    list_videos.append(i-1)

    driver.execute_script("window.scrollTo(0, 0);")

    return list_videos

def play_video():
    driver.implicitly_wait(5)
    ActionChains(driver).send_keys("K").perform()

def pantalla_completa():
    driver.implicitly_wait(5)
    ActionChains(driver).send_keys("F").perform()

if __name__ == "__main__":
    main()