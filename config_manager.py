import json
import os

class ConfigManager:
    """配置管理器
    
    负责加载、保存和管理应用程序的配置数据
    """
    # 默认配置定义
    DEFAULT_CONFIG = {
        "layout_config": {
            "column1": {"rows": 8, "cols": 3, "row_height": 60, "col_width": 80},
            "column2": {"rows": 8, "cols": 3, "row_height": 60, "col_width": 80},
            "column3": {"rows": 8, "cols": 3, "row_height": 60, "col_width": 80}
        },
        "column_names": {
            "column1": "南",
            "column2": "中",
            "column3": "北"
        },
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

    def __init__(self, config_file="config.json"):
        """初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self):
        """加载配置文件
        
        Returns:
            dict: 配置数据
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置和文件配置，确保所有必要的字段都存在
                    for key, value in self.DEFAULT_CONFIG.items():
                        if key not in config:
                            config[key] = value
                        elif isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if sub_key not in config[key]:
                                    config[key][sub_key] = sub_value
                    return config
            else:
                # 如果配置文件不存在，创建默认配置文件
                self.save_config(self.DEFAULT_CONFIG)
                return self.DEFAULT_CONFIG
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            # 加载失败时返回默认配置
            return self.DEFAULT_CONFIG
            
    def save_config(self, config):
        """保存配置文件
        
        Args:
            config: 要保存的配置数据
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")

    def get_config(self):
        """获取当前配置
        
        Returns:
            dict: 当前配置数据
        """
        return self.config

    def update_config(self, new_config):
        """更新配置并保存
        
        Args:
            new_config: 新的配置数据
        """
        self.config = new_config
        self.save_config(new_config)

    def get_layout_config(self):
        """获取布局配置
        
        Returns:
            dict: 布局配置数据
        """
        return self.config.get("layout_config", self.DEFAULT_CONFIG["layout_config"])

    def update_layout_config(self, new_layout_config):
        """更新布局配置
        
        Args:
            new_layout_config: 新的布局配置数据
        """
        self.config["layout_config"] = new_layout_config
        self.save_config(self.config)