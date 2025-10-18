from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    SubtitleLabel,
    PushButton,
    FluentIcon as FIF,
    PrimaryPushButton,
    InfoBar,
    InfoBarPosition,
    SpinBox
)

class SettingsPanel(QWidget):
    """设置面板部件
    
    用于配置座位布局的行数和列数
    """
    # 定义配置更新信号，携带布局配置数据
    settings_updated = pyqtSignal(dict)
    
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
        
        # 在FluentWindow结构中，控件会自动显示，不需要强制显示
    
    def close_parent_dialog(self):
        """关闭父窗口（在FluentWindow结构中不再需要）"""
        # 在FluentWindow结构中，我们不再需要关闭整个对话框
        # 而是直接应用设置并保持界面打开
        pass
    
    def apply_settings(self):
        """应用设置并实时更新界面"""
        try:
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
            
            # 保存设置到实例变量
            self.custom_layout_config = custom_layout_config
            
            # 首先发送信号通知主界面更新座位布局
            self.settings_updated.emit(custom_layout_config)
            
            # 直接保存配置到文件（不依赖parent的属性）
            import json
            import os
            config_file = "config.json"
            
            # 如果文件存在，先读取现有内容
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            else:
                # 如果文件不存在，创建默认配置
                config_data = {
                    "layout_config": custom_layout_config,
                    "column_names": self.column_names,
                    "window": {
                        "title": "教室座位安排系统",
                        "max_width": 1200,
                        "max_height": 800,
                        "min_width": 900,
                        "min_height": 700,
                        "size_percentage": 0.85
                    },
                    "theme": "LIGHT",
                    "styles": {
                        "main_window": "background-color: #f5f7fa;"
                    }
                }
            
            # 更新布局配置
            config_data["layout_config"] = custom_layout_config
            
            # 写入文件，确保正确处理中文字符
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            
            print(f"配置已保存到 {config_file}")
            
            InfoBar.success(
                title="成功",
                content="座位布局已更新并保存",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
        except Exception as e:
            print(f"保存配置出错: {str(e)}")
            InfoBar.error(
                title="错误",
                content=f"应用设置时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )