import sys
import os
import base64
import subprocess
import shutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QTextEdit, QVBoxLayout, QHBoxLayout, 
    QWidget, QPushButton, QFileDialog, QMessageBox, QFontDialog, QColorDialog, QInputDialog,
    QToolBar, QAction, QMenu, QLabel, QDialog, QSpinBox, QFormLayout, QDialogButtonBox, QComboBox, QToolButton, QDesktopWidget,QLineEdit  
)
from PyQt5.QtGui import (
    QTextCharFormat, QFont, QColor, QTextCursor, QIcon, QImage, QPixmap, QTextImageFormat,
    QKeySequence, QPalette, QTextBlockFormat
)
from PyQt5.QtCore import Qt, QMimeData, QByteArray, QBuffer, QIODevice
import xml.etree.ElementTree as ET

def EasyInf():
    inf = {
        '软件名称': '笔记软件',
        '版本号': '1.0.6',
        '功能介绍': '一个快速/简单的笔记软件。',
        'PID': '003',
        '分组': '效率',
        '依赖': 'pyqt5,numpy,scipy'
    }
    return inf

class ResizeImageDialog(QDialog):
    """调整图片大小的对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("调整图片大小")
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(10, 1000)  # 设置宽度范围
        self.width_spinbox.setValue(200)  # 默认宽度
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(10, 1000)  # 设置高度范围
        self.height_spinbox.setValue(200)  # 默认高度

        # 布局
        layout = QFormLayout(self)
        layout.addRow("宽度:", self.width_spinbox)
        layout.addRow("高度:", self.height_spinbox)

        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

    def get_size(self):
        """获取用户输入的宽度和高度"""
        return self.width_spinbox.value(), self.height_spinbox.value()
class NoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # 获取程序所在的目录
        self.program_dir = os.path.dirname(os.path.abspath(__file__))
        self.setting_file = os.path.join(self.program_dir, "setting.xml")
        self.work_dir = self.load_or_create_setting()  # 加载或创建工作目录
        self.current_file = os.path.join(self.work_dir, "notes.xml")  # notes.xml 文件路径
        self.backup_dir = os.path.join(self.work_dir, "backup")  # 备份文件夹路径
        self.notes_list_file = os.path.join(self.work_dir, "notes_list.xml")  # 常用文件列表路径
        self.search_matches = []  # 存储匹配位置
        self.search_pos = 0  # 新增：记录搜索位置
        self.search_matches = []  # 新增：存储匹配位置
        # 初始化备份文件夹
        self.init_backup_dir()

        # 备份 notes.xml
        self.backup_notes_file()

        self.initUI()
        self.load_notes()
        self.load_notes_list()  # 加载常用文件列表

        # 程序启动时显示第一个笔记的内容
        if self.note_list.count() > 0:
            self.note_list.setCurrentRow(0)
            self.show_note_content()

        # 居中显示窗口
        self.center()

    def center(self):
        """将窗口居中显示"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def init_backup_dir(self):
        """初始化备份文件夹"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def backup_notes_file(self):
        """备份 notes.xml 文件"""
        if not os.path.exists(self.current_file):
            return

        # 获取当前备份文件列表
        backup_files = sorted(
            [f for f in os.listdir(self.backup_dir) if f.startswith("notes") and f.endswith(".xml")],
            key=lambda x: int(x[5:-4]) if x[5:-4].isdigit() else 0
        )

        # 计算下一个备份文件的编号
        if not backup_files:
            next_backup_num = 1
        else:
            last_backup_num = int(backup_files[-1][5:-4])
            next_backup_num = (last_backup_num % 20) + 1  # 循环覆盖 1-20

        # 备份文件路径
        backup_file = os.path.join(self.backup_dir, f"notes{next_backup_num}.xml")

        # 复制 notes.xml 到备份文件
        shutil.copy2(self.current_file, backup_file)
        print(f"已备份到: {backup_file}")

    def load_or_create_setting(self):
        """检查 setting.xml 是否存在，如果不存在则创建并选择工作目录"""
        if not os.path.exists(self.setting_file):
            # 弹出目录选择框
            work_dir = QFileDialog.getExistingDirectory(self, "选择工作目录", os.path.expanduser("~"))
            if not work_dir:
                QMessageBox.warning(self, "警告", "未选择工作目录，程序将退出！")
                sys.exit(1)

            # 创建 setting.xml 并保存工作目录
            root = ET.Element("settings")
            work_dir_element = ET.SubElement(root, "work_dir")
            work_dir_element.text = work_dir
            tree = ET.ElementTree(root)
            tree.write(self.setting_file, encoding="utf-8", xml_declaration=True)
            return work_dir
        else:
            # 读取 setting.xml 中的工作目录
            tree = ET.parse(self.setting_file)
            root = tree.getroot()
            work_dir = root.find("work_dir").text
            return work_dir

    def on_search_clicked(self):
        """处理搜索按钮点击事件"""
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入搜索内容")
            return

        # 获取当前笔记内容
        content = self.note_content.toPlainText()
        
        # 如果是新的搜索，重置搜索位置和匹配列表
        if not hasattr(self, 'search_matches') or not hasattr(self, 'search_pos'):
            self.search_matches = []
            self.search_pos = 0

        # 如果是新的搜索关键词，重新查找所有匹配位置
        if not self.search_matches or keyword != self.last_search_keyword:
            self.search_matches = []
            self.search_pos = 0
            start = 0
            while True:
                index = content.find(keyword, start)
                if index == -1:
                    break
                self.search_matches.append(index)
                start = index + 1

            if not self.search_matches:
                QMessageBox.information(self, "提示", "未找到匹配内容")
                return

        # 保存当前搜索关键词
        self.last_search_keyword = keyword

        # 定位到当前匹配项
        if self.search_pos >= len(self.search_matches):
            self.search_pos = 0  # 如果超出范围，回到第一个匹配项

        self.highlight_search_result()

        # 准备下一次搜索
        self.search_pos += 1

    def highlight_search_result(self):
        """高亮显示搜索结果"""
        if not self.search_matches:
            return

        # 清除之前的高亮
        self.note_content.setExtraSelections([])

        # 获取当前匹配项的位置
        pos = self.search_matches[self.search_pos - 1]
        keyword = self.search_input.text().strip()

        # 创建高亮选择
        cursor = self.note_content.textCursor()
        cursor.setPosition(pos)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(keyword))

        # 设置高亮格式
        selection = QTextEdit.ExtraSelection()
        selection.cursor = cursor
        selection.format.setBackground(QColor("#FFD700"))  # 黄色背景

        # 应用高亮
        self.note_content.setExtraSelections([selection])

        # 将匹配项滚动到可见区域
        self.note_content.setTextCursor(cursor)
        self.note_content.ensureCursorVisible()


    def initUI(self):
        self.setWindowTitle('笔记软件 v 0.0.6')  # 添加版本号
        self.setGeometry(100, 100, 800, 600)

        # 设置灰色主题
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E3440;
            }
            QListWidget {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 5px;
                padding: 5px;
            }
            QTextEdit {
                background-color: white;  /* 右侧内容背景改为白色 */
                color: black;  /* 文字颜色改为黑色 */
                border: 1px solid #4C566A;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
            QToolBar {
                background-color: #3B4252;
                border: none;
                padding: 5px;
            }
            QToolButton {
                color: white;  /* 设置文本颜色为白色 */
                background-color: transparent;  /* 背景透明 */
                border: none;  /* 去除边框 */
                padding: 5px;  /* 内边距 */
            }
            QToolButton:hover {
                background-color: #5E81AC;  /* 悬停时背景颜色 */
            }
            QMenu {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #5E81AC;
            }
        QLineEdit {
            background-color: #ECEFF4;
            color: #2E3440;
            border: 1px solid #4C566A;
            border-radius: 3px;
            padding: 2px;
        }           
        """)




        # 左侧笔记标题列表
        self.note_list = QListWidget()
        self.note_list.currentItemChanged.connect(self.show_note_content)  # 监听当前项变化
        self.note_list.setDragEnabled(True)  # 启用拖动
        self.note_list.setDragDropMode(QListWidget.InternalMove)  # 设置拖动模式为内部移动
        self.note_list.setContextMenuPolicy(Qt.CustomContextMenu)  # 启用右键菜单
        self.note_list.customContextMenuRequested.connect(self.show_note_list_context_menu)  # 连接右键菜单事件
        self.note_list.itemDoubleClicked.connect(self.rename_note)  # 双击修改笔记名称

        # 右侧笔记内容编辑框
        self.note_content = QTextEdit()
        self.note_content.textChanged.connect(self.save_note)
        self.note_content.setAcceptRichText(True)  # 允许富文本
        self.note_content.setContextMenuPolicy(Qt.CustomContextMenu)  # 启用自定义右键菜单
        self.note_content.customContextMenuRequested.connect(self.show_context_menu)  # 连接右键菜单事件
        self.note_content.setStyleSheet("background-color: #d7e8d5; color: black;")  # 默认背景颜色为护眼绿

        # 设置默认字体为微软雅黑
        font = QFont("微软雅黑", 10)
        self.note_content.setFont(font)

        # 工具栏
        toolbar = QToolBar("格式工具栏")
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # 加粗按钮
        bold_action = QAction("加粗", self)  # 使用文本 "B"
        bold_action.triggered.connect(self.toggle_bold)
        toolbar.addAction(bold_action)

        # 斜体按钮
        italic_action = QAction("斜体", self)  # 使用文本 "I"
        italic_action.triggered.connect(self.toggle_italic)
        toolbar.addAction(italic_action)

        # 居中按钮
        align_center_action = QAction("居中", self)
        align_center_action.triggered.connect(self.align_center)
        toolbar.addAction(align_center_action)

        # 下划线按钮
        underline_action = QAction("下划线", self)  # 使用文本 "_"
        underline_action.triggered.connect(self.toggle_underline)
        toolbar.addAction(underline_action)

        # 字体选择按钮 (F 按钮)
        font_action = QAction("字体", self)  # 使用文本 "F"
        font_action.triggered.connect(self.change_font)
        toolbar.addAction(font_action)

        # 字体选择下拉框
        self.font_combo = QComboBox()
        self.font_combo.addItems(["微软雅黑", "宋体", "黑体", "楷体", "Arial", "Times New Roman"])
        self.font_combo.currentTextChanged.connect(self.change_font_from_combo)
        toolbar.addWidget(self.font_combo)

        # 字号选择下拉框
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(i) for i in range(10, 33)])  # 字号范围 10-32
        self.font_size_combo.currentTextChanged.connect(self.change_font_size_from_combo)
        toolbar.addWidget(self.font_size_combo)

        # 颜色选择按钮
        self.color_button = QToolButton()
        self.color_button.setText("颜色")
        self.color_button.clicked.connect(self.change_color)
        toolbar.addWidget(self.color_button)

        # 常用颜色下拉框
        self.color_combo = QComboBox()
        self.color_combo.addItems(["黑色", "白色", "红色", "绿色", "蓝色", "黄色", "紫色", "橙色"])
        self.color_combo.currentTextChanged.connect(self.change_color_from_combo)
        toolbar.addWidget(self.color_combo)

        # 行距
        XL_action = QAction("行距:", self)
        toolbar.addAction(XL_action)

        # 调整行距按钮
        self.line_spacing_combo = QComboBox()
        self.line_spacing_combo.addItems([str(i) for i in range(10, 41)])  # 行距范围 10-40
        self.line_spacing_combo.currentTextChanged.connect(self.change_line_spacing)
        toolbar.addWidget(self.line_spacing_combo)

        # 背景颜色
        BG_action = QAction("背景:", self)
        toolbar.addAction(BG_action)

        # 背景颜色快速选择按钮
        self.bg_color_combo = QComboBox()
        self.bg_color_combo.addItems(["护眼绿", "白色", "黑色", "灰色"])
        self.bg_color_combo.currentTextChanged.connect(self.change_background_color)
        toolbar.addWidget(self.bg_color_combo)

        # 添加“常用”按钮
        self.toggle_favorites_button = QToolButton()
        self.toggle_favorites_button.setText("常用")
        self.toggle_favorites_button.setCheckable(True)  # 设置为可切换状态
        self.toggle_favorites_button.clicked.connect(self.toggle_favorites_view)
        toolbar.addWidget(self.toggle_favorites_button)


        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索内容")
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.on_search_clicked)
        toolbar.addWidget(QLabel(""))
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.search_button)


        # 按钮
        self.new_as_button = QPushButton('新建')
        self.new_as_button.clicked.connect(self.new_file)

        self.save_as_button = QPushButton('另存')
        self.save_as_button.clicked.connect(self.save_as)

        self.open_button = QPushButton('打开')
        self.open_button.clicked.connect(self.open_xml)

        self.clear_button = QPushButton('清空')  # 清空笔记按钮
        self.clear_button.clicked.connect(self.clear_notes)

        self.add_to_favorites_button = QPushButton('常用')  # 添加到常用文件列表按钮
        self.add_to_favorites_button.clicked.connect(self.add_to_favorites)

        self.about_button = QPushButton('关于')  # 关于按钮
        self.about_button.clicked.connect(self.show_about)

        # 常用文件列表
        self.favorites_list = QListWidget()
        self.favorites_list.itemClicked.connect(self.open_favorite_file)  # 点击常用文件列表项打开文件
        self.favorites_list.setContextMenuPolicy(Qt.CustomContextMenu)  # 启用右键菜单
        self.favorites_list.customContextMenuRequested.connect(self.show_favorites_context_menu)  # 连接右键菜单事件

        # 将常用文件列表放入一个单独的 QWidget 中
        self.favorites_widget = QWidget()
        favorites_layout = QVBoxLayout(self.favorites_widget)
        favorites_layout.addWidget(QLabel(""))
        favorites_layout.addWidget(self.favorites_list)

        # 默认隐藏常用文件列表区域
        self.favorites_widget.setVisible(False)

        # 布局
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.note_list)
        left_layout.addWidget(self.new_as_button)
        left_layout.addWidget(self.open_button)
        left_layout.addWidget(self.save_as_button)
        left_layout.addWidget(self.clear_button)  # 添加清空笔记按钮
        left_layout.addWidget(self.add_to_favorites_button)  # 添加到常用文件列表按钮
        left_layout.addWidget(self.about_button)  # 添加关于按钮

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.note_content)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 3)
        main_layout.addWidget(self.favorites_widget, 1)  # 将常用文件列表区域添加到主布局

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 支持 Ctrl+C 和 Ctrl+V
        self.note_content.keyPressEvent = self.custom_key_press_event

    def toggle_favorites_view(self):
        """切换常用文件列表视图的显示和隐藏状态"""
        is_visible = self.favorites_widget.isVisible()
        self.favorites_widget.setVisible(not is_visible)
        self.toggle_favorites_button.setChecked(not is_visible)

    def show_note_list_context_menu(self, pos):
        """显示笔记列表的右键菜单"""
        context_menu = QMenu(self)

        # 添加菜单项
        add_note_action = context_menu.addAction("新增笔记")
        add_note_action.triggered.connect(self.add_note)

        delete_note_action = context_menu.addAction("删除笔记")
        delete_note_action.triggered.connect(self.delete_note)

        # 显示菜单
        context_menu.exec_(self.note_list.mapToGlobal(pos))
    def new_file(self):
        """新建文件"""
        # 保存当前笔记内容
        if hasattr(self, 'current_note_title') and self.current_note_title:
            self.save_note()

        options = QFileDialog.Options()
        # 默认保存路径为工作目录，文件名为 notes-新建文件.xml
        default_file_name = os.path.join(self.work_dir, "notes-新建文件.xml")
        file_name, _ = QFileDialog.getSaveFileName(
            self, 
            "新建文件", 
            default_file_name,  # 默认路径和文件名
            "XML Files (*.xml);;All Files (*)", 
            options=options
        )
        if file_name:
            self.current_file = file_name
            self.root = ET.Element('notes')  # 创建新的根节点
            self.tree = ET.ElementTree(self.root)

            # 添加一个默认的“新笔记”
            new_note = ET.SubElement(self.root, 'note')
            ET.SubElement(new_note, 'title').text = "新笔记"
            ET.SubElement(new_note, 'content').text = ""

            # 保存文件
            self.tree.write(self.current_file)

            # 更新界面
            self.note_list.clear()  # 清空笔记列表
            self.note_list.addItem("新笔记")  # 添加“新笔记”到列表
            self.note_content.clear()  # 清空笔记内容
            self.setWindowTitle(f'笔记软件 v1.0 - {self.current_file}')  # 更新窗口标题

            # 将内容编辑框与“新笔记”关联
            self.current_note_title = "新笔记"
            self.note_list.setCurrentRow(0)  # 选中“新笔记”
            self.show_note_content()  # 显示“新笔记”的内容（此时内容为空）

    def add_note(self):
        """新增笔记"""
        while True:
            title, ok = QInputDialog.getText(self, '新增笔记', '请输入笔记标题:')
            if not ok:
                return  # 用户取消输入

            # 检查标题是否重复
            if title in [self.note_list.item(i).text() for i in range(self.note_list.count())]:
                QMessageBox.warning(self, "错误", "笔记标题不能重复，请重新输入！")
            else:
                break

        self.note_list.addItem(title)
        new_note = ET.SubElement(self.root, 'note')
        ET.SubElement(new_note, 'title').text = title
        ET.SubElement(new_note, 'content').text = ''
        self.tree.write(self.current_file)

    def rename_note(self, item):
        """双击修改笔记名称"""
        old_title = item.text()
        while True:
            new_title, ok = QInputDialog.getText(self, '改名', '请输入新的笔记标题:', text=old_title)
            if not ok:
                return  # 用户取消输入

            # 检查标题是否重复
            if new_title == old_title:
                break  # 标题未修改，直接退出

            if new_title in [self.note_list.item(i).text() for i in range(self.note_list.count())]:
                QMessageBox.warning(self, "错误", "笔记标题不能重复，请重新输入！")
            else:
                break

        # 更新笔记标题
        item.setText(new_title)
        for note in self.root.findall('note'):
            if note.find('title').text == old_title:
                note.find('title').text = new_title
                break
        self.tree.write(self.current_file)

    def delete_note(self):
        """删除笔记"""
        selected_item = self.note_list.currentItem()
        if selected_item:
            title = selected_item.text()
            for note in self.root.findall('note'):
                if note.find('title').text == title:
                    self.root.remove(note)
                    break
            self.tree.write(self.current_file)
            self.note_list.takeItem(self.note_list.row(selected_item))



    def custom_key_press_event(self, event):
        # 处理 Ctrl+C 和 Ctrl+V
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_C:  # Ctrl+C
                self.note_content.copy()
            elif event.key() == Qt.Key_V:  # Ctrl+V
                self.paste_image_or_text()
            elif event.key() == Qt.Key_A:  # Ctrl+A
                self.note_content.selectAll()
        else:
            QTextEdit.keyPressEvent(self.note_content, event)

    def paste_image_or_text(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasImage():  # 粘贴图片
            self.paste_image()
        elif mime_data.hasText():  # 粘贴文本
            # 获取剪贴板中的纯文本
            plain_text = mime_data.text()
            # 插入纯文本到笔记内容
            self.note_content.insertPlainText(plain_text)

    def paste_image(self):
        """粘贴图片并插入原始大小"""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasImage():
            image = QImage(mime_data.imageData())
            # 将图片转换为 Base64 编码
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            image.save(buffer, "PNG")
            base64_data = base64.b64encode(byte_array.data()).decode('utf-8')

            # 插入图片到笔记内容
            cursor = self.note_content.textCursor()
            image_format = QTextImageFormat()
            image_format.setName(f"data:image/png;base64,{base64_data}")
            cursor.insertImage(image_format)

    def resize_image(self, cursor):
        """调整图片大小"""
        # 获取图片格式
        image_format = cursor.charFormat().toImageFormat()
        if image_format.isValid():
            # 弹出调整大小的对话框
            dialog = ResizeImageDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                width, height = dialog.get_size()
                # 获取图片的 Base64 数据
                image_src = image_format.name()  # 获取图片的 src 属性
                if image_src.startswith("data:image/png;base64,"):
                    base64_data = image_src[len("data:image/png;base64,"):]
                    # 创建新的图片格式
                    new_image_format = QTextImageFormat()
                    new_image_format.setWidth(width)
                    new_image_format.setHeight(height)
                    new_image_format.setName(f"data:image/png;base64,{base64_data}")
                    # 删除原有图片
                    cursor.deleteChar()
                    # 插入调整大小后的图片
                    cursor.insertImage(new_image_format)

    def show_context_menu(self, pos):
        # 创建右键菜单
        context_menu = QMenu(self)

        # 添加菜单项
        undo_action = context_menu.addAction("撤销")
        undo_action.triggered.connect(self.note_content.undo)

        redo_action = context_menu.addAction("重做")
        redo_action.triggered.connect(self.note_content.redo)

        context_menu.addSeparator()

        copy_action = context_menu.addAction("复制")
        copy_action.triggered.connect(self.note_content.copy)

        paste_action = context_menu.addAction("粘贴")
        paste_action.triggered.connect(self.paste_image_or_text)

        context_menu.addSeparator()

        cut_action = context_menu.addAction("剪切")
        cut_action.triggered.connect(self.note_content.cut)

        delete_action = context_menu.addAction("删除")
        delete_action.triggered.connect(self.note_content.cut)  # 删除功能类似于剪切

        # 添加全选功能
        select_all_action = context_menu.addAction("全选")
        select_all_action.triggered.connect(self.note_content.selectAll)

        # 添加调整图片大小选项
        cursor = self.note_content.cursorForPosition(pos)
        image_format = cursor.charFormat().toImageFormat()
        if image_format.isValid():
            context_menu.addSeparator()
            resize_action = context_menu.addAction("调整图片大小")
            resize_action.triggered.connect(lambda: self.resize_image(cursor))

        # 显示菜单
        context_menu.exec_(self.note_content.mapToGlobal(pos))

    def load_notes(self):
        """加载笔记列表和内容"""
        try:
            # 清空笔记列表和内容
            self.note_list.clear()
            self.note_content.clear()
            self.current_note_title = None  # 重置当前笔记标题

            # 解析 XML 文件
            self.tree = ET.parse(self.current_file)
            self.root = self.tree.getroot()

            # 加载笔记列表
            for note in self.root.findall('note'):
                title = note.find('title').text
                self.note_list.addItem(title)

            # 默认显示第一个笔记的内容
            if self.note_list.count() > 0:
                self.note_list.setCurrentRow(0)
                self.show_note_content()
        except FileNotFoundError:
            # 如果文件不存在，初始化空的 XML 结构
            self.root = ET.Element('notes')
            self.tree = ET.ElementTree(self.root)
            self.tree.write(self.current_file)
            QMessageBox.information(self, "提示", "文件不存在，已创建新文件！")
        except ET.ParseError:
            QMessageBox.warning(self, "错误", "文件格式错误，无法加载！")

    def show_note_content(self):
        """显示当前选中的笔记内容"""
        selected_item = self.note_list.currentItem()
        if selected_item:
            self.current_note_title = selected_item.text()
            for note in self.root.findall('note'):
                if note.find('title').text == self.current_note_title:
                    content = note.find('content').text
                    self.note_content.setHtml(content)  # 使用 setHtml 加载带格式的内容
                    break

    def save_note(self):
        """保存当前笔记内容"""
        if hasattr(self, 'current_note_title') and self.current_note_title:
            # 清除高亮标记
            self.note_content.setExtraSelections([])
            
            # 保存内容
            content = self.note_content.toHtml()  # 使用 toHtml 保存带格式的内容
            for note in self.root.findall('note'):
                if note.find('title').text == self.current_note_title:
                    note.find('content').text = content
                    break
            self.tree.write(self.current_file)

    def clear_notes(self):
        """清空笔记"""
        # 弹出确认框
        confirm, ok = QInputDialog.getText(self, "确认清空", "请输入 'R' 确认清空所有笔记:")
        if ok and confirm == 'R':
            self.note_list.clear()
            self.note_content.clear()
            self.root.clear()  # 清空 XML 根节点
            self.tree.write(self.current_file)
            QMessageBox.information(self, "清空成功", "所有笔记已清空！")

    def open_xml(self):
        """打开一个新的 XML 文件"""
        # 保存当前笔记内容到旧文件
        if hasattr(self, 'current_note_title') and self.current_note_title:
            self.save_note()  # 保存到旧文件

        options = QFileDialog.Options()
        # 默认打开路径为工作目录
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "打开", 
            self.work_dir,  # 默认路径为工作目录
            "XML Files (*.xml);;All Files (*)", 
            options=options
        )
        if file_name:
            # 更新当前文件路径
            self.current_file = file_name
            self.setWindowTitle(f'笔记软件 v1.0 - {self.current_file}')  # 更新窗口标题

            # 重置状态
            self.current_note_title = None
            self.note_content.clear()

            # 加载新文件
            self.load_notes()

    def save_as(self):
        """另存为"""
        options = QFileDialog.Options()
        # 默认保存路径为工作目录，文件名为 notes-工作文件.xml
        default_file_name = os.path.join(self.work_dir, "notes-工作文件.xml")
        file_name, _ = QFileDialog.getSaveFileName(
            self, 
            "另存为", 
            default_file_name,  # 默认路径和文件名
            "XML Files (*.xml);;All Files (*)", 
            options=options
        )
        if file_name:
            self.tree.write(file_name)
            self.current_file = file_name
            self.setWindowTitle(f'笔记软件 v1.0 - {self.current_file}')  # 更新窗口标题

    def show_about(self):
        """显示关于信息"""
        QMessageBox.information(self, "关于", "开发者：sysucai\n411703730@qq.com")

    def change_font_from_combo(self, font_name):
        """从字体下拉框中选择字体并应用到文本（保持字号不变）"""
        cursor = self.note_content.textCursor()
        
        # 获取当前光标的字号
        current_font_size = cursor.charFormat().fontPointSize()
        
        # 创建一个新的 QFont 对象，设置字体名称并保持原有字号
        font = QFont(font_name)
        font.setPointSize(current_font_size)
        
        # 调用 change_font_with_font 函数
        self.change_font_with_font(font)

    def change_font_with_font(self, font):
        """使用传入的 QFont 对象更改字体（保持字号不变）"""
        cursor = self.note_content.textCursor()
        
        # 创建一个新的文本格式
        format = QTextCharFormat()
        format.setFont(font)  # 设置字体名称和字号

        if cursor.hasSelection():  # 如果有选中文本
            cursor.mergeCharFormat(format)
        else:  # 如果没有选中文本，应用到当前光标位置
            cursor.mergeCharFormat(format)
            self.note_content.setTextCursor(cursor)  # 更新光标位置
        
        self.note_content.update()  # 强制刷新 UI

    def change_font(self):
        """打开字体对话框选择字体"""
        cursor = self.note_content.textCursor()
        if cursor.hasSelection():
            # 设置默认字体为微软雅黑
            default_font = QFont("微软雅黑", 10)
            font, ok = QFontDialog.getFont(default_font, self, "选择字体")
            if ok:
                self.change_font_with_font(font)  # 调用辅助函数
        

    def change_font_size_from_combo(self, font_size):
        cursor = self.note_content.textCursor()
        format = QTextCharFormat()
        format.setFontPointSize(int(font_size))
        
        if cursor.hasSelection():  # 如果有选中文本
            cursor.mergeCharFormat(format)
        else:  # 如果没有选中文本，应用到当前光标位置
            cursor.mergeCharFormat(format)
            self.note_content.setTextCursor(cursor)
        
        # 强制刷新 UI
        self.note_content.update()
        self.note_content.repaint()
        
        # 打印调试信息
        #print(f"Changed font size to: {font_size}")
    def change_color(self):
        """从工具栏颜色按钮中选择颜色"""
        cursor = self.note_content.textCursor()
        if cursor.hasSelection():
            color = QColorDialog.getColor()
            if color.isValid():
                format = QTextCharFormat()
                format.setForeground(color)
                cursor.mergeCharFormat(format)

    def change_color_from_combo(self, color_name):
        """从工具栏颜色下拉框中选择颜色"""
        cursor = self.note_content.textCursor()
        if cursor.hasSelection():
            # 将颜色名称转换为 QColor
            color_map = {
                "黑色": QColor("black"),
                "白色": QColor("white"),
                "红色": QColor("red"),
                "绿色": QColor("green"),
                "蓝色": QColor("blue"),
                "黄色": QColor("yellow"),
                "紫色": QColor("purple"),
                "橙色": QColor("orange"),
            }
            color = color_map.get(color_name, QColor("black"))  # 默认黑色
            format = QTextCharFormat()
            format.setForeground(color)
            cursor.mergeCharFormat(format)

    def change_background_color(self, bg_color_name):
        """从工具栏背景颜色下拉框中选择背景颜色"""
        bg_color_map = {
            "白色": QColor("white"),
            "黑色": QColor("black"),
            "灰色": QColor("gray"),
            "护眼绿": QColor("#d7e8d5"),  # 修改为 #d7e8d5
        }
        bg_color = bg_color_map.get(bg_color_name, QColor("#d7e8d5"))  # 默认背景颜色为护眼绿
        self.note_content.setStyleSheet(f"background-color: {bg_color.name()}; color: black;")

    def align_center(self):
        """将选中的文本或段落居中"""
        cursor = self.note_content.textCursor()
        block_format = QTextBlockFormat()
        block_format.setAlignment(Qt.AlignCenter)
        cursor.mergeBlockFormat(block_format)

    def change_line_spacing(self, line_spacing):
        """调整行距"""
        cursor = self.note_content.textCursor()
        block_format = cursor.blockFormat()
        block_format.setLineHeight(int(line_spacing), QTextBlockFormat.FixedHeight)  # 固定行高
        cursor.mergeBlockFormat(block_format)

    def toggle_bold(self):
        cursor = self.note_content.textCursor()
        if cursor.hasSelection():
            format = QTextCharFormat()
            if cursor.charFormat().fontWeight() == QFont.Bold:
                format.setFontWeight(QFont.Normal)
            else:
                format.setFontWeight(QFont.Bold)
            cursor.mergeCharFormat(format)

    def toggle_italic(self):
        cursor = self.note_content.textCursor()
        if cursor.hasSelection():
            format = QTextCharFormat()
            format.setFontItalic(not cursor.charFormat().fontItalic())
            cursor.mergeCharFormat(format)

    def toggle_underline(self):
        cursor = self.note_content.textCursor()
        if cursor.hasSelection():
            format = QTextCharFormat()
            format.setFontUnderline(not cursor.charFormat().fontUnderline())
            cursor.mergeCharFormat(format)

    def load_notes_list(self):
        """加载常用文件列表"""
        try:
            # 解析 XML 文件
            tree = ET.parse(self.notes_list_file)
            root = tree.getroot()

            # 加载常用文件列表
            self.favorites_list.clear()
            for file in root.findall('file'):
                file_name = file.text
                self.favorites_list.addItem(file_name)
        except FileNotFoundError:
            # 如果文件不存在，初始化空的 XML 结构
            root = ET.Element('favorites')
            tree = ET.ElementTree(root)
            tree.write(self.notes_list_file)
        except ET.ParseError:
            QMessageBox.warning(self, "错误", "常用文件列表格式错误，无法加载！")

    def save_notes_list(self):
        """保存常用文件列表"""
        root = ET.Element('favorites')
        for i in range(self.favorites_list.count()):
            file_name = self.favorites_list.item(i).text()
            ET.SubElement(root, 'file').text = file_name
        tree = ET.ElementTree(root)
        tree.write(self.notes_list_file)

    def add_to_favorites(self):
        """将当前文件添加到常用文件列表"""
        if not self.current_file:
            return

        # 获取文件名（不带后缀）
        file_name = os.path.splitext(os.path.basename(self.current_file))[0]

        # 检查是否已经存在
        if file_name in [self.favorites_list.item(i).text() for i in range(self.favorites_list.count())]:
            QMessageBox.warning(self, "提示", "该文件已经在常用文件列表中！")
            return

        # 添加到常用文件列表
        self.favorites_list.addItem(file_name)
        self.save_notes_list()

    def open_favorite_file(self, item):
        """打开常用文件列表中的文件"""
        file_name = item.text() + ".xml"
        file_path = os.path.join(self.work_dir, file_name)

        if not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", f"文件 {file_name} 不存在！")
            return

        # 更新当前文件路径
        self.current_file = file_path
        self.setWindowTitle(f'笔记软件 v1.0 - {self.current_file}')  # 更新窗口标题

        # 重置状态
        self.current_note_title = None
        self.note_content.clear()

        # 加载新文件
        self.load_notes()

    def show_favorites_context_menu(self, pos):
        """显示常用文件列表的右键菜单"""
        context_menu = QMenu(self)

        # 添加菜单项
        remove_action = context_menu.addAction("移除")
        remove_action.triggered.connect(self.remove_from_favorites)

        # 显示菜单
        context_menu.exec_(self.favorites_list.mapToGlobal(pos))

    def remove_from_favorites(self):
        """从常用文件列表中移除选中的文件"""
        selected_item = self.favorites_list.currentItem()
        if selected_item:
            self.favorites_list.takeItem(self.favorites_list.row(selected_item))
            self.save_notes_list()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NoteApp()
    ex.show()
    sys.exit(app.exec_())
