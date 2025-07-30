import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QScreen, QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect

def EasyInf():
    inf={
    '软件名称':'截图工具',
    '版本号':'1.0.0',
    '功能介绍':'一款截图工具。',
    'PID':'004',
    '分组':'效率',
    '依赖':'pyqt5'
        }
    return inf

class ScreenshotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 截取整个屏幕
        screen = QApplication.primaryScreen()
        self.full_screenshot = screen.grabWindow(0)

        # 显示截图
        self.label = QLabel(self)
        self.label.setPixmap(self.full_screenshot)
        self.setCentralWidget(self.label)

        # 初始化选择区域
        self.start_pos = None
        self.end_pos = None
        self.dragging = False

        # 窗口设置
        self.setWindowTitle("选择截图区域")
        self.showFullScreen()  # 全屏显示

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.dragging = True

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.end_pos = event.pos()
            self.update()  # 触发重绘

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.end_pos = event.pos()
            self.dragging = False
            self.capture_selected_area()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.dragging and self.start_pos and self.end_pos:
            # 创建一个新的QPixmap，复制原始截图
            temp_pixmap = QPixmap(self.full_screenshot)
            painter = QPainter(temp_pixmap)
            pen = QPen(QColor(255, 0, 0), 2, Qt.SolidLine)
            painter.setPen(pen)
            rect = QRect(self.start_pos, self.end_pos).normalized()
            painter.drawRect(rect)
            painter.end()

            # 更新label的显示
            self.label.setPixmap(temp_pixmap)

    def capture_selected_area(self):
        if self.start_pos and self.end_pos:
            # 计算矩形区域
            rect = QRect(self.start_pos, self.end_pos).normalized()

            # 从全屏截图中裁剪选定区域
            selected_area = self.full_screenshot.copy(rect)

            # 将截图复制到剪贴板
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(selected_area)

            print(f"截图已复制到剪贴板。区域: {rect}")
            self.close()  # 关闭窗口


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenshotApp()
    sys.exit(app.exec_())
