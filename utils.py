import csv
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox

# 确保日志文件夹存在
log_dir = 'log'
os.makedirs(log_dir, exist_ok=True)

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, f'seats_changer_{datetime.now().strftime("%Y%m%d")}.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 创建不同模块的logger
main_logger = logging.getLogger('main')
config_logger = logging.getLogger('config')
ui_logger = logging.getLogger('ui')
layout_logger = logging.getLogger('layout')
file_logger = logging.getLogger('file')

class LogManager:
    """日志管理器
    
    提供统一的日志记录接口
    """
    
    @staticmethod
    def get_logger(module_name='main'):
        """获取指定模块的logger
        
        Args:
            module_name: 模块名称
            
        Returns:
            logging.Logger: logger实例
        """
        return logging.getLogger(module_name)
    
    @staticmethod
    def debug(logger, message):
        """记录调试信息
        
        Args:
            logger: logger实例
            message: 调试信息
        """
        logger.debug(message)
    
    @staticmethod
    def info(logger, message):
        """记录信息
        
        Args:
            logger: logger实例
            message: 信息内容
        """
        logger.info(message)
    
    @staticmethod
    def warning(logger, message):
        """记录警告
        
        Args:
            logger: logger实例
            message: 警告信息
        """
        logger.warning(message)
    
    @staticmethod
    def error(logger, message):
        """记录错误
        
        Args:
            logger: logger实例
            message: 错误信息
        """
        logger.error(message)
    
    @staticmethod
    def exception(logger, message, exc_info=True):
        """记录异常
        
        Args:
            logger: logger实例
            message: 异常信息
            exc_info: 是否包含异常堆栈
        """
        logger.exception(message, exc_info=exc_info)

class CSVManager:
    """CSV文件管理器
    
    负责导入和导出CSV文件
    """
    @staticmethod
    def import_from_csv(parent=None):
        """从CSV文件导入学生名单
        
        Args:
            parent: 父窗口，用于显示对话框
        
        Returns:
            list: 学生名单列表
        """
        file_path, _ = QFileDialog.getOpenFileName(
            parent, "选择CSV文件", "", "CSV文件 (*.csv);;所有文件 (*)"
        )
        
        if not file_path:
            return []
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                new_students = []
                for row in reader:
                    if row:  # 跳过空行
                        student_name = row[0].strip()
                        if student_name and student_name not in new_students:
                            new_students.append(student_name)
                
                return new_students
                
        except Exception as e:
            error_message = f"导入CSV文件时出错: {str(e)}"
            if parent:
                QMessageBox.critical(parent, "错误", error_message)
            else:
                print(error_message)
            return []

    @staticmethod
    def validate_file_path(file_path, ext=None):
        """验证文件路径是否有效
        
        Args:
            file_path: 文件路径
            ext: 期望的文件扩展名
        
        Returns:
            bool: 文件路径是否有效
        """
        if not file_path:
            return False
            
        if ext:
            _, file_ext = os.path.splitext(file_path)
            if file_ext.lower() != ext.lower():
                return False
                
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except:
                return False
                
        return True

class UIUtils:
    """UI工具类
    
    包含一些UI相关的通用函数
    """
    @staticmethod
    def show_error_message(parent, title, message):
        """显示错误消息对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            message: 错误消息
        """
        QMessageBox.critical(parent, title, message)

    @staticmethod
    def show_warning_message(parent, title, message):
        """显示警告消息对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            message: 警告消息
        """
        QMessageBox.warning(parent, title, message)

    @staticmethod
    def show_info_message(parent, title, message):
        """显示信息消息对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            message: 信息消息
        """
        QMessageBox.information(parent, title, message)

    @staticmethod
    def ask_confirmation(parent, title, message):
        """显示确认对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            message: 确认消息
        
        Returns:
            bool: 用户是否确认
        """
        reply = QMessageBox.question(parent, title, message, 
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes