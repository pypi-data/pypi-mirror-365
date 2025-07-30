#!/usr/bin/env python
# coding: utf-8

import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsLineItem, QMenu, QAction, QInputDialog, QFileDialog, QMessageBox,
    QColorDialog, QFontDialog, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox,QDesktopWidget
)
from PyQt5.QtCore import Qt, QPointF, QLineF, QRectF, QSizeF
from PyQt5.QtGui import QBrush, QPen, QColor, QPainter, QTextDocument, QTextOption, QTransform, QFont, QImage, QClipboard
from PyQt5.QtWidgets import QTextEdit, QDialog, QVBoxLayout, QDialogButtonBox

def EasyInf():
    inf={
    '软件名称':'思维导图工具',
    '版本号':'1.0.0',
    '功能介绍':'一个简单的思维导图工具。',
    'PID':'001',
    '分组':'效率',
    '依赖':'pyqt5,json'
        }
    return inf
        

class MindMapNode(QGraphicsRectItem):
    """思维导图节点"""
    def __init__(self, rect, text="节点", parent=None):
        super().__init__(rect, parent)
        self.setBrush(QBrush(QColor(173, 216, 230)))  # 节点背景颜色
        self.setPen(QPen(Qt.black))  # 节点边框颜色
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)  # 发送位置变化信号
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)  # 允许选中
        self.setZValue(1)  # 节点位于上层

        # 添加文本
        self.text_item = QGraphicsTextItem(self)
        self.text_item.setPos(rect.x() + 5, rect.y() + 5)  # 文本位置
        self.text_item.setTextWidth(rect.width() - 10)  # 设置文本宽度
        self.set_text(text)  # 设置初始文本

    def set_text(self, text):
        """设置节点文本"""
        # 使用 QTextDocument 实现文字换行和自动缩小
        document = QTextDocument()
        document.setDefaultTextOption(QTextOption(Qt.AlignLeft | Qt.AlignTop))
        document.setTextWidth(self.rect().width() - 10)  # 设置文本宽度
        document.setPlainText(text)
        self.text_item.setDocument(document)

        # 自动调整字体大小以适应方框
        font = self.text_item.font()
        font_size = font.pointSize()
        while (document.size().height() > self.rect().height() - 10 or
               document.size().width() > self.rect().width() - 10) and font_size > 1:
            font_size -= 1
            font.setPointSize(font_size)
            self.text_item.setFont(font)
            document.setTextWidth(self.rect().width() - 10)
            document.setPlainText(text)

    def get_text(self):
        """获取节点文本"""
        return self.text_item.toPlainText()

    def get_font(self):
        """获取节点字体"""
        return self.text_item.font()

    def get_font_color(self):
        """获取节点字体颜色"""
        return self.text_item.defaultTextColor()

    def mouseDoubleClickEvent(self, event):
        """双击编辑文本"""
        dialog = QDialog()
        dialog.setWindowTitle("编辑节点文本")
        dialog.setMinimumWidth(400)  # 设置对话框宽度

        # 创建多行文本框
        text_edit = QTextEdit()
        text_edit.setPlainText(self.get_text())  # 设置当前文本
        text_edit.setAcceptRichText(False)  # 仅支持纯文本

        # 创建按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        layout.addWidget(button_box)
        dialog.setLayout(layout)

        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            new_text = text_edit.toPlainText()
            if new_text:
                self.set_text(new_text)

    def paint(self, painter, option, widget=None):
        """绘制节点"""
        if self.isSelected():
            # 选中时改变颜色
            painter.setBrush(QBrush(QColor(255, 200, 200)))  # 选中时的背景颜色
            painter.setPen(QPen(Qt.red, 2))  # 选中时的边框颜色
        else:
            painter.setBrush(self.brush())
            painter.setPen(self.pen())
        painter.drawRect(self.rect())


class MindMapLine(QGraphicsLineItem):
    """思维导图关系线"""
    def __init__(self, line, parent=None):
        super().__init__(line, parent)
        self.setPen(QPen(Qt.black, 2))  # 线条样式
        self.setFlag(QGraphicsLineItem.ItemSendsGeometryChanges)  # 发送位置变化信号
        self.setFlag(QGraphicsLineItem.ItemIsSelectable)  # 允许选中
        self.setZValue(0)  # 直线位于下层

    def paint(self, painter, option, widget=None):
        """绘制线条"""
        if self.isSelected():
            # 选中时改变颜色
            painter.setPen(QPen(Qt.red, 2))  # 选中时的线条颜色
        else:
            painter.setPen(self.pen())
        painter.drawLine(self.line())


class NodeEditDialog(QDialog):
    """节点编辑对话框"""
    def __init__(self, nodes, parent=None):
        super().__init__(parent)
        self.nodes = nodes
        self.setWindowTitle("编辑节点")
        self.layout = QVBoxLayout()

        # 宽度
        self.width_label = QLabel("宽度:")
        self.width_input = QLineEdit(str(nodes[0].rect().width()))
        self.layout.addWidget(self.width_label)
        self.layout.addWidget(self.width_input)

        # 高度
        self.height_label = QLabel("高度:")
        self.height_input = QLineEdit(str(nodes[0].rect().height()))
        self.layout.addWidget(self.height_label)
        self.layout.addWidget(self.height_input)

        # 边框颜色
        self.border_color_label = QLabel("边框颜色:")
        self.border_color_button = QPushButton("选择边框颜色")
        self.border_color_button.clicked.connect(self.choose_border_color)
        self.layout.addWidget(self.border_color_label)
        self.layout.addWidget(self.border_color_button)

        # 填充颜色
        self.fill_color_label = QLabel("填充颜色:")
        self.fill_color_button = QPushButton("选择填充颜色")
        self.fill_color_button.clicked.connect(self.choose_fill_color)
        self.layout.addWidget(self.fill_color_label)
        self.layout.addWidget(self.fill_color_button)

        # 字体
        self.font_label = QLabel("字体:")
        self.font_button = QPushButton("选择字体")
        self.font_button.clicked.connect(self.choose_font)
        self.layout.addWidget(self.font_label)
        self.layout.addWidget(self.font_button)

        # 字体颜色
        self.font_color_label = QLabel("字体颜色:")
        self.font_color_button = QPushButton("选择字体颜色")
        self.font_color_button.clicked.connect(self.choose_font_color)
        self.layout.addWidget(self.font_color_label)
        self.layout.addWidget(self.font_color_button)

        # 确认按钮
        self.confirm_button = QPushButton("确认")
        self.confirm_button.clicked.connect(self.confirm)
        self.layout.addWidget(self.confirm_button)

        self.setLayout(self.layout)

        # 默认字体为微软雅黑
        self.font = QFont("微软雅黑", 12)
        self.font_color = QColor(Qt.black)

    def choose_border_color(self):
        """选择边框颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.border_color = color

    def choose_fill_color(self):
        """选择填充颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.fill_color = color

    def choose_font(self):
        """选择字体"""
        font, ok = QFontDialog.getFont(self.font, self, "选择字体")
        if ok:
            self.font = font

    def choose_font_color(self):
        """选择字体颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.font_color = color

    def confirm(self):
        """确认修改"""
        width = float(self.width_input.text())
        height = float(self.height_input.text())

        for node in self.nodes:
            node.setRect(QRectF(node.rect().x(), node.rect().y(), width, height))

            if hasattr(self, 'border_color'):
                node.setPen(QPen(self.border_color))

            if hasattr(self, 'fill_color'):
                node.setBrush(QBrush(self.fill_color))

            if hasattr(self, 'font'):
                node.text_item.setFont(self.font)

            if hasattr(self, 'font_color'):
                node.text_item.setDefaultTextColor(self.font_color)

        self.close()


class LineEditDialog(QDialog):
    """连接线编辑对话框"""
    def __init__(self, lines, parent=None):
        super().__init__(parent)
        self.lines = lines
        self.setWindowTitle("编辑连接线")
        self.layout = QVBoxLayout()

        # 线条粗细
        self.thickness_label = QLabel("线条粗细:")
        self.thickness_input = QLineEdit(str(lines[0].pen().width()))
        self.layout.addWidget(self.thickness_label)
        self.layout.addWidget(self.thickness_input)

        # 线条样式
        self.style_label = QLabel("线条样式:")
        self.style_combo = QComboBox()
        self.style_combo.addItems(["实线", "虚线", "点线", "点划线", "双点划线"])
        self.layout.addWidget(self.style_label)
        self.layout.addWidget(self.style_combo)

        # 线条颜色
        self.color_label = QLabel("线条颜色:")
        self.color_button = QPushButton("选择颜色")
        self.color_button.clicked.connect(self.choose_color)
        self.layout.addWidget(self.color_label)
        self.layout.addWidget(self.color_button)

        # 确认按钮
        self.confirm_button = QPushButton("确认")
        self.confirm_button.clicked.connect(self.confirm)
        self.layout.addWidget(self.confirm_button)

        self.setLayout(self.layout)

    def choose_color(self):
        """选择线条颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color

    def confirm(self):
        """确认修改"""
        thickness = int(self.thickness_input.text())
        style = self.style_combo.currentText()

        for line in self.lines:
            pen = line.pen()
            pen.setWidth(thickness)

            if style == "实线":
                pen.setStyle(Qt.SolidLine)
            elif style == "虚线":
                pen.setStyle(Qt.DashLine)
            elif style == "点线":
                pen.setStyle(Qt.DotLine)
            elif style == "点划线":
                pen.setStyle(Qt.DashDotLine)
            elif style == "双点划线":
                pen.setStyle(Qt.DashDotDotLine)

            if hasattr(self, 'color'):
                pen.setColor(self.color)

            line.setPen(pen)

        self.close()


class MindMapScene(QGraphicsScene):
    """思维导图画布"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 800, 600)  # 画布大小
        self.current_line = None  # 当前绘制的连接线
        self.start_node = None  # 连接线的起始节点
        self.drawing_node = False  # 是否正在绘制节点
        self.start_pos = QPointF()  # 绘制节点的起点
        self.line_start_pos = QPointF()  # 连接线的起点
        self.history = []  # 操作历史记录

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 检查是否点击在已有方框或直线上
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            if isinstance(item, (MindMapNode, MindMapLine)):
                # 如果点击在已有方框或直线上，则选中
                item.setSelected(True)
                return

            # 开始绘制节点
            self.drawing_node = True
            self.start_pos = event.scenePos()

        elif event.button() == Qt.RightButton:
            # 记录连接线的起点
            self.line_start_pos = event.scenePos()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.drawing_node:
            # 更新节点的终点（用于绘制矩形）
            pass
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.drawing_node and event.button() == Qt.LeftButton:
            # 完成绘制节点
            end_pos = event.scenePos()
            rect = QRectF(self.start_pos, end_pos).normalized()
            if rect.width() > 10 and rect.height() > 10:  # 避免过小的节点
                # 检查是否与已有节点或直线重叠
                overlap = False
                for item in self.items():
                    if isinstance(item, MindMapNode) and item.rect().intersects(rect):
                        overlap = True
                        break
                    elif isinstance(item, MindMapLine):
                        # 检查直线是否与矩形相交
                        line = item.line()
                        if rect.intersects(QRectF(line.p1(), line.p2()).normalized()):
                            overlap = True
                            break
                if not overlap:
                    node = MindMapNode(rect)
                    self.addItem(node)
                    self.history.append(("add_node", node))  # 记录操作历史
            self.drawing_node = False

        elif event.button() == Qt.RightButton:
            # 完成绘制连接线
            line_end_pos = event.scenePos()
            line = MindMapLine(QLineF(self.line_start_pos, line_end_pos))
            self.addItem(line)
            self.history.append(("add_line", line))  # 记录操作历史

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        """键盘按下事件"""
        if event.key() == Qt.Key_Delete:
            # 删除选中的对象
            for item in self.selectedItems():
                self.history.append(("remove", item))  # 记录操作历史
                self.removeItem(item)
        elif event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            # 移动选中的对象
            delta = 5  # 每次移动的像素数
            dx, dy = 0, 0
            if event.key() == Qt.Key_Left:
                dx = -delta
            elif event.key() == Qt.Key_Right:
                dx = delta
            elif event.key() == Qt.Key_Up:
                dy = -delta
            elif event.key() == Qt.Key_Down:
                dy = delta

            for item in self.selectedItems():
                if isinstance(item, MindMapNode):
                    # 移动节点
                    item.setPos(item.pos() + QPointF(dx, dy))
                elif isinstance(item, MindMapLine):
                    # 移动直线
                    line = item.line()
                    item.setLine(QLineF(line.p1() + QPointF(dx, dy), line.p2() + QPointF(dx, dy)))

        super().keyPressEvent(event)

    def undo(self):
        """撤销操作"""
        if self.history:
            action, item = self.history.pop()
            if action == "add_node" or action == "add_line":
                self.removeItem(item)
            elif action == "remove":
                self.addItem(item)


class MindMapView(QGraphicsView):
    """思维导图视图"""
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        self.setDragMode(QGraphicsView.RubberBandDrag)  # 拖拽模式（支持框选")

    def keyPressEvent(self, event):
        """键盘按下事件"""
        if event.key() == Qt.Key_Delete:
            # 删除选中的对象
            for item in self.scene().selectedItems():
                self.scene().removeItem(item)
        super().keyPressEvent(event)


class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("思维导图工具")
        self.setGeometry(100, 100, 800, 600)

        # 创建画布和视图
        self.scene = MindMapScene()
        self.view = MindMapView(self.scene)
        self.setCentralWidget(self.view)

        # 创建菜单栏
        self.create_menus()
        # 居中显示窗口
        self.center()
    def center(self):
        """将窗口居中显示"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
    def create_menus(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")
        save_action = QAction("保存", self)
        save_action.triggered.connect(self.save_mindmap)
        file_menu.addAction(save_action)

        load_action = QAction("加载", self)
        load_action.triggered.connect(self.load_mindmap)
        file_menu.addAction(load_action)

        # 导出为图片
        export_action = QAction("导出为图片", self)
        export_action.triggered.connect(self.export_as_image)
        file_menu.addAction(export_action)

        # 截图至裁剪版
        copy_to_clipboard_action = QAction("截图至裁剪版", self)
        copy_to_clipboard_action.triggered.connect(self.copy_to_clipboard)
        file_menu.addAction(copy_to_clipboard_action)

        # 关于
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        file_menu.addAction(about_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        undo_action = QAction("撤销", self)
        undo_action.triggered.connect(self.scene.undo)
        edit_menu.addAction(undo_action)

        # 节点编辑
        node_edit_action = QAction("编辑节点", self)
        node_edit_action.triggered.connect(self.edit_node)
        edit_menu.addAction(node_edit_action)

        # 连接线编辑
        line_edit_action = QAction("编辑连接线", self)
        line_edit_action.triggered.connect(self.edit_line)
        edit_menu.addAction(line_edit_action)

    def copy_to_clipboard(self):
        """将整个思维导图保存为图片并复制到剪贴板"""
        # 获取场景中的所有内容
        rect = self.scene.itemsBoundingRect()  # 获取场景中所有内容的边界矩形
        padding = 20  # 增加一些边距
        rect.adjust(-padding, -padding, padding, padding)  # 扩大边界矩形

        # 创建图片
        image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
        image.fill(Qt.white)  # 填充白色背景

        # 使用 QPainter 渲染场景到图片
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        self.scene.render(painter, QRectF(image.rect()), rect)  # 渲染整个场景
        painter.end()

        # 将图片复制到剪贴板
        clipboard = QApplication.clipboard()
        clipboard.setImage(image)

        QMessageBox.information(self, "截图至裁剪版", "思维导图已复制到剪贴板，可以粘贴到其他程序中。")

    def edit_node(self):
        """编辑节点"""
        selected_nodes = [item for item in self.scene.selectedItems() if isinstance(item, MindMapNode)]
        if selected_nodes:
            dialog = NodeEditDialog(selected_nodes, self)
            dialog.exec_()

    def edit_line(self):
        """编辑连接线"""
        selected_lines = [item for item in self.scene.selectedItems() if isinstance(item, MindMapLine)]
        if selected_lines:
            dialog = LineEditDialog(selected_lines, self)
            dialog.exec_()

    def save_mindmap(self):
        """保存思维导图"""
        file_path, _ = QFileDialog.getSaveFileName(self, "保存思维导图", "", "JSON 文件 (*.json)")
        if file_path:
            data = {"nodes": [], "connections": []}
            for item in self.scene.items():
                if isinstance(item, MindMapNode):
                    data["nodes"].append(
                        {
                            "x": item.rect().x(),
                            "y": item.rect().y(),
                            "width": item.rect().width(),
                            "height": item.rect().height(),
                            "text": item.get_text(),
                            "border_color": item.pen().color().name(),
                            "fill_color": item.brush().color().name(),
                            "font": item.text_item.font().toString(),
                            "font_color": item.text_item.defaultTextColor().name(),
                        }
                    )
                elif isinstance(item, MindMapLine):
                    data["connections"].append(
                        {
                            "start": (item.line().x1(), item.line().y1()),
                            "end": (item.line().x2(), item.line().y2()),
                            "color": item.pen().color().name(),
                            "thickness": item.pen().width(),
                            "style": item.pen().style(),
                        }
                    )
            with open(file_path, "w") as f:
                json.dump(data, f)

    def load_mindmap(self):
        """加载思维导图"""
        file_path, _ = QFileDialog.getOpenFileName(self, "加载思维导图", "", "JSON 文件 (*.json)")
        if file_path:
            with open(file_path, "r") as f:
                data = json.load(f)
            self.scene.clear()
            nodes = []
            for node_data in data["nodes"]:
                rect = QRectF(node_data["x"], node_data["y"], node_data["width"], node_data["height"])
                node = MindMapNode(rect, node_data["text"])
                node.setPen(QPen(QColor(node_data["border_color"])))
                node.setBrush(QBrush(QColor(node_data["fill_color"])))
                font = QFont()
                font.fromString(node_data["font"])
                node.text_item.setFont(font)
                node.text_item.setDefaultTextColor(QColor(node_data["font_color"]))
                self.scene.addItem(node)
                nodes.append(node)
            for conn_data in data["connections"]:
                line = MindMapLine(QLineF(conn_data["start"][0], conn_data["start"][1], conn_data["end"][0], conn_data["end"][1]))
                pen = line.pen()
                pen.setColor(QColor(conn_data["color"]))
                pen.setWidth(conn_data["thickness"])
                pen.setStyle(conn_data["style"])
                line.setPen(pen)
                self.scene.addItem(line)

    def export_as_image(self):
        """导出为图片"""
        file_path, _ = QFileDialog.getSaveFileName(self, "导出为图片", "", "PNG 图片 (*.png)")
        if file_path:
            # 获取场景中的所有内容
            rect = self.scene.itemsBoundingRect()  # 获取场景中所有内容的边界矩形
            padding = 20  # 增加一些边距
            rect.adjust(-padding, -padding, padding, padding)  # 扩大边界矩形

            # 创建图片
            image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
            image.fill(Qt.white)  # 填充白色背景

            # 使用 QPainter 渲染场景到图片
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
            self.scene.render(painter, QRectF(image.rect()), rect)  # 渲染整个场景
            painter.end()

            # 保存图片
            image.save(file_path)

    def show_about(self):
        """显示关于信息"""
        QMessageBox.information(self, "关于", "Sysucai, Email: 411703730@qq.com")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
