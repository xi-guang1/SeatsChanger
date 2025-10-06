from PyQt5.QtCore import QDataStream, QIODevice, QMimeData, QVariant, Qt
from PyQt5.QtGui import QDrag, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QSpinBox as SpinBox,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    PrimaryPushButton,
    PushButton,
    SubtitleLabel,
    TitleLabel,
    ToolTipFilter,
    ToolTipPosition,
)


class DraggableLabel(QLabel):
    """可拖拽的学生姓名标签控件
    
    用于在学生列表中显示姓名，并支持拖拽到座位控件中
    """
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._init_ui()

    def _init_ui(self):
        """初始化UI样式和属性"""
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            DraggableLabel {
                background-color: #e3f2fd;
                border: 1px solid #90caf9;
                border-radius: 8px;
                padding: 8px 12px;
                margin: 2px;
                font-weight: 600;
                font-size: 14px;
            }
            DraggableLabel:hover {
                background-color: #bbdefb;
                border-color: #64b5f6;
            }
        """)
        self.setFixedHeight(40)
        self.setMouseTracking(True)  # 启用鼠标跟踪以显示工具提示
        self.installEventFilter(ToolTipFilter(self, 200, ToolTipPosition.TOP))
        
        # 启用拖拽光标
        self.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self, event):
        """鼠标按下事件：记录拖拽起始位置"""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        """鼠标移动事件：处理拖拽逻辑"""
        if not (event.buttons() & Qt.LeftButton):
            return
            
        # 检查拖拽距离是否超过阈值
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
            
        self._start_drag()

    def _start_drag(self):
        """启动拖拽操作"""
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.text())
        drag.setMimeData(mime_data)
        
        # 创建拖拽预览图像
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setOpacity(0.7)
        self.render(painter)
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(self.drag_start_position)
        
        drag.exec_(Qt.MoveAction)


class SeatWidget(CardWidget):
    """座位控件
    
    用于显示座位状态，支持接收拖拽的学生信息和自身拖拽
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_occupied = False  # 座位是否被占用
        self.student_name = ""    # 座位上的学生姓名
        self._init_ui()

    def _init_ui(self):
        """初始化UI样式和布局"""
        self.setFixedSize(90, 70)
        self._update_style(occupied=False)
        
        self.layout = QVBoxLayout(self)
        self.label = QLabel("空座位", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #757575; font-size: 14px;")
        self.layout.addWidget(self.label)
        
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        
        # 启用悬停效果
        self.setCursor(Qt.PointingHandCursor)

    def _update_style(self, occupied):
        """更新座位样式"""
        if occupied:
            self.setStyleSheet("""
                SeatWidget {
                    background-color: #e3f2fd;
                    border: 1px solid #90caf9;
                    border-radius: 8px;
                    margin: 2px;
                    padding: 0px;
                }
            """)
        else:
            self.setStyleSheet("""
                SeatWidget {
                    background-color: #f5f5f5;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    margin: 2px;
                    padding: 0px;
                }
                SeatWidget:hover {
                    background-color: #e3f2fd;
                    border: 1px solid #90caf9;
                }
            """)

    def mousePressEvent(self, event):
        """鼠标按下事件：记录拖拽起始位置（仅当座位被占用时）"""
        if event.button() == Qt.LeftButton and self.is_occupied:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        """鼠标移动事件：处理已占用座位的拖拽逻辑"""
        if not (event.buttons() & Qt.LeftButton) or not self.is_occupied:
            return
            
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
            
        self._start_drag()

    def _start_drag(self):
        """启动拖拽操作"""
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.student_name)
        drag.setMimeData(mime_data)
        
        # 创建拖拽预览图像
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setOpacity(0.7)
        self.render(painter)
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(self.drag_start_position)
        
        # 拖拽完成后清空座位
        if drag.exec_(Qt.MoveAction) == Qt.MoveAction:
            self.clear_seat()

    def clear_seat(self):
        """清空座位信息"""
        self.label.setText("空座位")
        self.label.setStyleSheet("color: #757575;")
        self._update_style(occupied=False)
        self.is_occupied = False
        self.student_name = ""

    def dragEnterEvent(self, event):
        """拖拽进入事件：检查是否可接受拖拽数据"""
        if (event.mimeData().hasText() or 
            event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist")) and not self.is_occupied:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """放置事件：处理学生信息放置逻辑"""
        if self.is_occupied:
            event.ignore()
            if hasattr(self.window(), 'show_status_message'):
                self.window().show_status_message("该座位已被占用，无法放置")
            return
            
        student_name = self._get_student_name_from_mime(event.mimeData())
        
        # 更新座位显示
        self.label.setText(student_name)
        self.label.setStyleSheet("color: #1976d2; font-weight: bold;")
        self._update_style(occupied=True)
        self.is_occupied = True
        self.student_name = student_name
        
        # 从学生列表移除已放置的学生
        if hasattr(self.window(), 'remove_student_from_list'):
            self.window().remove_student_from_list(student_name)
            
        event.acceptProposedAction()

    def _get_student_name_from_mime(self, mime_data):
        """从MIME数据中提取学生姓名"""
        if mime_data.hasText():
            return mime_data.text()
            
        if mime_data.hasFormat("application/x-qabstractitemmodeldatalist"):
            item_data = mime_data.data("application/x-qabstractitemmodeldatalist")
            stream = QDataStream(item_data, QIODevice.ReadOnly)
            
            while not stream.atEnd():
                row = stream.readInt32()
                col = stream.readInt32()
                map_items = stream.readInt32()
                
                for _ in range(map_items):
                    role = stream.readInt32()
                    value = QVariant()
                    stream >> value
                    if role == 0:  # Qt.DisplayRole
                        return str(value.value() if hasattr(value, 'value') else value)
        
        return "未知学生"


class SettingsPanel(QWidget):
    """设置面板部件
    
    用于配置座位布局的行数和列数
    """
    def __init__(self, parent=None, layout_config=None, column_names=None):
        super().__init__(parent)
        
        # 设置布局配置和列名
        self.layout_config = layout_config or {
            "column1": {"rows": 8, "cols": 3, "row_height": 60, "col_width": 80},
            "column2": {"rows": 8, "cols": 3, "row_height": 60, "col_width": 80},
            "column3": {"rows": 8, "cols": 3, "row_height": 60, "col_width": 80}
        }
        
        self.column_names = column_names or {
            "column1": "南",
            "column2": "中",
            "column3": "北"
        }
        
        # 存储输入控件引用
        self.column_rows_inputs = {}
        self.column_cols_inputs = {}
        
        # 初始化UI
        self._init_ui()
    
    def _init_ui(self):
        """初始化设置面板UI - 使用qfluentwidgets组件优化界面美观性"""
        
        # 使用qfluentwidgets的主题色
        self.setStyleSheet("background-color: white;")
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 设置最小尺寸
        self.setMinimumSize(550, 350)
        
        # 添加标题 - 使用qfluentwidgets的TitleLabel
        title = TitleLabel("座位布局设置", self)
        title.show()
        main_layout.addWidget(title)
        
        # 添加说明文字 - 使用qfluentwidgets的BodyLabel
        description = BodyLabel("请设置每列的行数和列数：", self)
        description.show()
        main_layout.addWidget(description)
        
        # 创建设置项容器 - 使用qfluentwidgets的CardWidget
        settings_container = CardWidget(self)
        settings_container.show()
        settings_layout = QVBoxLayout(settings_container)
        settings_layout.setSpacing(10)
        settings_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(settings_container)
        
        # 为每个列添加行数和列数设置
        for col_key, col_name in self.column_names.items():
            # 创建一行设置
            row_widget = CardWidget(settings_container)
            row_widget.show()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setSpacing(15)
            row_layout.setContentsMargins(10, 10, 10, 10)
            
            # 列名
            col_label = SubtitleLabel(f"{col_name}列:", row_widget)
            col_label.setFixedWidth(80)
            col_label.show()
            row_layout.addWidget(col_label)
            
            # 行数设置
            rows_group = QWidget(row_widget)
            rows_group.show()
            rows_layout = QVBoxLayout(rows_group)
            rows_layout.setContentsMargins(0, 0, 0, 0)
            
            rows_label = BodyLabel("行数", rows_group)
            rows_label.show()
            rows_layout.addWidget(rows_label)
            
            rows_spinbox = SpinBox(rows_group)
            rows_spinbox.setRange(1, 20)
            rows_spinbox.setValue(self.layout_config[col_key]["rows"])
            rows_spinbox.setFixedWidth(80)
            rows_spinbox.setStyleSheet("QSpinBox { background-color: white; border: 1px solid #d0d0d0; border-radius: 4px; padding: 4px; }")
            rows_spinbox.show()
            rows_layout.addWidget(rows_spinbox)
            
            self.column_rows_inputs[col_key] = rows_spinbox
            row_layout.addWidget(rows_group)
            
            # 列数设置
            cols_group = QWidget(row_widget)
            cols_group.show()
            cols_layout = QVBoxLayout(cols_group)
            cols_layout.setContentsMargins(0, 0, 0, 0)
            
            cols_label = BodyLabel("列数", cols_group)
            cols_label.show()
            cols_layout.addWidget(cols_label)
            
            cols_spinbox = SpinBox(cols_group)
            cols_spinbox.setRange(1, 10)
            cols_spinbox.setValue(self.layout_config[col_key]["cols"])
            cols_spinbox.setFixedWidth(80)
            cols_spinbox.setStyleSheet("QSpinBox { background-color: white; border: 1px solid #d0d0d0; border-radius: 4px; padding: 4px; }")
            cols_spinbox.show()
            cols_layout.addWidget(cols_spinbox)
            
            self.column_cols_inputs[col_key] = cols_spinbox
            row_layout.addWidget(cols_group)
            
            row_layout.addStretch(1)
            settings_layout.addWidget(row_widget)
        
        # 添加按钮
        buttons_widget = QWidget(self)
        buttons_widget.show()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.addStretch(1)
        
        # 使用qfluentwidgets的PushButton
        cancel_button = PushButton("取消", buttons_widget)
        cancel_button.setMinimumWidth(80)
        cancel_button.clicked.connect(self.close_parent_dialog)
        cancel_button.show()
        buttons_layout.addWidget(cancel_button)
        
        # 使用qfluentwidgets的PrimaryPushButton
        apply_button = PrimaryPushButton("应用设置", buttons_widget)
        apply_button.setMinimumWidth(100)
        apply_button.clicked.connect(self.apply_settings)
        apply_button.show()
        buttons_layout.addWidget(apply_button)
        
        main_layout.addWidget(buttons_widget)
        
        # 强制显示所有控件
        self.show()
        for child in self.findChildren(QWidget):
            child.show()
    
    def close_parent_dialog(self):
        """安全关闭父对话框"""
        if self.parent():
            try:
                self.parent().reject()
            except Exception as e:
                pass  # 静默处理错误
    
    def apply_settings(self):
        """应用设置并关闭对话框"""
        # 创建新的布局配置
        custom_layout_config = {}
        
        # 从输入框获取每列的行数和列数
        for col_key in self.column_names.keys():
            rows = self.column_rows_inputs[col_key].value()
            cols = self.column_cols_inputs[col_key].value()
            
            # 保留原有的行高和列宽设置
            custom_layout_config[col_key] = {
                "rows": rows,
                "cols": cols,
                "row_height": self.layout_config[col_key]["row_height"],
                "col_width": self.layout_config[col_key]["col_width"]
            }
        
        # 保存设置，准备在对话框关闭后应用
        self.custom_layout_config = custom_layout_config
        
        # 设置对话框结果并关闭
        if self.parent():
            try:
                # 设置对话框结果为接受
                self.parent().accept()
            except Exception as e:
                # 如果设置结果失败，尝试直接关闭
                self.close_parent_dialog()