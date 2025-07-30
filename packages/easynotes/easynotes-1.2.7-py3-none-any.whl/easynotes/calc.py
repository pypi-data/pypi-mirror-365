import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QLineEdit, QPushButton
from PyQt5.QtCore import Qt

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('计算器')
        self.resize(300, 400)
        self.center()
        self.setStyleSheet("""
            QWidget {
                background-color: #2E3440;
                color: #D8DEE9;
                font-size: 20px;
            }
            QLineEdit {
                background-color: #3B4252;
                border: 2px solid #4C566A;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton {
                background-color: #4C566A;
                border: 2px solid #4C566A;
                border-radius: 5px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
            QPushButton:pressed {
                background-color: #81A1C1;
            }
        """)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.layout.addWidget(self.display)

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        grid_layout = QGridLayout()
        self.layout.addLayout(grid_layout)

        positions = [(i, j) for i in range(4) for j in range(4)]

        for position, button in zip(positions, buttons):
            btn = QPushButton(button)
            btn.clicked.connect(self.on_click)
            grid_layout.addWidget(btn, *position)

        self.clear_btn = QPushButton('C')
        self.clear_btn.clicked.connect(self.clear)
        grid_layout.addWidget(self.clear_btn, 4, 0, 1, 2)

        self.backspace_btn = QPushButton('←')
        self.backspace_btn.clicked.connect(self.backspace)
        grid_layout.addWidget(self.backspace_btn, 4, 2, 1, 2)

    def on_click(self):
        button = self.sender()
        text = button.text()

        if text == '=':
            self.calculate_result()
        else:
            self.display.setText(self.display.text() + text)

    def calculate_result(self):
        try:
            value = eval(self.display.text())
            if isinstance(value, float):
                # 四舍五入到10位小数
                value_rounded = round(value, 10)
                # 检查是否为整数
                if value_rounded.is_integer():
                    result = str(int(value_rounded))
                else:
                    # 转换为字符串并去除末尾的零
                    result = "{:.10f}".format(value_rounded).rstrip('0').rstrip('.')
            else:
                result = str(value)
            self.display.setText(result)
        except Exception as e:
            self.display.setText("错误")

    def clear(self):
        self.display.clear()

    def backspace(self):
        text = self.display.text()
        self.display.setText(text[:-1])

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            self.calculate_result()
        elif key == Qt.Key_Backspace:
            self.backspace()
        elif key == Qt.Key_Escape:
            self.clear()
        elif key in [Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9,
                     Qt.Key_Plus, Qt.Key_Minus, Qt.Key_Asterisk, Qt.Key_Slash, Qt.Key_Period]:
            self.display.setText(self.display.text() + event.text())

    def center(self):
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
