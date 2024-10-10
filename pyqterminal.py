#!/usr/bin/env python3
import sys
import os
import configparser
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QToolBar,
    QMenu,
    QAction,
    QSlider,
    QLabel,
    QDialog,
    QTextEdit,
    QInputDialog,
    QFontDialog,
    QColorDialog
)
from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QFontMetrics, QTextCursor, QFont, QColor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = configparser.ConfigParser()
        self.config_file = os.path.expanduser('~/.pyqterminal.ini')
        print(f"Config file path: {self.config_file}")  # Debug print

        self.setWindowTitle("PyQTerminal")
        self.setGeometry(100, 100, 600, 400)

        # Atributo para tornar o fundo da janela transparente
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Barra no topo
        self.toolbar = QToolBar("Barra de Ferramentas", self)
        self.toolbar.setStyleSheet("background-color: rgba(0, 0, 0, 1);")  # Cor de fundo da barra
        self.addToolBar(self.toolbar)  # Adiciona a barra ao QMainWindow

        self.toolbar.setFixedHeight(40)
        self.toolbar.setMovable(False)

        # Criar menu Editar
        self.edit_menu = QMenu("Editar", self)

        # Criar uma ação para o menu
        self.edit_action = QAction("Editar", self)
        self.toolbar.addAction(self.edit_action)  # Adiciona a ação à barra de ferramentas

        # Conectar o clique da ação ao método que abre o menu
        self.edit_action.triggered.connect(self.show_edit_menu)

        # Adiciona ações ao menu
        font_action = QAction("Fonte", self)
        opacity_action = QAction("Opacidade", self)
        self.edit_menu.addAction(font_action)
        self.edit_menu.addAction(opacity_action)

        # Conectar a ação de opacidade a um método para abrir o controle deslizante
        opacity_action.triggered.connect(self.open_opacity_dialog)

        # Estilizar o menu
        self.edit_menu.setStyleSheet(
            "QMenu { background-color: rgba(255, 255, 255, 0.9); }"
            "QMenu::item { color: black; padding: 5px; }"
            "QMenu::item:selected { background-color: rgba(0, 0, 255, 0.3); color: white; }"  # Altera a cor do texto na seleção
        )

        # Área central
        self.central_widget = QWidget(self)  # Passar `self` como pai
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Ajustar margens e preenchimentos do layout
        self.layout.setContentsMargins(0, 0, 0, 0)  # Margens de 0
        self.layout.setSpacing(0)  # Espaçamento entre os widgets de 0

        # Adiciona um widget que terá a opacidade ajustável
        self.transparent_widget = QWidget(self.central_widget)
        self.layout.addWidget(self.transparent_widget)  # Adiciona o widget transparente ao layout
        self.transparent_layout = QVBoxLayout(self.transparent_widget)

        # Rótulo para mostrar o diretório atual no formato desejado
        directory_name = self.format_directory(os.getcwd())  # Formata o diretório atual

        # Estilizar o rótulo do diretório
        self.directory_label = self.create_directory_label(directory_name)

        self.transparent_layout.addWidget(self.directory_label)  # Adiciona o rótulo ao layout do widget transparente

        # Replace the transparent_layout.addStretch() with a QTextEdit
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("background-color: transparent; color: white;")
        self.transparent_layout.addWidget(self.output_area)

        # Add input line
        self.input_line = QLineEdit()
        self.input_line.setStyleSheet("background-color: rgba(255, 255, 255, 0.2); color: white;")
        self.transparent_layout.addWidget(self.input_line)

        # Set up QProcess for running terminal commands
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.command_finished)

        # Connect input_line to send_command method
        self.input_line.returnPressed.connect(self.send_command)

        # Modificar a ação de fonte existente
        self.font_action = self.edit_menu.actions()[0]  # Assumindo que "Fonte" é a primeira ação
        self.font_menu = QMenu("Fonte", self)
        self.font_action.setMenu(self.font_menu)

        # Adicionar ações ao submenu Fonte
        self.font_color_action = QAction("Cor", self)
        self.font_type_action = QAction("Tipo", self)

        self.font_menu.addAction(self.font_color_action)
        self.font_menu.addAction(self.font_type_action)

        # Conectar ações aos métodos correspondentes
        self.font_color_action.triggered.connect(self.change_font_color)
        self.font_type_action.triggered.connect(self.change_font_type)

        # Carregar ou criar configurações
        self.load_or_create_settings()

        # Aplicar a opacidade carregada
        self.set_transparent_background(self.opacity)

    def create_directory_label(self, directory_name):
        
        # Rótulo para mostrar o diretório atual no formato desejado
        directory_label = QLabel(f"📂 {directory_name}")  # Usando um ícone de pasta
        font_metrics = QFontMetrics(QLabel().font())
        text_width = font_metrics.width(directory_name)
        max_width = text_width + 50  # Ajuste conforme necessário
        
        # Definir a largura máxima permitida
        directory_label.setFixedWidth(max_width)  # Define a largura máxima para o QLabel

        # Estilizar o rótulo do diretório
        directory_label.setStyleSheet(
            "background-color: rgba(65, 125, 221, 0.8);"  # Cor de fundo com opacidade
            "color: white; font-weight: bold; font-size: 14px; padding: 5px;"  # Estilo do texto
        )
        
        return directory_label

    def format_directory(self, path):
        # Formata o caminho do diretório substituindo o diretório home por '~'
        home = os.path.expanduser("~")
        if path.startswith(home):
            return '~' + path[len(home):] 
        return path  # Retorna o caminho original se não for o diretório home

    def show_edit_menu(self):
        # Mostrar o menu Editar abaixo da ação Editar
        pos = self.toolbar.actionGeometry(self.edit_action).bottomLeft()
        pos = self.toolbar.mapToGlobal(pos)
        self.edit_menu.exec_(pos)

    def open_opacity_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajustar Opacidade")

        # Layout para o diálogo
        dialog_layout = QVBoxLayout(dialog)

        # Criação do controle deslizante
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)  # Faixa de 0 a 100
        slider.setValue(self.opacity)  # Usa o valor atual de opacidade
        slider.setTickInterval(10)
        slider.setTickPosition(QSlider.TicksBelow)

        # Rótulo para mostrar a opacidade atual
        label = QLabel(f"Opacidade: {self.opacity}%")
        
        # Conectar o controle deslizante ao método que ajusta a opacidade
        slider.valueChanged.connect(lambda value: self.set_opacity(value, label))

        dialog_layout.addWidget(slider)
        dialog_layout.addWidget(label)
        dialog.setLayout(dialog_layout)

        dialog.exec_()  # Exibe o diálogo

    def set_opacity(self, value, label=None):
        self.opacity = value
        self.set_transparent_background(value)
        if label:
            label.setText(f"Opacidade: {value}%")
        print(f"Set opacity to: {value}")  # Debug print
        self.save_settings()

    def set_transparent_background(self, opacity):
        # Ajusta a cor de fundo do widget transparente com base na opacidade
        self.transparent_widget.setStyleSheet(f"background-color: rgba(0, 0, 0, {opacity / 100});")
        print(f"Set background opacity to: {opacity}")  # Debug print

    def send_command(self):
        command = self.input_line.text()
        self.input_line.clear()
        self.output_area.append(f"$ {command}")  # Mostra o prompt e o comando digitado
        
        if command.strip().lower() == "clear":
            self.output_area.clear()  # Limpa a área de saída
        elif command.strip().lower() == "cd":
            # Change to home directory
            os.chdir(os.path.expanduser("~"))
            self.update_directory_label()
        elif command.startswith("cd "):
            # Change to specified directory
            new_dir = command[3:].strip()
            try:
                os.chdir(new_dir)
                self.update_directory_label()
            except FileNotFoundError:
                self.output_area.append(f"Directory not found: {new_dir}")
        elif command.startswith("sudo "):
            # Handle sudo commands
            self.execute_sudo_command(command)
        else:
            # For non-sudo commands, use QProcess
            self.process.start('bash', ['-c', command])
            self.input_line.setEnabled(False)
            QTimer.singleShot(100, self.check_process_state)

    def execute_sudo_command(self, command):
        # First, check if sudo requires a password
        check_process = QProcess()
        check_process.start('sudo', ['-n', 'true'])
        check_process.waitForFinished()

        if check_process.exitCode() == 0:
            # Sudo does not require a password, execute the command
            self.process.start('bash', ['-c', command])
        else:
            # Sudo requires a password, prompt for it
            password, ok = QInputDialog.getText(self, "Sudo", "Enter sudo password:", QLineEdit.Password)
            if ok:
                full_command = f"echo {password} | sudo -S {command[5:]}"
                self.process.start('bash', ['-c', full_command])
            else:
                self.output_area.append("Sudo command cancelled")
                return

        self.input_line.setEnabled(False)
        QTimer.singleShot(100, self.check_process_state)

    def check_process_state(self):
        if self.process.state() == QProcess.NotRunning:
            self.command_finished()
        else:
            QTimer.singleShot(100, self.check_process_state)

    def command_finished(self):
        self.update_directory_label()
        self.input_line.setEnabled(True)
        self.input_line.setFocus()

    def update_directory_label(self):
        current_dir = self.format_directory(os.getcwd())
        self.directory_label.setText(f"📂 {current_dir}")
        font_metrics = QFontMetrics(self.directory_label.font())
        text_width = font_metrics.width(current_dir)
        max_width = text_width + 50  # Ajuste conforme necessário
        self.directory_label.setFixedWidth(max_width)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.output_area.append(stdout.rstrip())
        self.output_area.moveCursor(QTextCursor.End)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.output_area.append(stderr.rstrip())
        self.output_area.moveCursor(QTextCursor.End)

    def change_font_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            new_color = color.name()
            self.output_area.setStyleSheet(f"background-color: transparent; color: {new_color};")
            print(f"Changed font color to: {new_color}")  # Debug print
            self.last_valid_color = new_color  # Armazena a última cor válida
            self.save_settings()
            print(f"Current style sheet after change: {self.output_area.styleSheet()}")  # Debug print

    def change_font_type(self):
        font, ok = QFontDialog.getFont(self.output_area.font(), self)
        if ok:
            self.output_area.setFont(font)
            self.save_settings()

    def load_or_create_settings(self):
        if not os.path.exists(self.config_file):
            self.create_default_config()
        self.load_settings()

    def create_default_config(self):
        self.config['Appearance'] = {
            'font_family': 'Monospace',
            'font_size': '12',
            'font_color': '#FFFFFF',
            'opacity': '85'
        }
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
        print(f"Created new config file: {self.config_file}")  # Debug print

    def load_settings(self):
        self.config.read(self.config_file)
        
        font_family = self.config.get('Appearance', 'font_family', fallback='Monospace')
        font_size = self.config.getint('Appearance', 'font_size', fallback=12)
        font_color = self.config.get('Appearance', 'font_color', fallback='#FFFFFF')
        self.opacity = self.config.getint('Appearance', 'opacity', fallback=85)

        font = QFont(font_family, font_size)
        self.output_area.setFont(font)
        self.output_area.setStyleSheet(f"background-color: transparent; color: {font_color};")
        self.set_transparent_background(self.opacity)
        print(f"Loaded font color: {font_color}")  # Debug print
        print(f"Loaded opacity: {self.opacity}")  # Debug print
        print(f"Current style sheet after loading: {self.output_area.styleSheet()}")  # Debug print

    def save_settings(self):
        style = self.output_area.styleSheet()
        print(f"Current style sheet before saving: {style}")  # Debug print
        
        # Extrai a cor da fonte do estilo
        font_color = next((s.split(':')[1].strip() for s in style.split(';') if 'color:' in s), '#FFFFFF')
        
        # Remove qualquer texto adicional após o valor da cor
        font_color = font_color.split()[0]
        
        # Se a cor for 'transparent', use a última cor válida ou branco como padrão
        if font_color == 'transparent':
            font_color = getattr(self, 'last_valid_color', '#FFFFFF')
        else:
            self.last_valid_color = font_color
        
        print(f"Extracted font color: {font_color}")  # Debug print
        print(f"Current opacity: {self.opacity}")  # Debug print

        self.config['Appearance'] = {
            'font_family': self.output_area.font().family(),
            'font_size': str(self.output_area.font().pointSize()),
            'font_color': font_color,
            'opacity': str(self.opacity)
        }

        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
        
        print(f"Saved font color: {font_color}")  # Debug print
        print(f"Saved opacity: {self.opacity}")  # Debug print

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())