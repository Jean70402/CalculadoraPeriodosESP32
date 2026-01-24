import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, SpanSelector
from scipy.fft import fft, fftfreq
import os

def obtener_analisis(tiempos, valores):
    v_arr = np.array(valores)
    v_centrado = v_arr - np.mean(v_arr)
    t_arr = (np.array(tiempos) - tiempos[0]) / 1000.0 # Segundos

    # 1. Periodo por cruce por cero
    indices = np.where(np.diff(np.sign(v_centrado)) > 0)[0]
    t_medio = 0
    if len(indices) >= 2:
        t_medio = np.mean(np.diff(t_arr[indices]))

    # 2. FFT (Transformada de Fourier)
    n = len(v_centrado)
    d = np.mean(np.diff(t_arr)) # Intervalo de muestreo
    yf = fft(v_centrado)
    xf = fftfreq(n, d)[:n//2]
    amplitud = 2.0/n * np.abs(yf[0:n//2])
    f_dominante = xf[np.argmax(amplitud[1:]) + 1] # Ignorar frecuencia 0

    return t_medio, f_dominante, xf, amplitud

class AnalizadorIndependiente:
    def __init__(self):
        self.df = None
        self.fig = plt.figure(figsize=(14, 9))
        # Ajuste de rejilla para dar espacio a la lista
        self.gs = self.fig.add_gridspec(2, 2, left=0.3, bottom=0.15, hspace=0.3, wspace=0.2)
        self.ax_signal = self.fig.add_subplot(self.gs[0, :])
        self.ax_fft = self.fig.add_subplot(self.gs[1, :])

        self.ax_signal.set_title("1. Selecciona tramo de interés", fontsize=10)
        self.ax_fft.set_title("2. Espectro de Frecuencias (FFT)", fontsize=10)

        self.txt_res = self.fig.text(0.5, 0.03, "Carga un archivo y arrastra el mouse",
                                     ha="center", fontsize=10, weight="bold", color="darkblue",
                                     bbox=dict(facecolor='white', alpha=0.8))

        # Panel lateral para archivos
        self.ax_list = plt.axes([0.02, 0.3, 0.22, 0.55], facecolor='#f4f4f4')
        self.refrescar_archivos()

        ax_ref = plt.axes([0.02, 0.2, 0.22, 0.05])
        self.btn_ref = Button(ax_ref, 'Refrescar Archivos', color='#e0e0e0')
        self.btn_ref.on_clicked(lambda e: self.refrescar_archivos())

        self.span = SpanSelector(self.ax_signal, self.on_select, 'horizontal', useblit=True,
                                 props=dict(alpha=0.3, facecolor='yellow'))

    def refrescar_archivos(self):
        self.ax_list.clear()
        self.ax_list.set_title("Archivos Excel", fontsize=9)
        archivos = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        # Recorte de nombres para evitar desbordamiento
        nombres_vista = [ (f[:22] + "..") if len(f) > 24 else f for f in archivos ]

        if not archivos:
            nombres_vista = ["Sin archivos"]
            self.mapa = {}
        else:
            self.mapa = dict(zip(nombres_vista, archivos))

        self.radio = RadioButtons(self.ax_list, nombres_vista, activecolor='blue')
        self.radio.on_clicked(self.cargar_datos)
        plt.draw()

    def cargar_datos(self, nombre_corto):
        archivo_real = self.mapa.get(nombre_corto)
        if not archivo_real: return
        self.df = pd.read_excel(archivo_real)
        self.ax_signal.clear()
        t = (self.df['ms'] - self.df['ms'].iloc[0]) / 1000.0
        # Sensibilidad 16384 para BMI160 en 2G
        self.ax_signal.plot(t, self.df['ax']/16384.0, 'r', label='AX', alpha=0.5)
        self.ax_signal.plot(t, self.df['ay']/16384.0, 'g', label='AY', alpha=0.5)
        self.ax_signal.plot(t, self.df['az']/16384.0, 'b', label='AZ', alpha=0.5)
        self.ax_signal.legend(loc='upper right', fontsize=8)
        self.ax_signal.grid(True, alpha=0.2)
        plt.draw()

    def on_select(self, xmin, xmax):
        if self.df is None: return
        t = (self.df['ms'] - self.df['ms'].iloc[0]) / 1000.0
        mask = (t >= xmin) & (t <= xmax)
        sel = self.df[mask]
        if len(sel) < 20: return

        self.ax_fft.clear()
        res_txt = f"Análisis de {xmin:.1f}s a {xmax:.1f}s:\n"

        colores = {'ax': 'red', 'ay': 'green', 'az': 'blue'}
        for col in ['ax', 'ay', 'az']:
            t_med, f_dom, xf, amp = obtener_analisis(sel['ms'].values, sel[col]/16384.0)
            self.ax_fft.plot(xf, amp, color=colores[col], label=f"FFT {col.upper()}", alpha=0.8)
            res_txt += f"{col.upper()}: T={t_med:.3f}s | f(FFT)={f_dom:.2f}Hz   "

        self.ax_fft.set_xlabel("Frecuencia (Hz)"); self.ax_fft.set_ylabel("Amplitud")
        self.ax_fft.grid(True, alpha=0.2); self.ax_fft.legend(fontsize=8)
        self.txt_res.set_text(res_txt)
        plt.draw()

if __name__ == "__main__":
    app = AnalizadorIndependiente()

    # Maximizar la ventana del analizador al abrir
    manager = plt.get_current_fig_manager()
    try:
        manager.window.state('zoomed')
    except:
        pass

    plt.show()