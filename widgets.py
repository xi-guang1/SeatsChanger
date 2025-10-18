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
    CardWidget,
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


# SettingsPanel类已移至settings.py文件中，避免重复定义