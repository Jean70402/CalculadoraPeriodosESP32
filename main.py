import subprocess
import sys
import threading
import time
import tkinter as tk
from collections import deque
from tkinter import simpledialog

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import serial
import serial.tools.list_ports
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, RadioButtons

# --- CONFIGURACIÓN ---
baudios = 921600
password = "INICIAR\n"
max_muestras = 500

datos_t = deque(maxlen=max_muestras)
datos_y_ax = deque(maxlen=max_muestras);
datos_y_ay = deque(maxlen=max_muestras);
datos_y_az = deque(maxlen=max_muestras)

puerto_seleccionado = None
ser = None
grabando = False
muestras_grabadas = []
estado_msg = "Seleccione un puerto COM"


def obtener_periodo(tiempos, valores):
    if len(valores) < 100: return 0.0
    v_arr = np.array(valores)
    v_centrado = v_arr - np.mean(v_arr)
    if np.max(v_centrado) - np.min(v_centrado) < 0.05: return 0.0
    indices_cruce = np.where(np.diff(np.sign(v_centrado)) > 0)[0]
    if len(indices_cruce) < 2: return 0.0
    t_arr = np.array(tiempos)
    tiempos_cruce = t_arr[indices_cruce] / 1000.0
    periodos = np.diff(tiempos_cruce)
    return np.mean(periodos)


def lectura_serial():
    global ser, grabando, muestras_grabadas, estado_msg
    while True:
        if puerto_seleccionado and (ser is None or not ser.is_open):
            try:
                estado_msg = f"Conectando a {puerto_seleccionado}..."
                temp_ser = serial.Serial(puerto_seleccionado, baudios, timeout=1)
                time.sleep(2)
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
                                ax_g, ay_g, az_g = v[1] / 16384.0, v[2] / 16384.0, v[3] / 16384.0
                                datos_t.append(v[0]);
                                datos_y_ax.append(ax_g);
                                datos_y_ay.append(ay_g);
                                datos_y_az.append(az_g)
                                if grabando: muestras_grabadas.append(v)
                            except:
                                continue
            except Exception as e:
                estado_msg = f"Error: {str(e)[:15]}"
                if ser: ser.close()
                ser = None
                time.sleep(1)
        time.sleep(0.1)


fig, ax = plt.subplots(figsize=(11, 8))
plt.subplots_adjust(bottom=0.3, left=0.25)

ln_ax, = ax.plot([], [], 'r-', label='AX', linewidth=1)
ln_ay, = ax.plot([], [], 'g-', label='AY', linewidth=1)
ln_az, = ax.plot([], [], 'b-', label='AZ', linewidth=1)
ax.legend(loc='upper right');
ax.grid(True, alpha=0.3)

txt_info = fig.text(0.5, 0.22, estado_msg, ha="center", weight="bold", color="blue")
txt_periodos = fig.text(0.5, 0.15, "Esperando movimiento...", ha="center", fontsize=9, color="darkgreen", weight="bold")


def update(frame):
    txt_info.set_text(estado_msg)
    if len(datos_t) < 10: return ln_ax, ln_ay, ln_az, txt_periodos
    t_vista = np.array(datos_t)
    t_relativo = (t_vista - t_vista[0]) / 1000.0
    ln_ax.set_data(t_relativo, datos_y_ax);
    ln_ay.set_data(t_relativo, datos_y_ay);
    ln_az.set_data(t_relativo, datos_y_az)
    ax.set_xlim(0, t_relativo[-1])
    all_vals = list(datos_y_ax) + list(datos_y_ay) + list(datos_y_az)
    ax.set_ylim(min(all_vals) - 0.2, max(all_vals) + 0.2)

    def f(v): return obtener_periodo(datos_t, v)

    tx, ty, tz = f(datos_y_ax), f(datos_y_ay), f(datos_y_az)

    def fmt(T): return f"{T:.3f}s ({1 / T:.1f}Hz)" if T > 0 else "---"

    txt_periodos.set_text(f"Periodos Tiempo Real:\nTX: {fmt(tx)} | TY: {fmt(ty)} | TZ: {fmt(tz)}")
    return ln_ax, ln_ay, ln_az, txt_periodos


# --- GESTIÓN DE PUERTOS ---
ax_radio = plt.axes([0.02, 0.4, 0.18, 0.4], facecolor='#f8f8f8')


def refrescar_puertos(event=None):
    ax_radio.clear()
    puertos = [p.device for p in serial.tools.list_ports.comports()]
    if not puertos: puertos = ["Sin puertos"]
    global radio
    radio = RadioButtons(ax_radio, puertos)
    radio.on_clicked(on_port_selected)
    plt.draw()


def on_port_selected(label):
    global puerto_seleccionado
    if ser: ser.close()
    puerto_seleccionado = label


def on_btn_clicked(event):
    global grabando, muestras_grabadas
    if not grabando:
        datos_t.clear();
        datos_y_ax.clear();
        datos_y_ay.clear();
        datos_y_az.clear()
        muestras_grabadas = []
        grabando = True
        btn_action.label.set_text("DETENER Y GUARDAR")
        btn_action.color = "tomato"
    else:
        grabando = False
        btn_action.label.set_text("INICIAR LECTURA")
        btn_action.color = "lightgreen"
        if muestras_grabadas:
            root = tk.Tk();
            root.withdraw()
            nombre = simpledialog.askstring("Guardar", "Nombre del archivo (sin .xlsx):")
            root.destroy()
            if not nombre: nombre = f"captura_{int(time.time())}"
            df = pd.DataFrame(muestras_grabadas, columns=['ms', 'ax', 'ay', 'az', 'gx', 'gy', 'gz'])
            df.to_excel(f"{nombre}.xlsx", index=False)


# Botones Interfaz
ax_btn = plt.axes([0.25, 0.05, 0.3, 0.07])
btn_action = Button(ax_btn, 'INICIAR LECTURA', color='lightgreen')
btn_action.on_clicked(on_btn_clicked)

ax_btn_ana = plt.axes([0.6, 0.05, 0.25, 0.07])
btn_ana = Button(ax_btn_ana, 'ABRIR ANALIZADOR', color='gold')
btn_ana.on_clicked(lambda e: subprocess.Popen([sys.executable, "analizador.py"]))

ax_ref_port = plt.axes([0.02, 0.32, 0.18, 0.05])
btn_ref_port = Button(ax_ref_port, 'Refrescar Puertos', color='lightgray')
btn_ref_port.on_clicked(refrescar_puertos)

refrescar_puertos()
threading.Thread(target=lectura_serial, daemon=True).start()
ani = FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)

manager = plt.get_current_fig_manager()
if __name__ == "__main__":
    # 2. Intentar maximizar según el backend (Windows/Tkinter es el más común)
    try:

        manager.window.iconbitmap("icono.ico")
        manager.window.title("Acelerograma - Grupo 2 EPN")
        manager.window.state('zoomed')

    except AttributeError:
        # Si usas otros backends como Qt o WX
        try:
            manager.frame.Maximize(True)
        except:
            try:
                manager.window.showMaximized()
            except:
                pass

    refrescar_puertos()
    threading.Thread(target=lectura_serial, daemon=True).start()
    ani = FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)
    fig.canvas.manager.set_window_title('Acelerograma - Grupo 2 EPN')
    plt.show()

