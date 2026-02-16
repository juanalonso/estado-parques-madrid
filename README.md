# Bot de Estado de Parques de Madrid

Este es un bot de Python que monitoriza el estado de las alertas de los parques de Madrid y publica actualizaciones en [Bluesky](https://bsky.app/profile/estadoparques.bsky.social).

## Funcionalidades

- Consulta la API de alertas de parques del Ayuntamiento de Madrid.
- Compara el estado actual con el estado anterior guardado.
- Si hay cambios en el nivel de alerta (verde, amarillo, naranja, rojo), publica un post en Bluesky con el estado de todos los parques monitorizados.
- Mantiene un registro local del último estado conocido para detectar cambios.

## Requisitos

- Python 3.x
- Una cuenta de Bluesky

## Instalación

1.  Clona este repositorio o descarga los archivos.
2.  Instala las dependencias necesarias:

```bash
pip install requests atproto python-dotenv
```

## Configuración

Crea un archivo `.env` en el directorio raíz del proyecto con tus credenciales de Bluesky:

```env
BLUESKY_EMAIL=tu_email@ejemplo.com
BLUESKY_PASSWORD=tu_contraseña_de_aplicación
```

> **Nota:** Se recomienda usar una "App Password" de Bluesky en lugar de tu contraseña principal.

## Uso

Para ejecutar el bot manualmente:

```bash
python estadoparques.py
```

El script:
1.  Obtendrá los datos de la API.
2.  Imprimirá el estado actual en la consola.
3.  Si detecta cambios respecto a la última ejecución, publicará un post en Bluesky y actualizará el archivo `estado_parques.json`.

## 🤖 Automatización

Para que el bot funcione de forma continua, puedes programar su ejecución mediante **cron** (en Linux/Mac) o el **Programador de tareas** (en Windows).

Ejemplo de crontab para ejecutarlo cada 30 minutos:

```bash
*/30 * * * * /ruta/al/python /ruta/al/proyecto/estadoparques.py >> /ruta/al/proyecto/bot.log 2>&1
```

## ⚠️ Exención de responsabilidad

Esta herramienta utiliza datos públicos del Ayuntamiento de Madrid pero no tiene ninguna afiliación oficial con dicha entidad.
