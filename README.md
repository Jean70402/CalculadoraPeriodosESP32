# 📈 Sistema de Análisis de Acelerogramas - Grupo 2 EPN

Este proyecto integra hardware basado en el microcontrolador **ESP32-C3** y el sensor **BMI160** con una interfaz de escritorio en Python para la captura y post-procesamiento de señales sísmicas y vibraciones mecánicas.

---

## 🚀 Funcionalidades 

* **Monitoreo en Tiempo Real:** Visualización gráfica de aceleración en los ejes X, Y y Z con auto-escalado dinámico.
* **Cálculo de Periodos (T):** Estimación automática del periodo dominante por eje mediante detección de cruces por cero en tiempo real.
* **Análisis de Frecuencias (FFT):** Herramienta de post-procesamiento para generar espectros de frecuencia mediante la Transformada Rápida de Fourier.
* **Selector Dinámico:** Permite seleccionar tramos específicos de una señal grabada utilizando el mouse para realizar análisis localizados.
* **Exportación de Datos:** Generación de reportes en formato Excel (.xlsx) con tiempos en milisegundos y valores de aceleración.

---

## 🛠️ Especificaciones de Hardware

* **Microcontrolador:** ESP32-C3 Super Mini (Arquitectura RISC-V).
* **Sensor:** IMU Bosch BMI160 de 16 bits.
* **Conexión Física (I2C):**
  * **SDA:** Pin 6.
  * **SCL:** Pin 7.
  * **Tasa de baudios:** 921,600 para garantizar una alta densidad de muestreo y estabilidad en la transmisión.

---

## 💻 Requisitos y Configuración

### 1. Instalación de Dependencias
Para ejecutar el código fuente, asegúrese de tener instalado Python 3.10 o superior y las siguientes librerías de procesamiento científico:

```bash
pip install pyserial pandas numpy matplotlib scipy openpyxl
```
O instale las librerias en `requierements.txt`

### 2. Uso de la Aplicación
1. **Conexión:** Conecte el dispositivo ESP32-C3 mediante USB.
2. **Ejecución:** Inicie el programa ejecutando el script principal `main.py`.
3. **Configuración de Puerto:** Seleccione el puerto COM correspondiente en el panel lateral (use el botón **Refrescar Puertos** si es necesario).
4. **Lectura:** Pulse el botón **INICIAR LECTURA** para comenzar la recepción de datos y la visualización en tiempo real.
5. **Análisis:** Para estudiar grabaciones previas, utilice el botón **ABRIR ANALIZADOR** y cargue el archivo de datos deseado.
6. **Obtención de periodos** Para obtener los periodos en los 3 ejes, seleccione los datos con el selector dinámico de la señal de estudio en la parte superior
---

## 📦 Distribución (.exe)

El proyecto está configurado para empaquetarse en un único archivo ejecutable de Windows que incluye una pantalla de carga personalizada y el icono institucional.

**Comando de generación:**
```bash
pyinstaller --noconsole --onefile --icon=icono.ico --splash splash.png --add-data "analizador.py;." --add-data "icono.ico;." main.py
```
---

## 📝 Notas 

* **Software de libre acceso:** El software está entregado  "As-is", cualquier contribución o comentario es grata.
---

## 🎓 Institución

* **Escuela Politécnica Nacional (EPN)**.
* **Facultad de Ingeniería Civil y Ambiental**.
* **Proyecto desarrollado por:** Jean Cedeño.
* **Ubicación:** Quito, Ecuador.
