import os
import sys
import ctypes
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import pandas as pd
from matplotlib.widgets import Button, RadioButtons, SpanSelector
from scipy.fft import fft, fftfreq

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def obtener_analisis(tiempos, valores):
    v_arr = np.array(valores)
    v_centrado = v_arr - np.mean(v_arr)
    t_arr = (np.array(tiempos) - tiempos[0]) / 1000.0
    indices = np.where(np.diff(np.sign(v_centrado)) > 0)[0]
    t_medio = np.mean(np.diff(t_arr[indices])) if len(indices) >= 2 else 0
    n = len(v_centrado)
    d = np.mean(np.diff(t_arr))
    yf = fft(v_centrado)
    xf = fftfreq(n, d)[:n // 2]
    amplitud = 2.0 / n * np.abs(yf[0:n // 2])
    f_dominante = xf[np.argmax(amplitud[1:]) + 1]
    return t_medio, f_dominante, xf, amplitud

class AnalizadorIndependiente:
    def __init__(self):
        self.df = None
        self.fig = plt.figure(figsize=(14, 9))
        self.gs = self.fig.add_gridspec(2, 2, left=0.32, bottom=0.15, hspace=0.3, wspace=0.2)
        self.ax_signal = self.fig.add_subplot(self.gs[0, :])
        self.ax_fft = self.fig.add_subplot(self.gs[1, :])
        self.txt_res = self.fig.text(0.5, 0.05, "Selecciona un archivo y arrastra el mouse", ha="center", weight="bold", color="darkblue")
        self.ax_list = plt.axes([0.02, 0.35, 0.25, 0.5], facecolor='#f4f4f4')
        self.refrescar_archivos()
        ax_ref = plt.axes([0.02, 0.25, 0.25, 0.05])
        self.btn_ref = Button(ax_ref, 'Refrescar Archivos', color='lightgray')
        self.btn_ref.on_clicked(lambda e: self.refrescar_archivos())
        self.span = SpanSelector(self.ax_signal, self.on_select, 'horizontal', useblit=True, props=dict(alpha=0.3, facecolor='yellow'))

    def refrescar_archivos(self):
        self.ax_list.clear()
        archivos = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        nombres_v = [(f[:22] + "..") if len(f) > 24 else f for f in archivos]
        self.mapa = dict(zip(nombres_v, archivos)) if archivos else {}
        self.radio = RadioButtons(self.ax_list, nombres_v if archivos else ["Sin archivos"])
        self.radio.on_clicked(self.cargar_datos)
        plt.draw()

    def cargar_datos(self, n_c):
        a_r = self.mapa.get(n_c)
        if not a_r: return
        self.df = pd.read_excel(a_r)
        self.ax_signal.clear()
        t = (self.df['ms'] - self.df['ms'].iloc[0]) / 1000.0
        for c, cl in zip(['ax','ay','az'], ['r','g','b']):
            self.ax_signal.plot(t, self.df[c]/16384.0, cl, label=c.upper(), alpha=0.5)
        self.ax_signal.legend(); self.ax_signal.grid(True, alpha=0.2)
        plt.draw()

    def on_select(self, xmin, xmax):
        if self.df is None: return
        t = (self.df['ms'] - self.df['ms'].iloc[0]) / 1000.0
        sel = self.df[(t >= xmin) & (t <= xmax)]
        if len(sel) < 20: return
        self.ax_fft.clear(); r_t = f"Análisis {xmin:.1f}s-{xmax:.1f}s:\n"
        for c, cl in zip(['ax','ay','az'], ['red','green','blue']):
            tm, fd, xf, amp = obtener_analisis(sel['ms'].values, sel[c]/16384.0)
            self.ax_fft.plot(xf, amp, color=cl, label=f"FFT {c.upper()}", alpha=0.8)
            r_t += f"{c.upper()}: T={tm:.3f}s | f={fd:.2f}Hz  "
        self.ax_fft.legend(); self.ax_fft.grid(True, alpha=0.2); self.txt_res.set_text(r_t); plt.draw()
        # Esto habilitará etiquetas interactivas en el gráfico de FFT
        mplcursors.cursor(self.ax_fft, hover=False).connect(
            "add", lambda sel: sel.annotation.set_text(f"f: {sel.target[0]:.2f}Hz\nAmp: {sel.target[1]:.4f}")
        )
if __name__ == "__main__":
    import ctypes
    try: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('epn.ingenieria.acelerograma.v1')
    except: pass
    app = AnalizadorIndependiente()
    manager = plt.get_current_fig_manager()
    try:
        manager.window.iconbitmap(resource_path("icono.ico"))
        manager.window.state('zoomed')
    except: pass
    plt.show()