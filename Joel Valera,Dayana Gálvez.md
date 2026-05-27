# RealTime Sensing

Repositorio del proyecto final.

## Contenido

### Interface — Código de ejemplo

La carpeta `Interface/` contiene un ejemplo funcional para conectar Python con tu tarjeta de desarrollo (ESP32). Incluye el firmware en C para leer el ADC y enviarlo por puerto serial, y un script en Python que recibe los datos y los grafica en tiempo real.

Consulta [`Interface/README.md`](Interface/README.md) para instrucciones de instalación, configuración del puerto serial y cómo correr el ejemplo.

### Proyectos de equipos

Cada equipo tendrá su propia carpeta dentro de este repositorio donde subirá su proyecto. La estructura será:

```
RealTime_Sensing/
├── Interface/          # Código de ejemplo: ESP32 + Python
├── Equipo_1/           # Proyecto del equipo 1
├── Equipo_2/           # Proyecto del equipo 2
├── Equipo_N/           # ...
└── README.md
```

Cada equipo debe crear su carpeta con el nombre acordado y subir ahí todos los archivos de su proyecto.
