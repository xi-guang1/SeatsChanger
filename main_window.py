from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    FluentWindow,
    FluentIcon as FIF,
    InfoBar,
    InfoBarPosition,
    LineEdit,
    PrimaryPushButton,
    PushButton,
    TitleLabel,
    Theme,
    setTheme,
)

# 导入自定义模块
from config_manager import ConfigManager
from widgets import DraggableLabel, SeatWidget
from settings import SettingsPanel
from export_manager import ExportManager
from utils import CSVManager

class MWindow(FluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.seatingChartWindow = SeatingChartWindow(
            self, 
            obj_name="seatingChartWindow"
        )
        self.Setting = SettingsPanel(
            self, 
            obj_name="Setting"
        )

        # self.Setting.buttons_widget.buttons_layout.apply_button.clicked.connect(self.reloadSetting)

        # 初始化配置管理器
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        self.current_layout_config = self.config["layout_config"].copy()  # 当前布局配置

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.seatingChartWindow, FIF.HOME, 'Home')
        self.addSubInterface(self.Setting, FIF.SETTING, 'Setting')

    def initWindow(self):
        """初始化窗口基本属性"""
        # 从配置文件设置窗口标题
        self.setWindowTitle(self.config["window"]["title"])
        
        # 获取屏幕可用尺寸并设置合理的窗口大小
        screen = QApplication.desktop().availableGeometry()
        size_percentage = self.config["window"]["size_percentage"]
        max_width = self.config["window"]["max_width"]
        max_height = self.config["window"]["max_height"]
        
        width = min(max_width, int(screen.width() * size_percentage))
        height = min(max_height, int(screen.height() * size_percentage))
        self.resize(width, height)
        
        # 设置窗口最小尺寸，确保UI组件不会被过度压缩
        self.setMinimumSize(self.config["window"]["min_width"], self.config["window"]["min_height"])
        
        # 设置主题和样式
        theme = Theme.LIGHT if self.config["theme"] == "LIGHT" else Theme.DARK
        setTheme(theme)  # 设置Fluent主题
        
        # 设置窗口样式
        self.setStyleSheet(self.config["styles"]["main_window"])

    def reloadSetting():
        pass

class SeatingChartWindow(QWidget):
    """教室座位安排系统主窗口"""
    def __init__(self,parent=None,obj_name="seatingChartWindow"):
        super().__init__(parent)
        self.setObjectName(obj_name)
        self.students = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十"]
        self.columns = {}  # 存储座位列数据
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        self.current_layout_config = self.config["layout_config"].copy()  # 当前布局配置
        
        # 初始化导出管理器
        self.export_manager = ExportManager(self)

        # self._init_window()
        self._init_ui()
        self._refresh_ui()
        

    def _init_ui(self):
        """初始化用户界面"""
        self.layout = QVBoxLayout(self)
        
        self._setup_control_panel()
        self._setup_seating_area()
        self._setup_student_list_area()

    def _setup_control_panel(self):
        """设置控制面板"""
        # 创建控制面板卡片
        control_card = CardWidget()
        control_card.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
        """)
        
        # 主控制面板
        control_layout = QHBoxLayout(control_card)
        control_layout.setSpacing(16)
        control_layout.setContentsMargins(20, 16, 20, 16)
        
        # 学生输入区域
        input_group = QWidget()
        input_layout = QHBoxLayout(input_group)
        input_layout.setSpacing(8)
        
        # 学生输入框
        self.add_student_edit = LineEdit()
        self.add_student_edit.setFixedWidth(200)
        self.add_student_edit.setPlaceholderText("输入学生姓名")
        self.add_student_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2196f3;
                outline: none;
            }
        """)
        
        input_layout.addWidget(self.add_student_edit)
        
        # 按钮
        self.add_student_button = PrimaryPushButton(
            "添加学生", icon=QIcon(FIF.ADD.path()))
        self.add_student_button.clicked.connect(self.add_student)
        self.add_student_button.setFixedHeight(36)
        
        self.import_csv_button = PushButton(
            "导入CSV", icon=QIcon(FIF.DOCUMENT.path()))
        self.import_csv_button.clicked.connect(self.import_from_csv)
        self.import_csv_button.setFixedHeight(36)
        
        self.export_as_image_button = PushButton(
            "导出为图片", icon=QIcon(FIF.SAVE.path()))
        self.export_as_image_button.clicked.connect(self.export_manager.export_as_image)
        self.export_as_image_button.setFixedHeight(36)
        
        # 添加导出为PDF按钮（适合打印分享）
        self.export_pdf_button = PushButton(
            "导出为PDF", icon=QIcon(FIF.DOCUMENT.path()))
        self.export_pdf_button.clicked.connect(self.export_manager.export_for_printing)
        self.export_pdf_button.setFixedHeight(36)
        
        # 组装主控制面板
        control_layout.addWidget(input_group)
        control_layout.addWidget(self.add_student_button)
        control_layout.addWidget(self.import_csv_button)
        control_layout.addWidget(self.export_as_image_button)
        control_layout.addWidget(self.export_pdf_button)
        
        self.layout.addWidget(control_card)

    def _setup_seating_area(self):
        """设置座位显示区域"""
        # 创建座位图表容器
        seating_container = QWidget()
        seating_container.setStyleSheet("background-color: transparent; padding: 20px; margin: 0px;")
        
        # 创建座位卡片
        seating_card = CardWidget()
        seating_card.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
        """)
        
        self.seating_chart_layout = QHBoxLayout(seating_card)
        self.seating_chart_layout.setSpacing(30)  # 设置列与列之间有适当间距
        self.seating_chart_layout.setContentsMargins(40, 30, 40, 30)  # 设置适当内边距
        
        # 将座位卡片添加到容器
        container_layout = QVBoxLayout(seating_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(seating_card)
        
        self.layout.addWidget(seating_container)
        
        # 添加讲台
        self._add_teacher_desk()
        
    def _add_teacher_desk(self):
        """添加讲台组件"""
        # 创建讲台容器
        desk_container = QWidget()
        desk_container.setStyleSheet("background-color: transparent; padding: 20px;")
        
        # 创建讲台布局
        desk_layout = QHBoxLayout(desk_container)
        desk_layout.setAlignment(Qt.AlignCenter)
        desk_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建讲台控件
        teacher_desk = QWidget()
        teacher_desk.setFixedSize(240, 90)  # 适当增大讲台尺寸
        teacher_desk.setStyleSheet("""
            QWidget {
                background-color: #e0f2f1;
                border: 2px solid #26a69a;
                border-radius: 8px;
            }
        """)
        
        # 添加讲台标签
        desk_label = QLabel("讲 台")
        desk_label.setAlignment(Qt.AlignCenter)
        desk_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #00796b;")
        desk_inner_layout = QVBoxLayout(teacher_desk)
        desk_inner_layout.addWidget(desk_label)
        
        # 添加讲台到布局
        desk_layout.addWidget(teacher_desk)
        
        # 添加到主布局
        self.layout.addWidget(desk_container)

    def _setup_student_list_area(self):
        """设置学生列表区域（水平滚动）"""
        # 创建学生列表卡片
        student_list_card = CardWidget()
        student_list_card.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
        """)
        
        # 学生列表布局
        student_list_layout = QVBoxLayout(student_list_card)
        student_list_layout.setSpacing(12)
        student_list_layout.setContentsMargins(20, 16, 20, 16)
        
        # 添加标题
        title_label = BodyLabel("学生列表 (拖拽到座位)")
        title_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #424242;")
        student_list_layout.addWidget(title_label)
        
        # 水平滚动区域
        student_scroll_area = QScrollArea()
        student_scroll_area.setFixedHeight(70)
        student_scroll_area.setWidgetResizable(True)
        student_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        student_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        student_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #fafafa;
            }
            QScrollBar:horizontal {
                height: 8px;
                background: transparent;
                margin: 3px 20px 3px 20px;
            }
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #90caf9;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                height: 0px;
                width: 0px;
            }
        """)
        
        # 学生列表容器
        self.student_container = QWidget()
        self.student_container.setStyleSheet("background-color: transparent;")
        self.student_layout = QHBoxLayout(self.student_container)
        self.student_layout.setSpacing(8)
        self.student_layout.setContentsMargins(10, 8, 10, 8)
        self.student_layout.setAlignment(Qt.AlignLeft)
        
        student_scroll_area.setWidget(self.student_container)
        student_list_layout.addWidget(student_scroll_area)
        
        # 将学生列表卡片添加到主布局
        self.layout.addWidget(student_list_card)

    def _refresh_ui(self):
        """刷新整个UI界面"""
        self.refresh_student_list()
        self.setup_seating_chart(self.config["layout_config"])
        InfoBar.success(
            title="成功",
            content="就绪",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )

    def refresh_student_list(self):
        """刷新学生列表显示"""
        # 清除现有学生标签
        for i in reversed(range(self.student_layout.count())):
            widget = self.student_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 添加所有学生标签
        for student in self.students:
            label = DraggableLabel(student)
            self.student_layout.addWidget(label)
        
        self.student_container.adjustSize()

    def remove_student_from_list(self, student_name):
        """从学生列表中移除指定学生"""
        if student_name in self.students:
            self.students.remove(student_name)
            self.refresh_student_list()
            InfoBar.success(
            title="成功",
            content=f"已安排学生 {student_name} 到座位",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )

    def setup_seating_chart(self, layout_config=None):
        """设置座位图表布局"""
        if layout_config is None:
            layout_config = self.config_manager.DEFAULT_CONFIG["layout_config"]
        
        # 保存当前布局配置
        self.current_layout_config = layout_config.copy()
        
        # 清空现有座位
        for i in reversed(range(self.seating_chart_layout.count())):
            widget = self.seating_chart_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 创建三大列座位
        for col_key in ["column1", "column2", "column3"]:
            self._create_seating_column(col_key, layout_config[col_key])
    

    def _create_seating_column(self, col_key, config):
        """创建单个列的座位布局"""
        column_widget = QWidget()
        column_widget.setStyleSheet("background-color: transparent;")
        column_layout = QVBoxLayout(column_widget)
        column_layout.setContentsMargins(0, 0, 0, 0)  # 设置列容器无内边距
        column_layout.setSpacing(15)  # 设置列内组件适当间距
        
        # 列标题
        col_title = BodyLabel(self.config["column_names"][col_key])
        col_title.setAlignment(Qt.AlignCenter)
        col_title.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #1976d2;
            padding: 8px 16px;
            background-color: #e3f2fd;
            border-radius: 6px;
            margin-bottom: 5px;
        """)
        # 固定标题高度，初始化后不再修改
        col_title.setFixedHeight(40)
        column_layout.addWidget(col_title)
        
        # 网格布局容器，添加背景
        grid_container = QWidget()
        grid_container.setStyleSheet("""
            background-color: #f5f5f5;
            border-radius: 8px;
            padding: 10px;
        """)
        
        # 网格布局
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(4)  # 设置座位之间的间距
        
        # 设置行列尺寸
        for row in range(config["rows"]):
            grid_layout.setRowMinimumHeight(row, config["row_height"])
        for col in range(config["cols"]):
            grid_layout.setColumnMinimumWidth(col, config["col_width"])
        
        # 添加座位控件
        self.columns[col_key] = []
        for row in range(config["rows"]):
            row_seats = []
            for col in range(config["cols"]):
                seat = SeatWidget()
                grid_layout.addWidget(seat, row, col)
                row_seats.append(seat)
            self.columns[col_key].append(row_seats)
        
        column_layout.addWidget(grid_container)
        self.seating_chart_layout.addWidget(column_widget)

    def add_student(self):
        """添加新学生到列表"""
        student_name = self.add_student_edit.text().strip()
        if not student_name:
            return
            
        if student_name in self.students:
            InfoBar.warning(
            title="警告",
            content="学生已存在",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )
            return
            
        self.students.append(student_name)
        self.refresh_student_list()
        self.add_student_edit.clear()
        InfoBar.success(
            title="成功",
            content=f"已添加学生: {student_name}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )

    def import_from_csv(self):
        """从CSV文件导入学生名单"""
        new_students = CSVManager.import_from_csv(self)
        
        if new_students:
            self.students = new_students
            self.refresh_student_list()
            InfoBar.success(
            title="成功",
            content=f"已从CSV文件导入 {len(new_students)} 名学生",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )
        elif not new_students:
            # 用户取消操作或文件为空的情况不显示警告
            pass
        else:
            # 这里处理的是已经在CSVManager中处理过的错误，无需额外处理
            pass

    def show_status_message(self, message):
        """显示状态栏消息"""
        InfoBar.info(
            title="信息",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )