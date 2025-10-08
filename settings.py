from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    SubtitleLabel,
    PushButton,
    FluentWindow,
    FluentIcon as FIF,
    PrimaryPushButton,
    InfoBar,
    InfoBarPosition,
    SpinBox
)

class SettingsDialog(FluentWindow):
    """设置对话框
    
    用于配置应用程序的各种设置，包括座位布局
    """
    def __init__(self, parent=None, layout_config=None, column_names=None):
        """初始化设置对话框
        
        Args:
            parent: 父窗口
            layout_config: 当前布局配置
            column_names: 列名称配置
        """
        super().__init__(parent)
        
        # self.setWindowTitle("设置")
        # self.resize(650, 450)  # 稍微增加对话框大小
        # self.setMinimumSize(600, 400)  # 设置最小尺寸
        
        self.mainSetting = SettingsPanel(
            self, 
            layout_config=layout_config, 
            column_names=column_names,
            obj_name="mainSetting"
        )
        self.themeSetting = SettingsPanel(
            self, 
            layout_config=layout_config, 
            column_names=column_names,
            obj_name="themeSetting"
        )

        # # 存储设置面板引用
        # self.settings_panel = SettingsPanel(
        #     self, 
        #     layout_config=layout_config, 
        #     column_names=column_names
        # )
        
        # # 设置对话框布局
        # layout = QVBoxLayout(self)
        # layout.addWidget(self.settings_panel)
        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.mainSetting, FIF.HOME, 'Home')
        self.addSubInterface(self.themeSetting, FIF.MUSIC, 'Music library')
        # self.addSubInterface(self.videoInterface, FIF.VIDEO, 'Video library')

        # self.navigationInterface.addSeparator()

        # self.addSubInterface(self.albumInterface, FIF.ALBUM, 'Albums', NavigationItemPosition.SCROLL)
        # self.addSubInterface(self.albumInterface1, FIF.ALBUM, 'Album 1', parent=self.albumInterface)

        # self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(900, 700)
        # self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('Setting')

class SettingsPanel(QWidget):
    """设置面板部件
    
    用于配置座位布局的行数和列数
    """
    def __init__(self, parent=None, layout_config=None, column_names=None, obj_name=""):
        super().__init__(parent)
        
        self.setObjectName(obj_name)

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
            rows_spinbox.setFixedWidth(120)
            rows_spinbox.setFixedHeight(30)
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
            cols_spinbox.setFixedWidth(120)
            cols_spinbox.setFixedHeight(30)
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
        
        try:
            # 在对话框关闭后，在主UI线程中应用设置
            self.parent().setup_seating_chart(dialog.settings_panel.custom_layout_config)
            # 更新配置文件中的布局配置
            self.parent().config["layout_config"] = dialog.settings_panel.custom_layout_config
            self.parent().config_manager.update_config(self.config)
            更新状态消息
            InfoBar.success(
        title="成功",
        content="座位布局已更新",
        orient=Qt.Horizontal,
        isClosable=True,
        position=InfoBarPosition.TOP_RIGHT,
        duration=2000,
        parent=self
    )
        except Exception as e:
            InfoBar.error(
        title="错误",
        content=f"应用设置时出错: {str(e)}",
        orient=Qt.Horizontal,
        isClosable=True,
        position=InfoBarPosition.TOP_RIGHT,
        duration=3000,
        parent=self
    )