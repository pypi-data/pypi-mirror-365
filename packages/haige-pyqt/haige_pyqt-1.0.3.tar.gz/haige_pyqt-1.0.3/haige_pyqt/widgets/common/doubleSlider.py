from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QSlider


class QDoubleSlider(QSlider):
    doubleValueChanged = pyqtSignal(float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 默认范围0.0-1.0，步长0.01
        self._min = 0.0
        self._max = 1.0
        self._step = 0.01
        self._decimals = 2  # 小数位数

        # 内部使用整数表示，放大100倍以获得0.01精度
        self._factor = 10 ** self._decimals
        super().setMinimum(0)
        super().setMaximum(int((self._max - self._min) / self._step))
        super().setSingleStep(1)  # 内部步长为1对应0.01

        self.valueChanged.connect(self._emit_double_value)

    def _emit_double_value(self, value):
        self.doubleValueChanged.emit(self._min + value * self._step)

    def setMinimum(self, min_val):
        self._min = min_val
        self._update_range()

    def setMaximum(self, max_val):
        self._max = max_val
        self._update_range()

    def setStep(self, step):
        """设置步长，如0.01"""
        self._step = step
        self._update_range()

    def _update_range(self):
        """更新内部整数范围"""
        super().setMaximum(int((self._max - self._min) / self._step))

    def value(self):
        return round(self._min + super().value() * self._step, self._decimals)

    def setValue(self, value):
        value = max(self._min, min(self._max, value))
        int_value = int(round((value - self._min) / self._step))
        super().setValue(int_value)

#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     # 使用示例
#     slider = QDoubleSlider(Qt.Horizontal)
#     slider.setMinimum(0.0)
#     slider.setMaximum(1.0)
#     slider.setSingleStep(0.01)
#     slider.setValue(0.5)
#     slider.doubleValueChanged.connect(print)
#     slider.show()
#     sys.exit(app.exec_())
