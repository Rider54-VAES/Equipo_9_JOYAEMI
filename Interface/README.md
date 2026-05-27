# RealTime sensing
Repositorio del proyecto final. Equipo 9-Emily Laurian

# Interfaz Serial ESP32 — Visualización de ADC en Tiempo Real

Este proyecto contiene el firmware para ESP32 y un script de Python que
permiten leer y graficar en tiempo real señales analógicas capturadas por
el Conversor Analógico-Digital (ADC) de la placa.

## Estructura del proyecto

```
Interface/
├── C_code/
│   └── ADC.c          # Firmware del ESP32: lee el ADC y envía datos por serial
├── Python_code/
│   └── ADC_sim.py     # Script Python: recibe los datos y los grafica en tiempo real
└── README.md
```

## Cómo funciona

```
ESP32 (GPIO34) → ADC → Serial USB → Python → Gráfica en pantalla
```

1. El ESP32 lee el voltaje en el pin GPIO34 a ~100 Hz.
2. Convierte cada lectura a un par de valores: `raw` (0–4095) y `voltage` (0.0–3.3 V).
3. Envía esos valores por USB en formato CSV: `2048,1.6500`.
4. El script Python los recibe, los parsea y los dibuja en dos gráficas en tiempo real.

---

## Requisitos

### Hardware

- Placa ESP32 (cualquier variante con GPIO34)
- Cable USB de datos (no solo de carga)

### Software

- Python 3.8 o superior
- Librerías Python:
  - [`pyserial`](https://pypi.org/project/pyserial/) — comunicación con el puerto serial
  - [`matplotlib`](https://pypi.org/project/matplotlib/) — graficación

---

## Instalación de librerías Python

Elige el gestor de paquetes que uses:

### Con pip (el más común)

```bash
pip install pyserial matplotlib
```

Si tu sistema tiene Python 2 y Python 3 instalados al mismo tiempo, usa:

```bash
pip3 install pyserial matplotlib
```

### Con conda (usuarios de Anaconda/Miniconda)

```bash
conda install pyserial matplotlib
```

O si prefieres conda-forge (recomendado para versiones más actualizadas):

```bash
conda install -c conda-forge pyserial matplotlib
```

### Con uv (gestor moderno y muy rápido)

Si no tienes `uv` instalado:

```bash
pip install uv
```

Luego instala las librerías:

```bash
uv pip install pyserial matplotlib
```

---

## ¿En qué puerto está conectada mi placa?

Antes de correr el script Python, necesitas saber el nombre del puerto serial
al que está conectado tu ESP32. Este nombre varía según el sistema operativo.

### macOS

Abre una terminal y ejecuta:

```bash
ls /dev/cu.*
```

Busca algo parecido a:
- `/dev/cu.wchusbserial10`
- `/dev/cu.usbserial-0001`
- `/dev/cu.SLAB_USBtoUART`

El nombre exacto depende del chip USB-Serial de tu placa (CH340, CP2102, FTDI, etc.).
Conecta y desconecta el ESP32 para identificar cuál aparece y desaparece.

### Linux

```bash
ls /dev/tty*
```

Busca algo como:
- `/dev/ttyUSB0`
- `/dev/ttyACM0`

También puedes usar:

```bash
dmesg | grep tty
```

Este comando muestra los mensajes del kernel al momento de conectar un dispositivo,
e indica el nombre del puerto asignado.

> **Permiso denegado en Linux:** si obtienes un error de permisos al abrir el puerto,
> agrega tu usuario al grupo `dialout`:
> ```bash
> sudo usermod -aG dialout $USER
> ```
> Luego cierra sesión y vuelve a entrar.

### Windows

1. Conecta el ESP32 por USB.
2. Abre el **Administrador de dispositivos** (Device Manager).
3. Despliega la sección **"Puertos (COM y LPT)"**.
4. Busca un dispositivo como **"USB-SERIAL CH340 (COM3)"** o similar.
5. El nombre del puerto es el que aparece entre paréntesis: `COM3`, `COM4`, etc.

---

## Cómo configurar y correr el script

1. Abre `Python_code/ADC_sim.py` en un editor de texto.
2. Cambia la línea del puerto por el que detectaste en el paso anterior:

   ```python
   PORT = "/dev/cu.wchusbserial10"  # macOS — ejemplo
   PORT = "/dev/ttyUSB0"            # Linux — ejemplo
   PORT = "COM3"                    # Windows — ejemplo
   ```

3. Asegúrate de que el ESP32 ya tiene cargado el firmware (`ADC.c`).
4. Cierra el Monitor Serial de Arduino IDE si está abierto (solo un programa
   puede usar el puerto serial a la vez).
5. Corre el script:

   ```bash
   python Python_code/ADC_sim.py
   ```

6. Deberías ver una ventana con dos gráficas actualizándose en tiempo real.
7. Para terminar, cierra la ventana de la gráfica o presiona `Ctrl+C` en la terminal.

---

## Solución de problemas comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `Error: [Errno 2] No such file or directory` | El puerto en `PORT` no existe | Verifica el nombre del puerto con los pasos de arriba |
| `Error: [Errno 16] Resource busy` | Otro programa está usando el puerto | Cierra Arduino IDE u otro monitor serial |
| Gráfica vacía o datos extraños | Baud rate incorrecto | Confirma que `BAUD = 115200` en el script y en `ADC.c` |
| `ModuleNotFoundError: No module named 'serial'` | pyserial no está instalado | Corre `pip install pyserial` |
| `ModuleNotFoundError: No module named 'matplotlib'` | matplotlib no está instalado | Corre `pip install matplotlib` |
