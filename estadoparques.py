import requests
import json
import os

from atproto import Client
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# --- CONFIGURACIÓN ---
URL_API = "https://sigma.madrid.es/hosted/rest/services/MEDIO_AMBIENTE/ALERTAS_PARQUES/MapServer/0/query?f=json&where=1%3D1&outFields=*&returnGeometry=false"
ARCHIVO_ESTADO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "estado_parques.json"
)
ARCHIVO_ESTADISTICAS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "estadisticas_parques.ndjson"
)
ESPACIO_INVISIBLE = ""  # ya no usamos \u3000 porque hemos movido el indicador al final
INDICADOR_CAMBIO = "🆕"

BLUESKY_EMAIL = os.getenv("BLUESKY_EMAIL")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")
IS_PRODUCTION = os.getenv("PRODUCTION", "False").lower() == "true"

diccionario_parques = {
    "Jardín del Capricho de la Alameda de Osuna": "Jardín del Capricho"
}

print(f"🔍 Iniciando bot. Modo producción: {IS_PRODUCTION}")


def obtener_datos_api():
    try:
        respuesta = requests.get(URL_API, timeout=10)
        respuesta.raise_for_status()
        data = respuesta.json()

        if "features" not in data:
            print("❌ Error: El JSON no tiene la estructura esperada ('features').")
            return None

        datos_dict = {}
        for feature in data["features"]:
            attrs = feature.get("attributes", {})
            nombre = attrs.get("ZONA_VERDE", "Desconocido").strip()
            codigo = attrs.get("ALERTA_DESCRIPCION") or attrs.get("ALERTA_DES") or 0
            datos_dict[nombre] = codigo
        return datos_dict

    except Exception as e:
        print(f"❌ Error conectando con la API: {e}")
        return None


def cargar_estado_anterior():
    if os.path.exists(ARCHIVO_ESTADO):
        try:
            with open(ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def guardar_estado_nuevo(datos):
    try:
        with open(ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Error guardando estado local: {e}")


def guardar_estadisticas(eventos):
    if not eventos:
        return

    try:
        with open(ARCHIVO_ESTADISTICAS, "a", encoding="utf-8") as f:
            for evento in eventos:
                f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"❌ Error guardando estadísticas históricas: {e}")


def parque_abierto(codigo):
    return codigo < 5


def obtener_emoji(codigo):
    """Devuelve el círculo de color según el código de alerta"""
    if codigo >= 5:
        return "🔴"  # Cerrado
    if codigo == 4:
        return "🟠"  # Naranja
    if codigo == 3:
        return "🟡"  # Amarilla
    return "🟢"  # Verde/Azul


def main():

    datos_actuales = obtener_datos_api()
    if datos_actuales is None:
        return

    datos_anteriores = cargar_estado_anterior()

    cambios_detectados = []
    eventos_cambio = []
    hay_cambios = False
    momento_deteccion = datetime.now().astimezone().isoformat(timespec="seconds")

    for parque, codigo_actual in datos_actuales.items():
        codigo_anterior = datos_anteriores.get(parque)
        if codigo_anterior != codigo_actual:
            hay_cambios = True
            # esto evita que el paso entre 5 y 6 se marque como cambio, ya que de cara al
            # visitante, el parque sigue cerrado igualmente
            ambos_cerrados = (
                codigo_anterior is not None
                and codigo_anterior >= 5
                and codigo_actual >= 5
            )
            if not ambos_cerrados:
                cambios_detectados.append(parque)
            if codigo_anterior is not None:
                eventos_cambio.append(
                    {
                        "detected_at": momento_deteccion,
                        "parque": parque,
                        "from_code": codigo_anterior,
                        "to_code": codigo_actual,
                        "from_open": parque_abierto(codigo_anterior),
                        "to_open": parque_abierto(codigo_actual),
                    }
                )

    post_text = ""

    parques_ordenados = sorted(datos_actuales.keys())

    for parque in parques_ordenados:
        codigo = datos_actuales[parque]
        emoji_semaforo = obtener_emoji(codigo)
        marca_cambio = ESPACIO_INVISIBLE
        if parque in cambios_detectados:
            marca_cambio = INDICADOR_CAMBIO
        nombre_parque = diccionario_parques.get(parque, parque)
        post_text += f"{emoji_semaforo} {nombre_parque} {marca_cambio}\n"
    print(post_text)

    if hay_cambios:
        guardar_estado_nuevo(datos_actuales)
        guardar_estadisticas(eventos_cambio)
        if IS_PRODUCTION:
            client = Client()
            client.login(BLUESKY_EMAIL, BLUESKY_PASSWORD)
            client.post(text=post_text, langs=["es"])


if __name__ == "__main__":
    main()
