import sys
import os
import random
import platform
import shutil 
import subprocess  # 新增
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QFileDialog, QMessageBox, QWidget, QVBoxLayout, QListWidget, QLabel,
    QDialog, QPushButton, QDateTimeEdit, QTimeEdit, QCheckBox, QMenu, QDesktopWidget, QGridLayout, QGroupBox, QLineEdit,
    QTextEdit, QListWidgetItem, QHBoxLayout
)
from PyQt5.QtGui import QIcon, QColor, QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QPoint, QProcess, QDateTime, QTimer
import shutil
import xml.etree.ElementTree as ET

os.chdir(os.path.dirname(os.path.abspath(__file__)))


# 获取用户主目录
home_dir = os.path.expanduser("~")

# 定义文件夹路径
folder_path = os.path.join(home_dir, "easynotes")

# 创建文件夹（如果不存在）
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

def EasyInf():
    inf = {
        '软件名称': '便捷任务栏',
        '版本号': '1.0.6',
        '功能介绍': '快速启动一些小工具。',
        'PID': '005',
        '分组': '效率',
        '依赖': 'pyqt5'
    }
    return inf

class RoundedWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor(46, 52, 64))  # 背景颜色
        painter.setBrush(brush)
        pen = QPen(Qt.NoPen)
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect(), 10, 10)  # 圆角矩形，圆角半径为10

class ReminderApp(QMainWindow):
    def __init__(self, check_interval=60000, parent=None):
        super().__init__(parent)
        self.check_interval = check_interval  # 默认检查间隔为 60000 毫秒
        self.day_to_number = {
            "星期一": "1",
            "星期二": "2",
            "星期三": "3",
            "星期四": "4",
            "星期五": "5",
            "星期六": "6",
            "星期日": "7",
        }
        self.print_today_info()
        self.initUI()
        self.load_settings()
        self.backup_clocks_file()
        self.load_reminders()
        # 设置关闭行为为隐藏窗口
        self.setAttribute(Qt.WA_DeleteOnClose, False)

    def closeEvent(self, event):
        # 重写 closeEvent，隐藏窗口而不是关闭
        self.hide()
        event.ignore()  # 忽略关闭事件，防止窗口被销毁

    def print_today_info(self):
        today = QDateTime.currentDateTime()
        date_str = today.toString('yyyy-MM-dd')
        day_of_week = today.toString('dddd')
        print(f"今天是：{date_str}，{day_of_week}")
        self.current_day_number = self.day_to_number.get(day_of_week, "1")
        print(f"当前星期数字: {self.current_day_number}")

    def initUI(self):
        self.setWindowTitle('提醒软件')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            background-color: black; 
            color: white;
            QPushButton {
                background-color: #444;
                color: white;
                border: 1px solid #555;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #888;
            }
            QTextEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
            }
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                max-width: 50px;
            }
        """)
        self.center()
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        self.temp_reminder_list = QListWidget()
        self.temp_reminder_list.setStyleSheet("background-color: #333; color: white;")
        self.temp_reminder_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.temp_reminder_list.customContextMenuRequested.connect(self.show_temp_context_menu)
        layout.addWidget(QLabel("临时提醒"))
        layout.addWidget(self.temp_reminder_list)
        self.repeat_reminder_list = QListWidget()
        self.repeat_reminder_list.setStyleSheet("background-color: #333; color: white;")
        self.repeat_reminder_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.repeat_reminder_list.customContextMenuRequested.connect(self.show_repeat_context_menu)
        layout.addWidget(QLabel("重复提醒"))
        layout.addWidget(self.repeat_reminder_list)
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(self.check_interval)  # 启动定时器

    def update_check_interval(self, interval):
        """更新检查提醒的时间间隔"""
        self.check_interval = interval
        self.timer.stop()  # 停止当前定时器
        self.timer.start(self.check_interval)  # 使用新的时间间隔启动定时器

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def load_settings(self):
        if not os.path.exists('setting.xml'):
            self.work_dir = os.getcwd()
            self.create_settings_file()
        else:
            tree = ET.parse('setting.xml')
            root = tree.getroot()
            self.work_dir = root.find('work_dir').text

    def create_settings_file(self):
        root = ET.Element('settings')
        work_dir = ET.SubElement(root, 'work_dir')
        work_dir.text = self.work_dir
        tree = ET.ElementTree(root)
        tree.write('setting.xml', encoding='UTF-8', xml_declaration=True)

    def backup_clocks_file(self):
        backup_dir = os.path.join(self.work_dir, 'backup')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        clocks_file = os.path.join(self.work_dir, 'myclocks.xml')
        if not os.path.exists(clocks_file):
            return
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith('clock') and f.endswith('.xml')]
        backup_files.sort()
        if len(backup_files) >= 20:
            os.remove(os.path.join(backup_dir, backup_files[0]))
        new_backup_name = f"clock{len(backup_files) + 1}.xml"
        shutil.copy(clocks_file, os.path.join(backup_dir, new_backup_name))

    def load_reminders(self):
        if not os.path.exists(os.path.join(self.work_dir, 'myclocks.xml')):
            self.temp_reminders = {}
            self.repeat_reminders = {}
            self.save_reminders()
        else:
            tree = ET.parse(os.path.join(self.work_dir, 'myclocks.xml'))
            root = tree.getroot()
            self.temp_reminders = self.parse_reminders(root.find('temp_reminders'))
            self.repeat_reminders = self.parse_reminders(root.find('repeat_reminders'))
            self.update_reminder_lists()

    def parse_reminders(self, element):
        reminders = {}
        if element is not None:
            for reminder in element.findall('reminder'):
                reminder_id = reminder.find('id').text
                reminders[reminder_id] = {
                    'id': reminder_id,
                    'time': reminder.find('time').text,
                    'content': reminder.find('content').text,
                    'completed': reminder.find('completed').text == 'True',
                }
                if reminder.find('days') is not None:
                    reminders[reminder_id]['days'] = reminder.find('days').text
                else:
                    reminders[reminder_id]['days'] = ''
                if reminder.find('last_completed_day') is not None:
                    reminders[reminder_id]['last_completed_day'] = reminder.find('last_completed_day').text
                else:
                    reminders[reminder_id]['last_completed_day'] = ''
        return reminders

    def update_reminder_lists(self):
        self.temp_reminder_list.clear()
        for reminder_id, reminder in sorted(self.temp_reminders.items(), key=lambda x: x[1]['time']):
            item = QListWidgetItem(f"{reminder['time']} - {reminder['content']} (ID: {reminder_id})")
            if reminder['completed']:
                item.setBackground(QColor('green'))
            self.temp_reminder_list.addItem(item)
        self.repeat_reminder_list.clear()
        for reminder_id, reminder in self.repeat_reminders.items():
            days = self.format_days(reminder['days']) if reminder['days'] else '每天'
            item = QListWidgetItem(f"{days} {reminder['time']} - {reminder['content']} (ID: {reminder_id})")
            if reminder['last_completed_day'] == self.current_day_number and reminder['completed']:
                item.setBackground(QColor('green'))
            else:
                item.setBackground(QColor('black'))
            self.repeat_reminder_list.addItem(item)

    def format_days(self, days_str):
        day_map = {'1': '一', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '7': '日'}
        days = days_str.split()
        return ' '.join([day_map[day] for day in days])

    def save_reminders(self):
        root = ET.Element('reminders')
        temp_reminders_elem = ET.SubElement(root, 'temp_reminders')
        for reminder_id, reminder in self.temp_reminders.items():
            reminder_elem = ET.SubElement(temp_reminders_elem, 'reminder')
            ET.SubElement(reminder_elem, 'id').text = reminder_id
            ET.SubElement(reminder_elem, 'time').text = reminder['time']
            ET.SubElement(reminder_elem, 'content').text = reminder['content']
            ET.SubElement(reminder_elem, 'completed').text = str(reminder['completed'])
        repeat_reminders_elem = ET.SubElement(root, 'repeat_reminders')
        for reminder_id, reminder in self.repeat_reminders.items():
            reminder_elem = ET.SubElement(repeat_reminders_elem, 'reminder')
            ET.SubElement(reminder_elem, 'id').text = reminder_id
            ET.SubElement(reminder_elem, 'time').text = reminder['time']
            ET.SubElement(reminder_elem, 'content').text = reminder['content']
            ET.SubElement(reminder_elem, 'completed').text = str(reminder['completed'])
            ET.SubElement(reminder_elem, 'days').text = reminder['days']
            ET.SubElement(reminder_elem, 'last_completed_day').text = reminder['last_completed_day']
        tree = ET.ElementTree(root)
        tree.write(os.path.join(self.work_dir, 'myclocks.xml'), encoding='UTF-8', xml_declaration=True)

    def generate_unique_id(self):
        while True:
            reminder_id = str(random.randint(10000, 99999))
            if reminder_id not in self.temp_reminders and reminder_id not in self.repeat_reminders:
                return reminder_id

    def show_temp_context_menu(self, position):
        menu = QMenu()
        add_action = menu.addAction("新增提醒")
        edit_action = menu.addAction("编辑提醒")
        delete_action = menu.addAction("删除提醒")
        action = menu.exec_(self.temp_reminder_list.mapToGlobal(position))
        if action == add_action:
            self.add_reminder(is_temp=True)
        elif action == edit_action:
            self.edit_temp_reminder()
        elif action == delete_action:
            self.delete_temp_reminder()

    def show_repeat_context_menu(self, position):
        menu = QMenu()
        add_action = menu.addAction("新增提醒")
        edit_action = menu.addAction("编辑提醒")
        delete_action = menu.addAction("删除提醒")
        action = menu.exec_(self.repeat_reminder_list.mapToGlobal(position))
        if action == add_action:
            self.add_reminder(is_temp=False)
        elif action == edit_action:
            self.edit_repeat_reminder()
        elif action == delete_action:
            self.delete_repeat_reminder()

    def add_reminder(self, is_temp=True, reminder=None, reminder_id=None):
        dialog = QDialog(self)
        dialog.setWindowTitle('编辑提醒' if reminder else '新增提醒')
        dialog.setGeometry(100, 100, 350, 300)
        dialog.setStyleSheet("background-color: black; color: white;")
        dialog.center = lambda: dialog.move(
            (QDesktopWidget().screenGeometry().width() - dialog.width()) // 2,
            (QDesktopWidget().screenGeometry().height() - dialog.height()) // 2
        )
        dialog.center()
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        time_group = QGroupBox("提醒时间")
        time_layout = QGridLayout()
        if is_temp:
            self.date_time_edit = QDateTimeEdit(QDateTime.currentDateTime())
            if reminder:
                self.date_time_edit.setDateTime(QDateTime.fromString(reminder['time'], 'yyyy-MM-dd HH:mm'))
            time_layout.addWidget(QLabel("日期和时间:"), 0, 0)
            time_layout.addWidget(self.date_time_edit, 0, 1)
        else:
            self.time_edit = QTimeEdit(QDateTime.currentDateTime().time())
            if reminder:
                self.time_edit.setTime(QDateTime.fromString(reminder['time'], 'HH:mm').time())
            time_layout.addWidget(QLabel("时间:"), 0, 0)
            time_layout.addWidget(self.time_edit, 0, 1)
            self.day_checkboxes = []
            days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            for i, day in enumerate(days):
                checkbox = QCheckBox(day)
                if reminder and str(i + 1) in reminder['days'].split():
                    checkbox.setChecked(True)
                self.day_checkboxes.append(checkbox)
                time_layout.addWidget(checkbox, 1 + i // 4, i % 4)
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        self.content_edit = QTextEdit()
        if reminder:
            self.content_edit.setText(reminder['content'])
        layout.addWidget(QLabel("提醒内容:"))
        layout.addWidget(self.content_edit)
        self.completed_checkbox = QCheckBox("已完成")
        if reminder:
            self.completed_checkbox.setChecked(reminder['completed'])
        layout.addWidget(self.completed_checkbox)
        confirm_button = QPushButton("确认")
        confirm_button.clicked.connect(lambda: self.save_reminder(dialog, is_temp, reminder, reminder_id))
        layout.addWidget(confirm_button)
        dialog.exec_()

    def save_reminder(self, dialog, is_temp, reminder=None, reminder_id=None):
        content = self.content_edit.toPlainText()
        if not content:
            QMessageBox.warning(self, "错误", "提醒内容不能为空！")
            return
        if is_temp:
            time = self.date_time_edit.dateTime().toString('yyyy-MM-dd HH:mm')
            if reminder:
                reminder.update({
                    'time': time,
                    'content': content,
                    'completed': self.completed_checkbox.isChecked()
                })
            else:
                reminder_id = self.generate_unique_id()
                self.temp_reminders[reminder_id] = {
                    'id': reminder_id,
                    'time': time,
                    'content': content,
                    'completed': self.completed_checkbox.isChecked(),
                    'days': '',
                    'last_completed_day': ''
                }
        else:
            time = self.time_edit.time().toString('HH:mm')
            days = []
            for i, checkbox in enumerate(self.day_checkboxes):
                if checkbox.isChecked():
                    days.append(str(i + 1))
            if not days:
                QMessageBox.warning(self, "错误", "请选择至少一个重复日期！")
                return
            days_str = ' '.join(days)
            if reminder:
                reminder.update({
                    'time': time,
                    'content': content,
                    'days': days_str,
                    'completed': self.completed_checkbox.isChecked()
                })
            else:
                reminder_id = self.generate_unique_id()
                self.repeat_reminders[reminder_id] = {
                    'id': reminder_id,
                    'time': time,
                    'content': content,
                    'completed': self.completed_checkbox.isChecked(),
                    'days': days_str,
                    'last_completed_day': ''
                }
        self.update_reminder_lists()
        self.save_reminders()
        dialog.accept()

    def edit_temp_reminder(self):
        selected_item = self.temp_reminder_list.currentItem()
        if selected_item:
            reminder_id = selected_item.text().split("(ID: ")[1][:-1]
            reminder = self.temp_reminders[reminder_id]
            self.add_reminder(is_temp=True, reminder=reminder, reminder_id=reminder_id)

    def edit_repeat_reminder(self):
        selected_item = self.repeat_reminder_list.currentItem()
        if selected_item:
            reminder_id = selected_item.text().split("(ID: ")[1][:-1]
            reminder = self.repeat_reminders[reminder_id]
            self.add_reminder(is_temp=False, reminder=reminder, reminder_id=reminder_id)

    def delete_temp_reminder(self):
        selected_item = self.temp_reminder_list.currentItem()
        if selected_item:
            reminder_id = selected_item.text().split("(ID: ")[1][:-1]
            del self.temp_reminders[reminder_id]
            self.update_reminder_lists()
            self.save_reminders()

    def delete_repeat_reminder(self):
        selected_item = self.repeat_reminder_list.currentItem()
        if selected_item:
            reminder_id = selected_item.text().split("(ID: ")[1][:-1]
            del self.repeat_reminders[reminder_id]
            self.update_reminder_lists()
            self.save_reminders()


    def check_reminders(self):
        self.print_today_info()  # 更新当前星期数字
        current_datetime = QDateTime.currentDateTime()
        current_time = current_datetime.toString('HH:mm')
        today_date = current_datetime.date()  # 获取当前日期

        # 检查临时提醒
        temp_reminders_to_delete = []  # 用于存储需要删除的临时提醒ID
        for reminder_id, reminder in self.temp_reminders.items():
            reminder_time = QDateTime.fromString(reminder['time'], 'yyyy-MM-dd HH:mm')
            reminder_date = reminder_time.date()
            if reminder['completed'] and reminder_date < today_date:
                # 如果提醒已完成且日期是今日之前的，则记录下来
                temp_reminders_to_delete.append(reminder_id)
            elif reminder_time <= current_datetime and not reminder['completed']:
                # 如果提醒时间已到且未完成，则显示提醒
                print(f"Showing temp reminder: {reminder['content']}")  # 调试信息
                self.show_reminder_dialog(reminder_id, reminder)
                reminder['completed'] = True  # 立即标记为完成，避免重复触发
                self.save_reminders()
                return  # 只处理一个提醒，避免多个提醒同时弹出

        # 删除已完成且日期是今日之前的临时提醒
        for reminder_id in temp_reminders_to_delete:
            del self.temp_reminders[reminder_id]
            print(f"Deleted completed temp reminder with ID: {reminder_id}")  # 调试信息

        # 更新提醒列表
        self.update_reminder_lists()

        # 检查重复提醒
        for reminder_id, reminder in self.repeat_reminders.items():
            if self.current_day_number in reminder['days'].split() and reminder['time'] <= current_time:
                if reminder['last_completed_day'] != self.current_day_number or not reminder['completed']:
                    print(f"Showing repeat reminder: {reminder['content']}")  # 调试信息
                    self.show_reminder_dialog(reminder_id, reminder)
                    reminder['last_completed_day'] = self.current_day_number  # 更新最后完成日期
                    reminder['completed'] = True  # 立即标记为完成，避免重复触发
                    self.save_reminders()
                    return  # 只处理一个提醒，避免多个提醒同时弹出

    def check_reminders_old(self):
        current_datetime = QDateTime.currentDateTime()
        current_time = current_datetime.toString('HH:mm')
        #print(f"Checking reminders at {current_time}")  # 调试信息

        # 检查临时提醒
        for reminder_id, reminder in self.temp_reminders.items():
            reminder_time = QDateTime.fromString(reminder['time'], 'yyyy-MM-dd HH:mm')
            if reminder_time <= current_datetime and not reminder['completed']:
                print(f"Showing temp reminder: {reminder['content']}")  # 调试信息
                # 弹出提醒对话框
                self.show_reminder_dialog(reminder_id, reminder)
                reminder['completed'] = True  # 立即标记为完成，避免重复触发
                self.save_reminders()
                return  # 只处理一个提醒，避免多个提醒同时弹出

        # 检查重复提醒
        for reminder_id, reminder in self.repeat_reminders.items():
            if self.current_day_number in reminder['days'].split() and reminder['time'] <= current_time:
                if reminder['last_completed_day'] != self.current_day_number or not reminder['completed']:
                    print(f"Showing repeat reminder: {reminder['content']}")  # 调试信息
                    # 弹出提醒对话框
                    self.show_reminder_dialog(reminder_id, reminder)
                    reminder['last_completed_day'] = self.current_day_number  # 更新最后完成日期
                    reminder['completed'] = True  # 立即标记为完成，避免重复触发
                    self.save_reminders()
                    return  # 只处理一个提醒，避免多个提醒同时弹出

    def show_reminder_dialog(self, reminder_id, reminder):
        dialog = QDialog(self.parent())  # 确保父窗口是 MainWindow
        dialog.setWindowTitle('提醒')
        dialog.setGeometry(100, 100, 400, 300)
        dialog.setStyleSheet("""
            background-color: black; 
            color: white;
            QPushButton {
                background-color: #444;
                color: white;
                border: 1px solid #555;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #888;
            }
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                max-width: 50px;
            }
            QTextEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
            }
        """)
        dialog.center = lambda: dialog.move(
            (QDesktopWidget().screenGeometry().width() - dialog.width()) // 2,
            (QDesktopWidget().screenGeometry().height() - dialog.height()) // 2
        )
        dialog.center()
        layout = QVBoxLayout()
        dialog.setLayout(layout)

        # 提醒内容（可编辑）
        self.content_edit = QTextEdit(reminder['content'])  # 使用 QTextEdit 替代 QLabel
        self.content_edit.setStyleSheet("background-color: #333; color: white;")
        self.content_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 添加垂直滚动条
        layout.addWidget(QLabel("提醒内容:"))
        layout.addWidget(self.content_edit)

        # 自定义延迟时间输入框
        self.snooze_time_edit = QLineEdit()
        self.snooze_time_edit.setPlaceholderText("分钟")
        self.snooze_time_edit.setText("10")  # 设置默认值为 10 分钟
        layout.addWidget(QLabel("延迟时间（分钟）:"))
        layout.addWidget(self.snooze_time_edit)

        # 按钮布局
        button_layout = QHBoxLayout()
        done_button = QPushButton('完成')
        done_button.clicked.connect(lambda: self.mark_reminder_done(reminder_id, reminder, dialog))
        button_layout.addWidget(done_button)

        snooze_button = QPushButton('以后提醒')
        if reminder.get('days', ''):
            snooze_button.clicked.connect(lambda: self.snooze_repeat_reminder(reminder_id, reminder, dialog))
        else:
            snooze_button.clicked.connect(lambda: self.snooze_temp_reminder(reminder_id, reminder, dialog))
        button_layout.addWidget(snooze_button)

        layout.addLayout(button_layout)
        dialog.exec_()

    def snooze_repeat_reminder(self, reminder_id, reminder, dialog):
        try:
            snooze_minutes = int(self.snooze_time_edit.text())
            if snooze_minutes <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的正整数值！")
            return

        # 更新提醒内容
        reminder['content'] = self.content_edit.toPlainText()
        # 标记当前提醒为完成
        reminder['completed'] = True
        reminder['last_completed_day'] = self.current_day_number

        # 生成一个临时提醒
        new_time = QDateTime.currentDateTime().addSecs(snooze_minutes * 60).toString('yyyy-MM-dd HH:mm')
        temp_reminder_id = self.generate_unique_id()
        self.temp_reminders[temp_reminder_id] = {
            'id': temp_reminder_id,
            'time': new_time,
            'content': reminder['content'],
            'completed': False,
            'days': '',
            'last_completed_day': ''
        }

        self.update_reminder_lists()
        self.save_reminders()
        dialog.close()  # 关闭对话框，不退出程序

    def mark_reminder_done(self, reminder_id, reminder, dialog):
        print("Marking reminder as done")  # 调试信息
        # 更新提醒内容
        reminder['content'] = self.content_edit.toPlainText()
        # 标记提醒为完成
        reminder['completed'] = True
        if 'days' in reminder:  # 如果是重复提醒，更新最后完成日期
            reminder['last_completed_day'] = self.current_day_number
        self.update_reminder_lists()
        self.save_reminders()
        dialog.close()  # 关闭对话框，不退出程序

    def snooze_temp_reminder(self, reminder_id, reminder, dialog):
        try:
            snooze_minutes = int(self.snooze_time_edit.text())
            if snooze_minutes <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的正整数值！")
            return

        # 更新提醒内容和时间
        reminder['content'] = self.content_edit.toPlainText()
        reminder_time = QDateTime.fromString(reminder['time'], 'yyyy-MM-dd HH:mm')
        new_time = reminder_time.addSecs(snooze_minutes * 60).toString('yyyy-MM-dd HH:mm')
        reminder['time'] = new_time
        reminder['completed'] = False
        self.update_reminder_lists()
        self.save_reminders()
        dialog.close()  # 关闭对话框，不退出程序

class ConfigDialog(QDialog):
    def __init__(self, python_command, work_dir, check_interval, parent=None):
        super().__init__(parent)
        self.setWindowTitle("配置")
        self.setGeometry(100, 100, 400, 250)  # 增加窗口高度以容纳新的输入框
        self.setStyleSheet("background-color: black; color: white;")
        self.center()  # 调用居中方法

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Python 启动命令
        self.python_command_edit = QLineEdit(python_command)
        self.python_command_edit.setPlaceholderText("请输入 Python 启动命令（如 python）")
        layout.addWidget(QLabel("Python 启动命令:"))
        layout.addWidget(self.python_command_edit)

        # 工作目录
        self.work_dir_edit = QLineEdit(work_dir)
        self.work_dir_edit.setPlaceholderText("请输入工作目录")
        layout.addWidget(QLabel("工作目录:"))
        layout.addWidget(self.work_dir_edit)

        # 选择工作目录按钮
        browse_button = QPushButton("选择工作目录")
        browse_button.clicked.connect(self.browse_work_dir)
        layout.addWidget(browse_button)

        # 检查提醒的时间间隔（毫秒）
        self.check_interval_edit = QLineEdit(str(check_interval))
        self.check_interval_edit.setPlaceholderText("请输入检查提醒的时间间隔（毫秒）")
        layout.addWidget(QLabel("检查提醒的时间间隔（毫秒）:"))
        layout.addWidget(self.check_interval_edit)

        # 确认按钮
        confirm_button = QPushButton("确认")
        confirm_button.clicked.connect(self.accept)
        layout.addWidget(confirm_button)

    def browse_work_dir(self):
        """打开文件对话框选择工作目录"""
        work_dir = QFileDialog.getExistingDirectory(self, "选择工作目录",  os.path.join(os.path.expanduser("~"), "easynotes"))
        if work_dir:
            self.work_dir_edit.setText(work_dir)

    def get_config(self):
        """获取用户输入的配置"""
        return {
            "python_command": self.python_command_edit.text().strip(),
            "work_dir": self.work_dir_edit.text().strip(),
            "check_interval": int(self.check_interval_edit.text().strip())  # 获取时间间隔
        }

    def center(self):
        """将窗口居中显示"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("工具条")
        self.setGeometry(100, 100, 420, 30)
        self.setStyleSheet("""
            QMainWindow {
                background-color: transparent;
            }
            QToolBar {
                background-color: transparent;
                border: none;
                padding: 0px;
                spacing: 2px;
            }
            QToolButton {
                color: #ECEFF4;
                background-color: #4C566A;
                border: none;
                padding: 5px;
                margin: 0px;
                font-size: 12px;
                min-width: 25px;
                border-radius: 5px;
            }
            QToolButton:hover {
                background-color: #5E81AC;
            }
            QToolButton:pressed {
                background-color: #81A1C1;
            }
        """)
        
        # 定义为类的成员变量
        self.toolbar = QToolBar("主工具栏")
        self.toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # 工具按钮
        self.notes_action = QAction(QIcon(), "笔记", self)
        self.notes_action.triggered.connect(self.run_easynotes)
        self.toolbar.addAction(self.notes_action)

        self.task_action = QAction(QIcon(), "任务", self)
        self.task_action.triggered.connect(self.run_task)
        self.toolbar.addAction(self.task_action)

        self.mindmap_action = QAction(QIcon(), "导图", self)
        self.mindmap_action.triggered.connect(self.run_mind)
        self.toolbar.addAction(self.mindmap_action)

        self.calcmap_action = QAction(QIcon(), "计算", self)
        self.calcmap_action.triggered.connect(self.run_calc)
        self.toolbar.addAction(self.calcmap_action)

        self.reminder_action = QAction(QIcon(), "提醒", self)
        self.reminder_action.triggered.connect(self.show_reminder_app)
        self.toolbar.addAction(self.reminder_action)

        # 易析按钮
        #self.stat_action = QAction(QIcon(), "易析", self)
        #self.stat_action.triggered.connect(self.run_easystat)
        #self.toolbar.addAction(self.stat_action)

        self.py_action = QAction(QIcon(), "工具", self)
        self.py_action.triggered.connect(self.run_py)
        self.toolbar.addAction(self.py_action)

        self.pdca_action = QAction(QIcon(), "截图", self)
        self.pdca_action.triggered.connect(self.run_pdca)
        self.toolbar.addAction(self.pdca_action)

        # 配置按钮
        self.config_action = QAction(QIcon(), "配置", self)
        self.config_action.triggered.connect(self.show_config_dialog)
        self.toolbar.addAction(self.config_action)

        # 收缩按钮
        self.toggle_action = QAction(QIcon(), "收缩", self)
        self.toggle_action.triggered.connect(self.toggle_toolbar)
        self.toolbar.addAction(self.toggle_action)

        # 关闭按钮
        self.close_action = QAction(QIcon(), '×', self)
        self.close_action.triggered.connect(self.close)
        self.toolbar.addAction(self.close_action)

        # 初始化变量
        self.dragging = False
        self.offset = QPoint()
        self.notes_process = QProcess(self)
        self.mind_process = QProcess(self)
        self.calc_process = QProcess(self)
        self.py_process = QProcess(self)
        self.task_process = QProcess(self)
        self.pdca_process = QProcess(self)
        self.stat_process = QProcess(self)
        self.is_collapsed = False  # 新增收缩状态标志
        self.moveToTopRight()

        # 连接 QProcess 的错误信号
        self.notes_process.errorOccurred.connect(lambda: print(f"笔记脚本启动失败: {self.notes_process.errorString()}"))
        self.mind_process.errorOccurred.connect(lambda: print(f"导图脚本启动失败: {self.mind_process.errorString()}"))
        self.calc_process.errorOccurred.connect(lambda: print(f"导图脚本启动失败: {self.calc_process.errorString()}"))

        self.task_process.errorOccurred.connect(lambda: print(f"任务脚本启动失败: {self.task_process.errorString()}"))
        self.pdca_process.errorOccurred.connect(lambda: print(f"截图脚本启动失败: {self.pdca_process.errorString()}"))
        self.stat_process.errorOccurred.connect(lambda: print(f"易析脚本启动失败: {self.stat_process.errorString()}"))

        # 加载配置
        self.setting_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setting.xml")
        self.config = self.load_or_create_setting()
        self.python_command = self.config.get("python_command", "python")
        self.work_dir = self.config.get("work_dir", os.path.join(os.path.expanduser("~"), "easynotes"))

        # 提醒窗口
        self.reminder_app = ReminderApp(self.config.get("check_interval", 60000), self)
        self.reminder_app.hide()

    def toggle_toolbar(self):
        """切换工具条的收缩状态"""
        if self.is_collapsed:
            # 恢复原状
            for action in self.toolbar.actions():
                if action != self.toggle_action:  # 不包括收缩按钮本身
                    action.setVisible(True)
            self.is_collapsed = False
            self.toggle_action.setText("收缩")
            self.resize(420, 30)  # 恢复原始宽度
        else:
            # 收缩工具条
            for action in self.toolbar.actions():
                if action != self.toggle_action:  # 不包括收缩按钮本身
                    action.setVisible(False)
            self.is_collapsed = True
            self.toggle_action.setText("展开")
            self.resize(50, 30)  # 收缩后的宽度
        self.moveToTopRight()  # 重新定位窗口
            
    def show_reminder_app(self):
        """显示提醒窗口"""
        if self.reminder_app.isHidden():
            self.reminder_app.show()
        else:
            self.reminder_app.activateWindow()  # 如果窗口已经显示，则激活它

    def show_config_dialog(self):
        """显示配置对话框"""
        dialog = ConfigDialog(self.python_command, self.work_dir, self.config["check_interval"], self)
        if dialog.exec_() == QDialog.Accepted:
            config = dialog.get_config()
            self.python_command = config["python_command"]
            self.work_dir = config["work_dir"]
            self.config["check_interval"] = config["check_interval"]  # 更新检查间隔
            self.save_setting(config)
            # 更新 ReminderApp 的检查间隔
            self.reminder_app.update_check_interval(config["check_interval"])

    def load_or_create_setting(self):
        """加载或创建配置文件"""
        if not os.path.exists(self.setting_file):
            # 如果配置文件不存在，创建默认配置
            config = {
                "python_command": "python",
                "work_dir":  os.path.join(os.path.expanduser("~"), "easynotes"),
                "check_interval": 60000  # 默认检查间隔为 60000 毫秒（1 分钟）
            }
            self.save_setting(config)
            return config
        else:
            # 如果配置文件存在，加载配置
            tree = ET.parse(self.setting_file)
            root = tree.getroot()
            config = {
                "python_command": root.find("python_command").text if root.find("python_command") is not None else "python3",
                "work_dir": root.find("work_dir").text if root.find("work_dir") is not None else  os.path.join(os.path.expanduser("~"), "easynotes"),
                "check_interval": int(root.find("check_interval").text) if root.find("check_interval") is not None else 60000
            }
            return config

    def save_setting(self, config):
        """保存配置到 setting.xml"""
        root = ET.Element("settings")
        ET.SubElement(root, "python_command").text = config["python_command"]
        ET.SubElement(root, "work_dir").text = config["work_dir"]
        ET.SubElement(root, "check_interval").text = str(config["check_interval"])  # 保存时间间隔
        tree = ET.ElementTree(root)
        tree.write(self.setting_file, encoding="utf-8", xml_declaration=True)

    def run_easynotes(self):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes.py")

        if not os.path.exists(script_path):
            QMessageBox.warning(self, "错误", f"未找到脚本: {script_path}")
            return
        if self.notes_process.state() == QProcess.Running:
            self.notes_process.terminate()
            self.notes_process.waitForFinished()
        self.notes_process.start(self.python_command, [script_path])

    def run_mind(self):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mind.py")

        if not os.path.exists(script_path):
            QMessageBox.warning(self, "错误", f"未找到脚本: {script_path}")
            return
        if self.mind_process.state() == QProcess.Running:
            self.mind_process.terminate()
            self.mind_process.waitForFinished()
        self.mind_process.start(self.python_command, [script_path])

    def run_task(self):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "task.py")

        if not os.path.exists(script_path):
            QMessageBox.warning(self, "错误", f"未找到脚本: {script_path}")
            return
        if self.task_process.state() == QProcess.Running:
            self.task_process.terminate()
            self.task_process.waitForFinished()
        self.task_process.start(self.python_command, [script_path])

    def run_pdca(self):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cut.py")

        if not os.path.exists(script_path):
            QMessageBox.warning(self, "错误", f"未找到脚本: {script_path}")
            return
        if self.pdca_process.state() == QProcess.Running:
            self.pdca_process.terminate()
            self.pdca_process.waitForFinished()
        self.pdca_process.start(self.python_command, [script_path])

    def run_py(self):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "easypymanager.py")

        if not os.path.exists(script_path):
            QMessageBox.warning(self, "错误", f"未找到脚本: {script_path}")
            return
        if self.py_process.state() == QProcess.Running:
            self.py_process.terminate()
            self.py_process.waitForFinished()
        self.py_process.start(self.python_command, [script_path])
        

    def run_calc(self):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calc.py")

        if not os.path.exists(script_path):
            QMessageBox.warning(self, "错误", f"未找到脚本: {script_path}")
            return
        if self.calc_process.state() == QProcess.Running:
            self.calc_process.terminate()
            self.calc_process.waitForFinished()
        self.calc_process.start(self.python_command, [script_path])
        
    def run_easystat(self):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "easystat.py")

        if not os.path.exists(script_path):
            QMessageBox.warning(self, "错误", f"未找到脚本: {script_path}")
            return
        
        # 根据操作系统选择启动命令
        if platform.system() == "Windows":
            # Windows 系统：使用 cmd.exe 启动并保持窗口打开
            # 确保路径用双引号括起来
            command = f'cmd.exe /k {self.python_command} {script_path}'
                # 启动终端输出弹窗
            subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # Linux 系统：使用 gnome-terminal 或其他终端启动
            terminal = self.get_linux_terminal()  # 获取可用的 Linux 终端
            if not terminal:
                QMessageBox.warning(self, "错误", "未找到可用的终端程序！")
                return
            command = f'{terminal} -e "{self.python_command} {script_path}"'
            
            # 使用 subprocess 启动
            subprocess.Popen(command, shell=True)
       

    def get_linux_terminal(self):
        """获取 Linux 系统可用的终端程序"""
        terminals = ["gnome-terminal", "xterm", "konsole", "xfce4-terminal", "mate-terminal"]
        for terminal in terminals:
            if shutil.which(terminal):  # 检查终端是否可用
                return terminal
        return None
        
    def moveToTopRight(self):
        screen_geometry = QApplication.desktop().screenGeometry()
        screen_width = screen_geometry.width()
        window_width = self.width()
        x = int(screen_width * 0.75) - window_width
        y = 0
        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
