import os
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtPrintSupport import QPrinter
from qfluentwidgets import InfoBar, InfoBarPosition

class ExportManager:
    """导出管理器
    
    负责将座位表导出为图片和PDF格式
    """
    def __init__(self, parent_window=None):
        """初始化导出管理器
        
        Args:
            parent_window: 父窗口引用，用于显示对话框和状态消息
        """
        self.parent_window = parent_window

    def export_as_image(self):
        """导出座位表为图片"""
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent_window, "保存图片", "座位安排.png", "PNG图片 (*.png);;JPEG图片 (*.jpg *.jpeg)"
        )
        
        if not file_path:
            return
            
        try:
            # 获取座位表区域截图
            seating_chart_widget = self.parent_window.seating_chart_layout.parent().parent()
            pixmap = seating_chart_widget.grab()
            pixmap.save(file_path)
            
            # 显示状态消息
            if self.parent_window:
                InfoBar.success(
                    title="成功",
                    content=f"已导出图片到: {file_path}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=2000,
                    parent=self.parent_window
                )
                
        except Exception as e:
            error_message = f"导出图片时出错: {str(e)}"
            QMessageBox.critical(self.parent_window, "错误", error_message)
            
    def export_for_printing(self):
        """导出座位表为适合打印的PDF格式"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent_window, "保存为PDF", "座位安排.pdf", "PDF文件 (*.pdf)"
            )
            
            if not file_path:
                return
            
            # 验证配置文件数据
            if not hasattr(self.parent_window, 'config') or not isinstance(self.parent_window.config, dict):
                raise ValueError("配置数据未正确加载")
            
            if "column_names" not in self.parent_window.config or "layout_config" not in self.parent_window.config:
                raise ValueError("配置文件缺少必要的键")
            
            # 创建一个适合打印的文档
            document = QTextDocument()
            
            # 构建完整的HTML内容字符串
            html_content = '''
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    * { box-sizing: border-box; }
                    body { font-family: SimHei, "Microsoft YaHei", Arial, sans-serif; margin: 0; padding: 10px; }
                    h1 { text-align: center; color: #333; margin-bottom: 15px; font-size: 20px; }
                    .teacher-desk { text-align: center; margin: 15px auto; padding: 10px; background-color: #e0f2f1; border: 2px solid #26a69a; width: 200px; font-weight: bold; font-size: 14px; }
                    
                    /* 布局容器 */
                    .main-container { width: 100%; page-break-inside: avoid; }
                    
                    /* 使用表格布局实现三列并排 */
                    .layout-table { display: table; width: 100%; table-layout: fixed; }
                    .layout-row { display: table-row; }
                    .layout-cell { display: table-cell; vertical-align: top; padding: 0 2px; }
                    
                    /* 标题样式 */
                    .column-title { 
                        text-align: center; 
                        font-weight: bold; 
                        font-size: 16px; 
                        padding: 6px; 
                        background-color: #f0f0f0; 
                        border: 1px solid #ddd; 
                        margin-bottom: 5px;
                    }
                    
                    /* 表格样式 */
                    table { 
                        width: 100%; 
                        border-collapse: collapse;
                        font-size: 11px;
                    }
                    th, td { 
                        border: 1px solid #000;
                        padding: 4px;
                        text-align: center;
                        word-wrap: break-word;
                    }
                    th { 
                        background-color: #f9f9f9;
                        font-weight: bold;
                        color: #333;
                    }
                    .empty-seat { background-color: #f9f9f9; color: #999; }
                    .occupied-seat { background-color: #fff; color: #333; }
                    
                    /* 统计信息 */
                    .print-date { 
                        text-align: right; 
                        margin-top: 20px;
                        font-style: italic;
                        color: #666;
                        font-size: 11px;
                    }
                </style>
            </head>
            <body>
                <h1>教室座位安排</h1>
                <div class="teacher-desk">讲 台</div>
                <div class="main-container">
            '''
            
            # 添加座位表内容
            col_keys = ["column1", "column2", "column3"]
            seat_count = 0
            occupied_count = 0
            
            # 准备列数据
            columns_html = {}
            column_titles = []
            
            for col_key in col_keys:
                # 安全地访问配置数据
                if col_key not in self.parent_window.config["column_names"] or col_key not in self.parent_window.config["layout_config"]:
                    print(f"警告：配置中缺少{col_key}的配置信息")
                    columns_html[col_key] = "<tr><td colspan='2'>无数据</td></tr>"
                    column_titles.append("")
                    continue
                
                col_name = self.parent_window.config["column_names"][col_key]
                col_config = self.parent_window.config["layout_config"][col_key]
                column_titles.append(col_name)
                
                # 生成表格HTML
                table_html = '<tr><th>座位</th><th>学生</th></tr>'
                
                try:
                    rows = col_config.get("rows", 0)
                    cols = col_config.get("cols", 0)
                    
                    if rows <= 0 or cols <= 0:
                        print(f"警告：{col_name}列的行列配置无效")
                        table_html += '<tr><td colspan="2">无座位数据</td></tr>'
                    else:
                        # 检查columns属性是否存在且有效
                        if not hasattr(self.parent_window, 'columns') or not isinstance(self.parent_window.columns, dict) or col_key not in self.parent_window.columns:
                            print(f"警告：缺少{col_name}列的座位数据")
                            # 生成默认的空座位数据
                            for row in range(rows):
                                for col in range(cols):
                                    seat_count += 1
                                    table_html += f'<tr class="empty-seat"><td>第{row+1}排第{col+1}列</td><td>空座位</td></tr>'
                        else:
                            for row in range(rows):
                                for col in range(cols):
                                    seat_index = row * cols + col
                                    seat_count += 1
                                    
                                    # 检查座位索引是否有效
                                    if seat_index < len(self.parent_window.columns[col_key]):
                                        seat = self.parent_window.columns[col_key][seat_index]
                                        
                                        # 检查座位对象是否有效
                                        if hasattr(seat, 'is_occupied') and seat.is_occupied and hasattr(seat, 'student_name'):
                                            student_name = seat.student_name
                                            occupied_count += 1
                                            table_html += f'<tr class="occupied-seat"><td>第{row+1}排第{col+1}列</td><td>{student_name}</td></tr>'
                                        else:
                                            table_html += f'<tr class="empty-seat"><td>第{row+1}排第{col+1}列</td><td>空座位</td></tr>'
                                    else:
                                        print(f"警告：{col_name}列的座位索引{seat_index}超出范围")
                                        table_html += f'<tr class="empty-seat"><td>第{row+1}排第{col+1}列</td><td>空座位</td></tr>'
                except Exception as inner_e:
                    print(f"处理座位数据时出错: {str(inner_e)}")
                    table_html += f'<tr><td colspan="2">数据处理错误</td></tr>'
                
                columns_html[col_key] = table_html
            
            # 添加标题行
            html_content += '<div class="layout-table">'
            html_content += '<div class="layout-row">'
            for title in column_titles:
                if title:
                    html_content += f'<div class="layout-cell"><div class="column-title">{title}</div></div>'
            html_content += '</div>'
            
            # 添加表格行
            html_content += '<div class="layout-row">'
            for col_key in col_keys:
                if column_titles[col_keys.index(col_key)]:
                    html_content += f'<div class="layout-cell"><table>{columns_html[col_key]}</table></div>'
            html_content += '</div>'
            html_content += '</div>'
            
            # 添加统计信息和日期
            current_date = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
            html_content += f'<div class="print-date">打印时间: {current_date}<br>总座位数: {seat_count}, 已占用: {occupied_count}, 空座位: {seat_count - occupied_count}</div>'
            
            # 关闭HTML
            html_content += '</div></body></html>'
            
            # 设置完整的HTML内容到文档
            document.setHtml(html_content)
            
            # 导出为PDF
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPrinter.A4)
            printer.setPageMargins(20, 20, 20, 20, QPrinter.Millimeter)
            
            # 安全地打印文档
            try:
                document.print_(printer)
                
                # 验证文件是否已创建
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    print(f"PDF文件已成功创建: {file_path}, 大小: {os.path.getsize(file_path)}字节")
                    if self.parent_window:
                        InfoBar.success(
                            title="成功",
                            content=f"已导出PDF到: {file_path}",
                            orient=Qt.Horizontal,
                            isClosable=True,
                            position=InfoBarPosition.TOP_RIGHT,
                            duration=2000,
                            parent=self.parent_window
                        )
                else:
                    raise IOError(f"PDF文件创建失败或为空: {file_path}")
            except Exception as print_error:
                print(f"打印文档时出错: {str(print_error)}")
                raise
            
        except Exception as e:
            import traceback
            error_info = traceback.format_exc()
            print(f"PDF导出错误详细信息:\n{error_info}")
            QMessageBox.critical(self.parent_window, "错误", f"导出PDF时出错: {str(e)}\n\n详细错误信息已打印到控制台")