"""Main window UI for file converter."""

import os
from pathlib import Path
from typing import List

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QProgressBar,
    QListWidget, QFileDialog, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent

from core.converter import batch_convert, ALL_FORMATS, IMAGE_FORMATS, ASTRO_FORMATS


class ConversionThread(QThread):
    """Thread for running conversions without freezing UI."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, files: List[str], output_dir: str, fmt: str):
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self.fmt = fmt

    def run(self):
        try:
            results = batch_convert(
                self.files,
                self.output_dir,
                self.fmt,
                progress_callback=lambda val: self.progress.emit(val)
            )
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class DropZone(QListWidget):
    """List widget that accepts file drops."""
    
    files_dropped = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFont(QFont("Consolas", 10))
        self.setMinimumHeight(200)

    def dragEnterEvent(self, event: QDragEnterEvent | None):
        if event and event.mimeData() and event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent | None):
        if event and event.mimeData():
            files = [u.toLocalFile() for u in event.mimeData().urls()]
            self.files_dropped.emit(files)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.files: List[str] = []
        self.output_dir = str(Path.home() / "Desktop")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("File Converter")
        self.setMinimumSize(600, 500)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)

        # File selection
        file_group = QGroupBox("Files")
        file_layout = QVBoxLayout(file_group)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Files")
        self.btn_add.clicked.connect(self.add_files)
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clear_files)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        
        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self.add_dropped_files)
        
        file_layout.addLayout(btn_layout)
        file_layout.addWidget(self.drop_zone)
        self.file_label = QLabel("0 files selected")
        file_layout.addWidget(self.file_label)
        layout.addWidget(file_group)

        # Output settings
        out_group = QGroupBox("Output")
        out_layout = QVBoxLayout(out_group)
        
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel("Convert to:"))
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(sorted([f.upper() for f in ALL_FORMATS]))
        self.fmt_combo.setCurrentText("PNG")
        fmt_layout.addWidget(self.fmt_combo)
        fmt_layout.addStretch()
        
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(f"Output: {self.output_dir}")
        self.dir_label.setWordWrap(True)
        self.btn_dir = QPushButton("Change")
        self.btn_dir.clicked.connect(self.change_output_dir)
        dir_layout.addWidget(self.dir_label, 1)
        dir_layout.addWidget(self.btn_dir)
        
        out_layout.addLayout(fmt_layout)
        out_layout.addLayout(dir_layout)
        layout.addWidget(out_group)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Convert button
        self.btn_convert = QPushButton("Convert")
        self.btn_convert.setMinimumHeight(50)
        self.btn_convert.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.btn_convert.clicked.connect(self.convert)
        layout.addWidget(self.btn_convert)

        layout.addStretch()

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files", "",
            "All Files (*);;Images (*.png *.jpg *.tiff *.bmp);;FITS (*.fit *.fits)"
        )
        if files:
            self.files.extend(files)
            self.update_file_list()

    def add_dropped_files(self, files: List[str]):
        self.files.extend(files)
        self.update_file_list()

    def clear_files(self):
        self.files.clear()
        self.update_file_list()

    def update_file_list(self):
        self.drop_zone.clear()
        for f in self.files:
            self.drop_zone.addItem(Path(f).name)
        self.file_label.setText(f"{len(self.files)} file(s) selected")

    def change_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Output Directory", self.output_dir)
        if dir_path:
            self.output_dir = dir_path
            self.dir_label.setText(f"Output: {self.output_dir}")

    def convert(self):
        if not self.files:
            QMessageBox.warning(self, "No Files", "Add files to convert.")
            return

        self.btn_convert.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.files))
        self.progress_bar.setValue(0)

        fmt = self.fmt_combo.currentText().lower()
        self.conv_thread = ConversionThread(self.files, self.output_dir, fmt)
        self.conv_thread.progress.connect(self.update_progress)
        self.conv_thread.finished.connect(self.conversion_done)
        self.conv_thread.error.connect(self.conversion_error)
        self.conv_thread.start()

    def update_progress(self, value: int):
        self.progress_bar.setValue(value)

    def conversion_done(self, results: List[str]):
        self.btn_convert.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        msg = f"Converted {len(results)} file(s) to {self.output_dir}"
        QMessageBox.information(self, "Done", msg)

    def conversion_error(self, error: str):
        self.btn_convert.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Conversion failed:\n{error}")
