import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QComboBox, QMessageBox, QFileDialog, QListWidget, QProgressBar, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PIL import Image
import os.path

class ImageConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图像格式转换")
        self.setGeometry(100, 100, 600, 400)
        
        self.setStyleSheet(open("style.qss", "r", encoding="utf-8").read())  # 加载样式表
        
        self.create_widgets()
        self.center_window()
        
        self.files_to_convert = []  # 存储待转换的文件列表
        
    def create_widgets(self):
        # 创建选择文件按钮
        self.select_button = QPushButton("选择文件")
        self.select_button.clicked.connect(self.select_files)
        
        # 创建选择文件夹按钮
        self.select_folder_button = QPushButton("选择文件夹")
        self.select_folder_button.clicked.connect(self.select_folder)
        
        # 创建文件格式选择框
        self.format_label = QLabel("选择格式:")
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["jpg", "png", "gif", "bmp", "ico"])  # 添加ICO选项
        
        # 创建导出路径选择按钮
        self.select_export_path_button = QPushButton("选择导出路径")
        self.select_export_path_button.clicked.connect(self.select_export_path)
        
        # 创建开始转换按钮
        self.convert_button = QPushButton("开始转换")
        self.convert_button.clicked.connect(self.start_conversion)
        
        # 创建打开输出目录文件夹按钮
        self.open_export_folder_button = QPushButton("打开导出目录")
        self.open_export_folder_button.clicked.connect(self.open_export_folder)

        # 创建转换进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        
        # 创建状态标签
        self.status_label = QLabel("")


        
        # 创建左侧布局
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.select_button)
        left_layout.addWidget(self.select_folder_button)
        left_layout.addWidget(self.format_label)
        left_layout.addWidget(self.format_combo)
        left_layout.addWidget(self.select_export_path_button)
        left_layout.addWidget(self.convert_button)
        left_layout.addWidget(self.progress_bar)
        left_layout.addWidget(self.status_label)
        left_layout.addWidget(self.open_export_folder_button)

        
        # 创建文件列表
        self.file_list = QListWidget()
        
        # 创建右侧布局
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.file_list)
        
        # 创建主布局
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        
        # 创建主部件并设置布局
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # 设置字体
        font = QFont("Arial", 12)
        self.select_button.setFont(font)
        self.select_folder_button.setFont(font)
        self.format_label.setFont(font)
        self.format_combo.setFont(font)
        self.select_export_path_button.setFont(font)
        self.convert_button.setFont(font)
        self.status_label.setFont(font)
        
        # 设置对齐方式
        self.format_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
    def center_window(self):
        # 居中窗口
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        window_size = self.geometry()
        x = (screen_size.width() - window_size.width()) // 2
        y = (screen_size.height() - window_size.height()) // 2
        self.move(x, y)
        
    def select_files(self):
        # 打开选择文件对话框
        file_paths, _ = QFileDialog.getOpenFileNames(self, "选择文件")
        
        # 检查是否选择了文件
        if file_paths:
            self.files_to_convert = file_paths
            self.update_file_list()
    
    def select_folder(self):
        # 打开选择文件夹对话框
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        
        # 检查是否选择了文件夹
        if folder_path:
            self.files_to_convert = self.get_image_files_in_folder(folder_path)
            self.update_file_list()
    
    def update_file_list(self):
        # 清空文件列表
        self.file_list.clear()
        
        # 添加文件到列表
        for file_path in self.files_to_convert:
            self.file_list.addItem(file_path)
        
    def get_image_files_in_folder(self, folder_path):
        # 获取文件夹中的所有图像文件
        file_list = os.listdir(folder_path)
        image_files = []
        
        for file_name in file_list:
            file_path = os.path.join(folder_path, file_name)
            
            if os.path.isfile(file_path) and self.is_image_file(file_path):
                image_files.append(file_path)
        
        return image_files
    
    def is_image_file(self, file_path):
        # 检查文件是否是图像文件
        valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.raw', '.bmp', '.ico']
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in valid_extensions
    
    def select_export_path(self):
        # 导出路径选择逻辑
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        if file_dialog.exec_():
            selected_directory = file_dialog.selectedFiles()
            self.export_path = selected_directory[0]
            self.status_label.setText(f"导出路径：{self.export_path}")
    def get_file_format(self, file_path):
        _, extension = os.path.splitext(file_path)
        return extension[1:].lower()

    def start_conversion(self):
        if not hasattr(self, 'export_path'):
            QMessageBox.warning(self, "警告", "请选择导出路径！")
            return

    # 获取用户选择的格式
        selected_format = self.format_combo.currentText()

    # 检查用户选择的格式是否与原始格式相同
        if self.files_to_convert:
            original_format = self.get_file_format(self.files_to_convert[0])
            if original_format == selected_format:
                QMessageBox.warning(self, "警告", "无法将文件转换为与原始格式相同的格式！")
                return

    # 启动转换线程
        self.conversion_thread = ConversionThread(self.files_to_convert, selected_format, self.export_path)
        self.conversion_thread.progress_updated.connect(self.update_progress)
        self.conversion_thread.finished.connect(self.conversion_finished)
        self.conversion_thread.conversion_failed.connect(self.conversion_failed)
        self.conversion_thread.start()

        # 禁用按钮防止重复点击
        self.select_button.setEnabled(False)
        self.select_folder_button.setEnabled(False)
        self.select_export_path_button.setEnabled(False)
        self.convert_button.setEnabled(False)
        
    def update_progress(self, value):
        # 更新转换进度条
        self.progress_bar.setValue(value)
        
    def conversion_finished(self):
        # 转换完成后的清理工作
        self.status_label.setText("转换完成！")
        
        # 恢复按钮状态
        self.select_button.setEnabled(True)
        self.select_folder_button.setEnabled(True)
        self.select_export_path_button.setEnabled(True)
        self.convert_button.setEnabled(True)
    def open_export_folder(self):
        if hasattr(self, 'export_path'):
            os.startfile(self.export_path)
        else:
            QMessageBox.warning(self, "警告", "导出路径未设置！")

    def conversion_failed(self, error_message):
        QMessageBox.warning(self, "转换失败", error_message)

    
class ConversionThread(QThread):
    progress_updated = pyqtSignal(int)
    conversion_failed = pyqtSignal(str)


    def __init__(self, files_to_convert, output_format, export_path):
        super().__init__()
        self.files_to_convert = files_to_convert
        self.output_format = output_format
        self.export_path = export_path
        
    def run(self):
        total_files = len(self.files_to_convert)
        converted_files = 0
        if self.files_to_convert:
            file_path = self.files_to_convert[0]
            _, extension = os.path.splitext(file_path)
            original_format = extension[1:].lower()
            if original_format == self.output_format:
                error_message = "无法将文件转换为与原始格式相同的格式！"
                self.conversion_failed.emit(error_message)
                return


        
        for file_path in self.files_to_convert:
            try:
                # 打开图像文件
                image = Image.open(file_path)
                
                # 构造输出文件路径
                output_path = self.get_output_path(file_path)
                
                # 转换并保存图像文件
                image.save(output_path, format=self.output_format)
                
                converted_files += 1
                progress = int(converted_files / total_files * 100)
                self.progress_updated.emit(progress)
            except Exception as e:
                print(f"转换失败: {str(e)}")
        
    def get_output_path(self, file_path):
        # 构造输出文件路径
        file_name = os.path.basename(file_path)
        file_name_without_extension = os.path.splitext(file_name)[0]
        output_name = file_name_without_extension + '.' + self.output_format
        
        if hasattr(self, 'export_path'):
            # 检查是否选择了导出路径
            output_path = os.path.join(self.export_path, output_name)
        else:
            # 使用原始文件所在目录作为输出路径
            output_path = os.path.join(os.path.dirname(file_path), output_name)
        
        return output_path
    def get_file_format(self, file_path):
        _, extension = os.path.splitext(file_path)
        return extension[1:].lower()

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    converter_app = ImageConverterApp()
    converter_app.show()
    sys.exit(app.exec_())
