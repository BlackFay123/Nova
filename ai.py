from google import genai
import nova

client = genai.Client(api_key="your_google_api_key_here")

while True:
    n = str(nova.reconocerVoz()).lower()
    print(n)

    if "nova" in n:
        nova.Hablar("Sí, escuchando...")
        print("Escuchando")
        n = str(nova.reconocerVoz()).lower()
        
        if n != "none":
            print(f"Bien, dijiste o preguntaste: {n}")
            nova.Hablar(f"Bien, dijiste o preguntaste: {n}")

            print("Espere un momento...")
            nova.Hablar("Espere un momento...") 

            response = client.models.generate_content(
                model="gemini-3-flash-preview", contents=n + " en 1 párrafo, si lo que te digo no tiene sentido no respondas nada literalmente"
            )    

            print(response.text)

            nova.Hablar(response.text)
        
        else:
            nova.Hablar("No se entendió lo que dijo")