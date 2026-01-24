import serial
import serial.tools.list_ports
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, RadioButtons
import threading
import time
from collections import deque

# --- CONFIGURACIÓN ---
baudios = 921600
password = "INICIAR\n"
max_muestras = 500

# Datos y estados
datos_x = deque(maxlen=max_muestras)
datos_y_ax = deque(maxlen=max_muestras); datos_y_ay = deque(maxlen=max_muestras); datos_y_az = deque(maxlen=max_muestras)

puerto_seleccionado = None
ser = None
grabando = False
muestras_grabadas = []
contador_muestras = 0
estado_msg = "Seleccione un puerto COM"

# --- HILO DE LECTURA SERIAL ---
def lectura_serial():
    global ser, contador_muestras, grabando, muestras_grabadas, estado_msg
    while True:
        if puerto_seleccionado and (ser is None or not ser.is_open):
            try:
                estado_msg = f"Conectando a {puerto_seleccionado}..."
                temp_ser = serial.Serial(puerto_seleccionado, baudios, timeout=1)
                time.sleep(2) # Espera crítica para el reinicio del C3

                # Handshake directo como te funcionaba antes
                temp_ser.write(password.encode())
                ser = temp_ser
                estado_msg = f"Conectado: {puerto_seleccionado}"


                while ser and ser.is_open:
                    linea = ser.readline().decode('utf-8', errors='ignore').strip()
                    if linea and ',' in linea:
                        partes = linea.split(',')
                        if len(partes) == 7:
                            try:
                                v = [float(x) for x in partes]
                                # Conversión a G (Rango 2G)
                                ax_g, ay_g, az_g = v[1]/16384.0, v[2]/16384.0, v[3]/16384.0

                                contador_muestras += 1
                                datos_x.append(contador_muestras)
                                datos_y_ax.append(ax_g); datos_y_ay.append(ay_g); datos_y_az.append(az_g)

                                if grabando:
                                    muestras_grabadas.append(v)
                            except: continue
            except Exception as e:
                estado_msg = f"Error: {str(e)[:15]}"
                if ser: ser.close()
                ser = None
                time.sleep(1)
        time.sleep(0.1)

# --- INTERFAZ GRÁFICA ---
fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(bottom=0.3, left=0.25)

ln_ax, = ax.plot([], [], 'r-', label='AX (g)', linewidth=1)
ln_ay, = ax.plot([], [], 'g-', label='AY (g)', linewidth=1)
ln_az, = ax.plot([], [], 'b-', label='AZ (g)', linewidth=1)

ax.legend(loc='upper right')
ax.set_title("Acelerograma Dinámico - ESP32-C3")
ax.grid(True, alpha=0.3)

txt_info = fig.text(0.5, 0.22, estado_msg, ha="center", weight="bold", color="blue")

def update(frame):
    txt_info.set_text(estado_msg)
    if len(datos_x) < 2: return ln_ax, ln_ay, ln_az

    ln_ax.set_data(datos_x, datos_y_ax); ln_ay.set_data(datos_x, datos_y_ay); ln_az.set_data(datos_x, datos_y_az)
    ax.set_xlim(datos_x[0], datos_x[-1])

    # Auto-escalado de eje Y
    all_vals = list(datos_y_ax) + list(datos_y_ay) + list(datos_y_az)
    ax.set_ylim(min(all_vals) - 0.2, max(all_vals) + 0.2)
    return ln_ax, ln_ay, ln_az

# --- ACCIONES DE LA INTERFAZ ---
def on_btn_clicked(event):
    global grabando, muestras_grabadas, datos_x, datos_y_ax, datos_y_ay, datos_y_az, contador_muestras
    if not grabando:
        # REINICIO TOTAL DE GRÁFICA
        datos_x.clear(); datos_y_ax.clear(); datos_y_ay.clear(); datos_y_az.clear()
        contador_muestras = 0; muestras_grabadas = []
        grabando = True
        btn_action.label.set_text("DETENER Y GUARDAR")
        btn_action.color = "tomato"
    else:
        grabando = False
        btn_action.label.set_text("INICIAR LECTURA")
        btn_action.color = "lightgreen"
        if muestras_grabadas:
            df = pd.DataFrame(muestras_grabadas, columns=['ms','ax','ay','az','gx','gy','gz'])
            nombre = f"acelerograma_{int(time.time())}.xlsx"
            df.to_excel(nombre, index=False)
            print(f"Excel guardado: {nombre}")

def on_port_selected(label):
    global puerto_seleccionado, ser
    if ser: ser.close()
    puerto_seleccionado = label
    print(f"Cambiando a puerto {label}")

# Configuración de Widgets
ax_btn = plt.axes([0.35, 0.05, 0.4, 0.1])
btn_action = Button(ax_btn, 'INICIAR LECTURA', color='lightgreen')
btn_action.on_clicked(on_btn_clicked)

# Selector de Puertos Dinámico
puertos_list = [p.device for p in serial.tools.list_ports.comports()]
if not puertos_list: puertos_list = ["No detectado"]
ax_radio = plt.axes([0.02, 0.35, 0.18, 0.45], facecolor='#f0f0f0')
radio = RadioButtons(ax_radio, puertos_list)
radio.on_clicked(on_port_selected)

# Lanzamiento de procesos
threading.Thread(target=lectura_serial, daemon=True).start()
ani = FuncAnimation(fig, update, interval=25, blit=False, cache_frame_data=False)
plt.show()