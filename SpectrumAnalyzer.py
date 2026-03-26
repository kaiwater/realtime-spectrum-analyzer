#プロット関係のライブラリ
from PySide6 import QtWidgets,QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import numpy as np
import sys
#音声関係のライブラリ
import pyaudio

class MainWindow():#(QtWidgets.QMainWindow):
    def __init__(self):
        # マイクインプット設定
        self.CHUNK = 8192         #1度に読み取る音声のデータ幅
        self.RATE = 96000         #サンプリング周波数
        self.MIN_FREQUENCY = 0
        self.MAX_FREQUENCY = 25000
        self.YRange = 50
        self.update_seconds = 50   #更新時間[ms]

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                     channels=1,
                                     rate=self.RATE,
                                     input=True,
                                     frames_per_buffer=self.CHUNK)

        # 音声データの格納場所(プロットデータ)
        self.data = np.zeros(self.CHUNK)
        self.axis = np.fft.fftfreq(len(self.data), d=1.0/self.RATE)

        # プロット初期設定
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle("SpectrumAnalyzer")
        self.plt = self.win.addPlot()
        self.plt.setYRange(0, self.YRange)
        self.plt.setXRange(self.MIN_FREQUENCY, self.MAX_FREQUENCY)

        # アップデート時間設定
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(self.update_seconds)

    def update(self):
        self.data = np.append(self.data, self.AudioInput())
        if len(self.data) > self.CHUNK * 10:
            self.data = self.data[len(self.data) - self.CHUNK * 10:]

        fft_data = self.FFT_AMP(self.data)
        axis = np.fft.fftfreq(len(self.data), d=1.0/self.RATE)

        # 0～MAX_FREQUENCY の正周波数だけ描画
        pos = np.where((axis >= self.MIN_FREQUENCY) & (axis <= self.MAX_FREQUENCY))
        axis = axis[pos]
        fft_data = fft_data[pos]

        self.plt.plot(x=axis, y=fft_data, clear=True, pen="y")

    def AudioInput(self):
        ret = self.stream.read(self.CHUNK, exception_on_overflow=False)
        ret = np.frombuffer(ret, dtype="int16") / 32768.0
        return ret

    def FFT_AMP(self, data):
        data = np.hamming(len(data)) * data
        data = np.fft.fft(data)
        data = np.abs(data)
        return data


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec())
