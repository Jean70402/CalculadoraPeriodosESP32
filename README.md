# 📈 Sistema de Análisis de Acelerogramas - Grupo 2 EPN

Este proyecto integra hardware basado en el microcontrolador **ESP32-C3** y el sensor **BMI160** con una interfaz de escritorio profesional en Python para la captura y post-procesamiento de señales sísmicas y vibraciones mecánicas.



---

## 🚀 Funcionalidades Clave

* **Monitoreo en Tiempo Real:** Visualización gráfica de aceleración en los ejes X, Y y Z con auto-escalado dinámico.
* **Handshake de Seguridad:** El software de Python envía automáticamente la clave `INICIAR` para habilitar la transmisión de datos desde el sensor.
* **Cálculo de Periodos (T):** Estimación automática del periodo dominante por eje mediante detección de cruces por cero en tiempo real.
* **Análisis de Frecuencias (FFT):** Herramienta de post-procesamiento para generar espectros de frecuencia mediante la Transformada Rápida de Fourier e identificar frecuencias de resonancia.
* **Selector Dinámico:** Permite seleccionar tramos específicos de una señal grabada utilizando el mouse para realizar análisis localizados.
* **Exportación de Datos:** Generación de reportes en formato Excel (.xlsx) con tiempos en milisegundos y valores de aceleración convertidos a unidades G.

---

## 🛠️ Especificaciones de Hardware

* **Microcontrolador:** ESP32-C3 Super Mini (Arquitectura RISC-V).
* **Sensor:** IMU Bosch BMI160 de 16 bits.
* **Configuración del Sensor:** Rango de acelerómetro de $\pm 2g$ con una sensibilidad de $16384 \text{ LSB}/g$.
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
### 2. Uso de la Aplicación
1. **Conexión:** Conecte el dispositivo ESP32-C3 mediante USB.
2. **Ejecución:** Inicie el programa ejecutando el script principal `main.py`.
3. **Configuración de Puerto:** Seleccione el puerto COM correspondiente en el panel lateral (use el botón **Refrescar Puertos** si es necesario).
4. **Lectura:** Pulse el botón **INICIAR LECTURA** para comenzar la recepción de datos y la visualización en tiempo real.
5. **Análisis:** Para estudiar grabaciones previas, utilice el botón **ABRIR ANALIZADOR** y cargue el archivo de datos deseado.

---

## 📦 Distribución (.exe)

El proyecto está configurado para empaquetarse en un único archivo ejecutable de Windows que incluye una pantalla de carga personalizada y el icono institucional.

**Comando de generación:**
```bash
pyinstaller --noconsole --onefile --icon=icono.ico --splash splash.png --add-data "analizador.py;." --add-data "icono.ico;." main.py
```
---

## 📝 Notas de Ingeniería

* **Compensación de Gravedad:** El software compensa automáticamente la aceleración de la gravedad ($1g$ en el eje vertical Z) mediante la eliminación de la componente DC para obtener cálculos precisos de periodo y FFT.
* **Gestión de Subprocesos:** Se utiliza el módulo `multiprocessing` y argumentos de sistema para asegurar que el analizador y la capturadora funcionen de forma independiente sin duplicar procesos.
* **Visualización:** El entorno fuerza el estado maximizado (`zoomed`) de las ventanas de Matplotlib para facilitar la lectura de gráficas de alta densidad.

---

## 🎓 Institución

* **Escuela Politécnica Nacional (EPN)**.
* **Facultad de Ingeniería**.
* **Proyecto desarrollado por:** Grupo 2.
* **Ubicación:** Quito, Ecuador.
