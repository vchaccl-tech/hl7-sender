# HL7 Sender: A simple HL7 message sender with MLLP support for testing and debugging.
# Copyright (C) 2025 Victor Chacón + Antigravity by Google
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import sys
import socket
import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QCheckBox, QGroupBox, QMessageBox, QComboBox,
                             QFileDialog, QInputDialog, QSplitter)
from PyQt6.QtGui import QFont, QTextCharFormat, QSyntaxHighlighter, QColor, QClipboard, QAction
from PyQt6.QtCore import Qt
import re # Para expresiones regulares en el resaltador de sintaxis

def get_app_config_path(app_name):
    """Devuelve la ruta estándar para la configuración de la aplicación."""
    if sys.platform == 'darwin':  # macOS
        return os.path.join(os.path.expanduser('~/Library/Application Support'), app_name, 'hl7_sender_settings.json')
    elif sys.platform == 'win32':  # Windows
        return os.path.join(os.environ['APPDATA'], app_name, 'hl7_sender_settings.json')
    else:  # Linux y otros
        return os.path.join(os.path.expanduser('~/.config'), app_name, 'hl7_sender_settings.json')

SETTINGS_FILE = get_app_config_path('HL7Sender')

TRANSLATIONS = {
    "es": {
        "window_title": "HL7 Sender",
        "config_group": "Configuración",
        "host": "Host:",
        "port": "Puerto:",
        "timeout": "Timeout (s):",
        "encoding": "Codificación:",
        "expect_ack": "Esperar ACK",
        "profiles_group": "Perfiles de Conexión",
        "profile_label": "Perfil:",
        "profile_tooltip": "Selecciona un perfil para cargar su configuración.",
        "msg_group": "Mensaje HL7",
        "resp_group": "Respuesta / Estado",
        "paste_btn": "Pegar Mensaje",
        "paste_tooltip": "Limpia el mensaje actual y pega el contenido del portapapeles",
        "format_btn": "Formatear Mensaje",
        "test_btn": "Probar Conexión",
        "send_btn": "Enviar Mensaje",
        "menu_file": "&Archivo",
        "menu_load": "&Cargar Mensaje desde Archivo...",
        "menu_exit": "&Salir",
        "menu_msg": "&Mensaje",
        "menu_paste": "&Pegar desde Portapapeles",
        "menu_format": "&Formatear Mensaje",
        "menu_conn": "&Conexión",
        "menu_test": "&Probar Conexión",
        "menu_send": "&Enviar Mensaje",
        "menu_profiles": "&Perfiles",
        "menu_save_profile": "&Guardar Perfil...",
        "menu_del_profile": "&Eliminar Perfil",
        "menu_view": "&Ver",
        "menu_dark_mode": "Modo &Oscuro",
        "menu_lang": "&Idioma",
        "status_loaded": "Perfil '{}' cargado.",
        "status_saved": "Perfil '{}' guardado.",
        "status_deleted": "Perfil '{}' eliminado.",
        "status_all_deleted": "Todos los perfiles han sido eliminados.",
        "status_conn_test": "Probando conexión a {}:{}...",
        "status_conn_ok": "Conexión exitosa a {}:{}",
        "status_conn_timeout": "Error: Tiempo de espera agotado para {}:{}",
        "status_conn_refused": "Error: Conexión rechazada por {}:{}",
        "status_conn_error": "Error de conexión a {}:{}: {}",
        "status_msg_sent": "Mensaje enviado a {}:{} a las {} (no se espera ACK)",
        "status_msg_cleared": "Mensaje limpiado y portapapeles pegado.",
        "status_msg_empty": "Mensaje limpiado. El portapapeles está vacío.",
        "status_formatted": "Mensaje formateado para visualización.",
        "status_no_format": "No se encontraron segmentos para formatear o el mensaje ya está formateado.",
        "err_input_title": "Error de entrada",
        "err_port_num": "El Puerto debe ser un número.",
        "err_port_timeout_num": "Port y Timeout deben ser números.",
        "err_msg_empty_title": "Advertencia de entrada",
        "err_msg_empty": "El mensaje está vacío.",
        "err_encoding_title": "Error de codificación",
        "err_encoding_invalid": "Codificación inválida: {}",
        "err_encoding_fail": "No se pudo codificar el mensaje con {}:\n{}",
        "err_timeout": "Error: Tiempo de espera agotado.",
        "err_refused": "Error: Conexión rechazada.",
        "err_profile_none": "No hay ningún perfil seleccionado para eliminar.",
        "warn_title": "Advertencia",
        "confirm_del_title": "Eliminar Perfil",
        "confirm_del_msg": "¿Está seguro de que desea eliminar el perfil '{}'?",
        "err_profile_not_found": "El perfil '{}' no fue encontrado.",
        "input_profile_title": "Guardar Perfil",
        "input_profile_msg": "Nombre del perfil:",
        "file_dialog_title": "Abrir archivo de mensaje HL7",
        "file_err_title": "Error de Archivo",
        "file_err_msg": "No se pudo leer el archivo con la codificación '{}':\n{}",
        "status_file_loaded": "Mensaje cargado desde {}",
        "status_file_err": "Error al leer el archivo: {}",
        "ack_timeout": "Error: Tiempo de espera agotado. Verifique que el servidor esté escuchando y que no haya un firewall bloqueando la conexión.",
        "ack_refused": "Error: Conexión rechazada. Verifique que la IP y el puerto son correctos y que el servidor está en ejecución.",
        "ack_raw": "Respuesta Raw (Invalid MLLP):\n{}",
        "ack_decoded": "ACK Recibido (Error de decodificación con {}):\n{}\n\n{}"
    },
    "en": {
        "window_title": "HL7 Sender",
        "config_group": "Configuration",
        "host": "Host:",
        "port": "Port:",
        "timeout": "Timeout (s):",
        "encoding": "Encoding:",
        "expect_ack": "Expect ACK",
        "profiles_group": "Connection Profiles",
        "profile_label": "Profile:",
        "profile_tooltip": "Select a profile to load its settings.",
        "msg_group": "HL7 Message",
        "resp_group": "Response / Status",
        "paste_btn": "Paste Message",
        "paste_tooltip": "Clears current message and pastes clipboard content",
        "format_btn": "Format Message",
        "test_btn": "Test Connection",
        "send_btn": "Send Message",
        "menu_file": "&File",
        "menu_load": "&Load Message from File...",
        "menu_exit": "&Exit",
        "menu_msg": "&Message",
        "menu_paste": "&Paste from Clipboard",
        "menu_format": "&Format Message",
        "menu_conn": "&Connection",
        "menu_test": "&Test Connection",
        "menu_send": "&Send Message",
        "menu_profiles": "&Profiles",
        "menu_save_profile": "&Save Profile...",
        "menu_del_profile": "&Delete Profile",
        "menu_view": "&View",
        "menu_dark_mode": "&Dark Mode",
        "menu_lang": "&Language",
        "status_loaded": "Profile '{}' loaded.",
        "status_saved": "Profile '{}' saved.",
        "status_deleted": "Profile '{}' deleted.",
        "status_all_deleted": "All profiles have been deleted.",
        "status_conn_test": "Testing connection to {}:{}...",
        "status_conn_ok": "Connection successful to {}:{}",
        "status_conn_timeout": "Error: Connection timed out for {}:{}",
        "status_conn_refused": "Error: Connection refused by {}:{}",
        "status_conn_error": "Connection error to {}:{}: {}",
        "status_msg_sent": "Message sent to {}:{} at {} (no ACK expected)",
        "status_msg_cleared": "Message cleared and clipboard pasted.",
        "status_msg_empty": "Message cleared. Clipboard is empty.",
        "status_formatted": "Message formatted for display.",
        "status_no_format": "No segments found to format or message is already formatted.",
        "err_input_title": "Input Error",
        "err_port_num": "Port must be a number.",
        "err_port_timeout_num": "Port and Timeout must be numbers.",
        "err_msg_empty_title": "Input Warning",
        "err_msg_empty": "Message is empty.",
        "err_encoding_title": "Encoding Error",
        "err_encoding_invalid": "Invalid encoding: {}",
        "err_encoding_fail": "Could not encode message with {}:\n{}",
        "err_timeout": "Error: Timed out.",
        "err_refused": "Error: Connection refused.",
        "err_profile_none": "No profile selected to delete.",
        "warn_title": "Warning",
        "confirm_del_title": "Delete Profile",
        "confirm_del_msg": "Are you sure you want to delete profile '{}'?",
        "err_profile_not_found": "Profile '{}' not found.",
        "input_profile_title": "Save Profile",
        "input_profile_msg": "Profile name:",
        "file_dialog_title": "Open HL7 Message File",
        "file_err_title": "File Error",
        "file_err_msg": "Could not read file with encoding '{}':\n{}",
        "status_file_loaded": "Message loaded from {}",
        "status_file_err": "Error reading file: {}",
        "ack_timeout": "Error: Timed out. Check if server is listening and no firewall is blocking.",
        "ack_refused": "Error: Connection refused. Check IP and Port are correct and server is running.",
        "ack_raw": "Raw Response (Invalid MLLP):\n{}",
        "ack_decoded": "ACK Received (Decoding error with {}):\n{}\n\n{}"
    }
}

# Clase para el resaltado de sintaxis HL7
class Hl7Highlighter(QSyntaxHighlighter):
    HL7_SEGMENTS = [
        "MSH", "PID", "PV1", "ORC", "OBR", "DG1", "OBX", "SAC", # Ejemplos del usuario
        "EVN", "ADD", "AIG", "AIS", "AIL", "AL1", "APT", "ARQ", "AUT", "BHS",
        "BTS", "BLG", "CDM", "CER", "CM0", "CM1", "CM2", "CNS", "CSP", #"CON", 
        "CSR", "CSS", "CTD", "CTI", "DB1", "DDI", "DFT", "DG1", "DRG", "DSC",
        "DSP", "EHC", "EQL", "EQP", "EQT", "FAC", "FHS", "FT1", "GOL", "GP1",
        "GP2", "GT1", "Hxx", "IAM", "IAR", "IIM", "ILT", "IN1", "IN2", "IN3",
        "INV", "ISD", "LAN", "LCC", "LDP", "LRL", "MFA", "MFE", "MFI", #"LOC",
        "MRG", "MTN", "NAA", "NBS", "NDS", "NK1", "NPU", "NSC", "NST", "NTE",
        "OM1", "OM2", "OM3", "OM4", "OM5", "OM6", "OM7", "ORG", "PR1", "PRA",
        "PRB", "PRC", "PRD", "PSG", "PSH", "PTH", "PV2", "QCN", "QID", "RCP",
        "RDF", "RDT", "REL", "RF1", "RGS", "RMI", "ROL", "RQ1", "RQD", "RXA",
        "RXC", "RXD", "RXE", "RXG", "RXO", "RXR", "RXV", "SCH", "SPM", "STF",
        "TCC", "TCD", "TQ1", "TQ2", "TXA", "UB1", "UB2", "UR1", "VAR", "VMD",
        "VP1", "VTQ", "Zxx", "MSA" # Segmentos "Z" pueden ser personalizados, pero este es un placeholder
    ]

    def __init__(self, document, dark_mode=False):
        super().__init__(document)
        self.dark_mode = dark_mode
        self.update_colors()

        # Expresión regular para encontrar nombres de segmento que no están precedidos por una letra
        segments_pattern = '|'.join(self.HL7_SEGMENTS)
        self.segment_pattern = re.compile(r"(?<![A-Za-z])(%s)\b" % segments_pattern)
        
        # Expresión regular para números
        self.number_pattern = re.compile(r'\b\d+\b')
        
        # Expresión regular para separadores
        self.separator_pattern = re.compile(r'\|')
    
    def update_colors(self):
        """Actualiza los colores según el modo (claro u oscuro)."""
        if self.dark_mode:
            # Modo oscuro: colores más brillantes para mejor contraste
            # Formato para los nombres de segmento (R=176 G=139 B=206)
            self.segment_format = QTextCharFormat()
            self.segment_format.setForeground(QColor(176, 139, 206))  # Lavanda/Púrpura claro
            self.segment_format.setFontWeight(QFont.Weight.Bold)

            # Formato para números (R=80 G=178 B=180)
            self.number_format = QTextCharFormat()
            self.number_format.setForeground(QColor(80, 178, 180))  # Cyan/Verde azulado

            # Formato para separadores | (R=201 G=196 B=136)
            self.separator_format = QTextCharFormat()
            self.separator_format.setForeground(QColor(201, 196, 136))  # Amarillo pálido
        else:
            # Modo claro: colores originales
            # Formato para los nombres de segmento (R=102 G=37 B=102)
            self.segment_format = QTextCharFormat()
            self.segment_format.setForeground(QColor(102, 37, 102))  # Púrpura oscuro
            self.segment_format.setFontWeight(QFont.Weight.Bold)

            # Formato para números (R=162 G=59 B=96)
            self.number_format = QTextCharFormat()
            self.number_format.setForeground(QColor(162, 59, 96))  # Rosa oscuro

            # Formato para separadores | (R=89 G=89 B=89)
            self.separator_format = QTextCharFormat()
            self.separator_format.setForeground(QColor(89, 89, 89))  # Gris
    
    def set_dark_mode(self, dark_mode):
        """Cambia el modo y actualiza los colores."""
        self.dark_mode = dark_mode
        self.update_colors()
        self.rehighlight()

    def highlightBlock(self, text):
        # Primero, aplicar formato a los separadores
        for match in self.separator_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.separator_format)
        
        # Luego, aplicar formato a los números
        for match in self.number_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)
        
        # Finalmente, aplicar formato a los segmentos (para que tengan prioridad)
        for match in self.segment_pattern.finditer(text):
            self.setFormat(match.start(1), match.end(1) - match.start(1), self.segment_format)

class HL7SenderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HL7 Sender")
        self.setGeometry(100, 100, 960, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        # Reducir márgenes para un look más slim
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)

        # Cargar configuración inicial para obtener idioma
        settings = self._read_settings()
        self.current_lang = settings.get("state", {}).get("language", "es")
        if self.current_lang not in TRANSLATIONS:
            self.current_lang = "es"

        self.create_menus()
        self.create_widgets()
        self.retranslate_ui() # Aplicar textos iniciales
        self.statusBar()  # Inicializar la barra de estado
        
        # Cargar configuración antes de crear los highlighters
        self.load_settings_and_profiles()
        
        # Obtener el modo oscuro de la configuración
        settings = self._read_settings()
        self.dark_mode = settings.get("state", {}).get("dark_mode", False)
        
        # Instanciar el resaltador de sintaxis para el editor de mensajes
        self.hl7_highlighter = Hl7Highlighter(self.msg_text.document(), self.dark_mode)
        
        # Instanciar el resaltador de sintaxis para la respuesta ACK
        self.hl7_response_highlighter = Hl7Highlighter(self.resp_text.document(), self.dark_mode)
        
        # Aplicar el tema inicial
        self.apply_theme()
        
        # Actualizar el estado del checkbox del menú
        self.dark_mode_action.setChecked(self.dark_mode)
        
        # Restaurar geometría de la ventana
        self.restore_window_geometry()

    def create_menus(self):
        menubar = self.menuBar()
        
        # Menú Archivo
        self.file_menu = menubar.addMenu(self.tr("menu_file"))
        
        self.load_action = QAction(self.tr("menu_load"), self)
        self.load_action.setShortcut("Ctrl+O")
        self.load_action.triggered.connect(self.load_message_from_file)
        self.file_menu.addAction(self.load_action)
        
        self.file_menu.addSeparator()
        
        self.exit_action = QAction(self.tr("menu_exit"), self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(QApplication.instance().quit)
        self.file_menu.addAction(self.exit_action)
        
        # Menú Mensaje
        self.message_menu = menubar.addMenu(self.tr("menu_msg"))
        
        self.paste_action = QAction(self.tr("menu_paste"), self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.triggered.connect(self.clear_and_paste_clipboard)
        self.message_menu.addAction(self.paste_action)
        
        self.format_action = QAction(self.tr("menu_format"), self)
        self.format_action.setShortcut("Ctrl+F")
        self.format_action.triggered.connect(self.format_message_for_display)
        self.message_menu.addAction(self.format_action)
        
        # Menú Conexión
        self.connection_menu = menubar.addMenu(self.tr("menu_conn"))
        
        self.test_action = QAction(self.tr("menu_test"), self)
        self.test_action.setShortcut("Ctrl+T")
        self.test_action.triggered.connect(self.test_connection)
        self.connection_menu.addAction(self.test_action)
        
        self.send_action = QAction(self.tr("menu_send"), self)
        self.send_action.setShortcut("Ctrl+Return")
        self.send_action.triggered.connect(self.send_message)
        self.connection_menu.addAction(self.send_action)
        
        # Menú Perfiles
        self.profiles_menu = menubar.addMenu(self.tr("menu_profiles"))
        
        self.save_profile_action = QAction(self.tr("menu_save_profile"), self)
        self.save_profile_action.setShortcut("Ctrl+S")
        self.save_profile_action.triggered.connect(self.save_profile)
        self.profiles_menu.addAction(self.save_profile_action)
        
        self.delete_profile_action = QAction(self.tr("menu_del_profile"), self)
        self.delete_profile_action.setShortcut("Ctrl+D")
        self.delete_profile_action.triggered.connect(self.delete_profile)
        self.profiles_menu.addAction(self.delete_profile_action)
        
        # Menú Ver
        self.view_menu = menubar.addMenu(self.tr("menu_view"))
        
        self.dark_mode_action = QAction(self.tr("menu_dark_mode"), self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(False)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        self.view_menu.addAction(self.dark_mode_action)
        
        # Menú Idioma
        self.lang_menu = self.view_menu.addMenu("&Idioma")
        
        self.lang_es_action = QAction("Español", self)
        self.lang_es_action.setCheckable(True)
        self.lang_es_action.triggered.connect(lambda: self.change_language("es"))
        self.lang_menu.addAction(self.lang_es_action)
        
        self.lang_en_action = QAction("English", self)
        self.lang_en_action.setCheckable(True)
        self.lang_en_action.triggered.connect(lambda: self.change_language("en"))
        self.lang_menu.addAction(self.lang_en_action)
        
        self.update_lang_menu_state()

    def create_widgets(self):
        # Configuration Group
        self.config_group = QGroupBox(self.tr("config_group"))
        font = self.config_group.font()
        font.setPointSize(font.pointSize() + 1)
        self.config_group.setFont(font)
        config_layout = QHBoxLayout()
        config_layout.setContentsMargins(6, 6, 6, 6)
        
        # IP Address
        self.host_label = QLabel(self.tr("host"))
        config_layout.addWidget(self.host_label)
        self.ip_entry = QLineEdit()
        config_layout.addWidget(self.ip_entry)

        # Port
        self.port_label = QLabel(self.tr("port"))
        config_layout.addWidget(self.port_label)
        self.port_entry = QLineEdit()
        self.port_entry.setFixedWidth(80)
        config_layout.addWidget(self.port_entry)

        # Timeout
        self.timeout_label = QLabel(self.tr("timeout"))
        config_layout.addWidget(self.timeout_label)
        self.timeout_entry = QLineEdit()
        self.timeout_entry.setFixedWidth(50)
        config_layout.addWidget(self.timeout_entry)

        # Encoding
        self.encoding_label = QLabel(self.tr("encoding"))
        config_layout.addWidget(self.encoding_label)
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["utf-8", "iso-8859-1", "cp1252", "ascii"])
        config_layout.addWidget(self.encoding_combo)

        # Expect ACK
        self.expect_ack_check = QCheckBox(self.tr("expect_ack"))
        config_layout.addWidget(self.expect_ack_check)

        self.config_group.setLayout(config_layout)
        self.layout.addWidget(self.config_group)

        # Profiles Group
        self.profiles_group = QGroupBox(self.tr("profiles_group"))
        font = self.profiles_group.font()
        font.setPointSize(font.pointSize() + 1)
        self.profiles_group.setFont(font)
        profiles_layout = QHBoxLayout()
        profiles_layout.setContentsMargins(6, 6, 6, 6)
        
        self.profile_label = QLabel(self.tr("profile_label"))
        profiles_layout.addWidget(self.profile_label)
        self.profiles_combo = QComboBox()
        self.profiles_combo.setToolTip(self.tr("profile_tooltip"))
        self.profiles_combo.activated.connect(self.load_profile) # Load when selected
        profiles_layout.addWidget(self.profiles_combo)

        self.profiles_group.setLayout(profiles_layout)
        self.layout.addWidget(self.profiles_group)

        # Message Group
        self.msg_group = QGroupBox(self.tr("msg_group"))
        font = self.msg_group.font()
        font.setPointSize(font.pointSize() + 1)
        self.msg_group.setFont(font)
        msg_layout = QVBoxLayout()
        msg_layout.setContentsMargins(6, 6, 6, 6)
        
        self.msg_text = QTextEdit()
        self.msg_text.setFont(QFont("Consolas", 14))
        self.msg_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap) # Enable horizontal scrolling
        self.msg_text.setStyleSheet("QTextEdit { background-color: white; color: black; }")
        msg_layout.addWidget(self.msg_text)
        self.msg_group.setLayout(msg_layout)

        # Response Group
        self.resp_group = QGroupBox(self.tr("resp_group"))
        font = self.resp_group.font()
        font.setPointSize(font.pointSize() + 1)
        self.resp_group.setFont(font)
        resp_layout = QVBoxLayout()
        resp_layout.setContentsMargins(6, 6, 6, 6)
        self.resp_text = QTextEdit()
        self.resp_text.setFont(QFont("Consolas", 14))
        self.resp_text.setReadOnly(True)
        self.resp_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap) # Enable horizontal scrolling
        self.resp_text.setStyleSheet("QTextEdit { background-color: white; color: black; }")
        resp_layout.addWidget(self.resp_text)
        self.resp_group.setLayout(resp_layout)
        
        # Create splitter for message and response groups
        self.text_splitter = QSplitter(Qt.Orientation.Vertical)
        self.text_splitter.addWidget(self.msg_group)
        self.text_splitter.addWidget(self.resp_group)
        self.layout.addWidget(self.text_splitter)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.paste_clipboard_btn = QPushButton(self.tr("paste_btn"))
        self.paste_clipboard_btn.setToolTip(self.tr("paste_tooltip"))
        self.paste_clipboard_btn.clicked.connect(self.clear_and_paste_clipboard)
        btn_layout.addWidget(self.paste_clipboard_btn)
        
        self.format_msg_btn = QPushButton(self.tr("format_btn"))
        self.format_msg_btn.clicked.connect(self.format_message_for_display)
        btn_layout.addWidget(self.format_msg_btn)

        self.test_conn_btn = QPushButton(self.tr("test_btn"))
        self.test_conn_btn.clicked.connect(self.test_connection)
        btn_layout.addWidget(self.test_conn_btn)

        self.send_btn = QPushButton(self.tr("send_btn"))
        self.send_btn.setDefault(True) # Establecer como botón por defecto
        self.send_btn.clicked.connect(self.send_message)
        btn_layout.addWidget(self.send_btn)

        self.layout.addLayout(btn_layout)

    def set_status(self, message, timeout=0):
        """Muestra un mensaje en la barra de estado."""
        self.statusBar().showMessage(message, timeout)

    def set_response_text(self, message):
        """Muestra un mensaje en el área de texto de respuesta."""
        self.resp_text.setPlainText(message)

    def load_message_from_file(self):
        """Abre un diálogo para seleccionar un archivo y carga su contenido en el área de mensaje."""
        file_path, _ = QFileDialog.getOpenFileName(self, self.tr("file_dialog_title"), "", "Archivos de Texto (*.txt *.hl7);;Todos los Archivos (*)")
        if file_path:
            try:
                # Usar la codificación seleccionada en la UI para leer el archivo
                encoding = self.encoding_combo.currentText()
                with open(file_path, 'r', encoding=encoding) as f:
                    message = f.read()
                self.msg_text.setPlainText(message)
                self.set_status(self.tr("status_file_loaded").format(os.path.basename(file_path)), timeout=5000)
            except Exception as e:
                self.set_status(self.tr("status_file_err").format(e), timeout=5000)
                QMessageBox.critical(self, self.tr("file_err_title"), self.tr("file_err_msg").format(encoding, e))
    
    def clear_and_paste_clipboard(self):
        """Limpia el área de mensaje y pega el contenido del portapapeles."""
        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text()
        
        if clipboard_text:
            self.msg_text.clear()
            self.msg_text.setPlainText(clipboard_text)
            self.resp_text.clear() # Limpiar respuesta al pegar
            self.set_status(self.tr("status_msg_cleared"), timeout=3000)
        else:
            self.msg_text.clear()
            self.resp_text.clear() # Limpiar respuesta al limpiar
            self.set_status(self.tr("status_msg_empty"), timeout=3000)

    def format_message_for_display(self):
        """Formatea un mensaje HL7 de una sola línea, separando los segmentos para una mejor legibilidad."""
        self.resp_text.clear() # Limpiar respuesta al formatear
        current_message = self.msg_text.toPlainText()
        
        # 1. Reemplazar los separadores existentes (\r, \n) por un separador temporal único.
        temp_sep = "|||TEMP_SEP|||"
        text = current_message.replace('\r', temp_sep).replace('\n', temp_sep)

        # 2. Insertar el separador temporal antes de cada ID de segmento HL7.
        segments_pattern = '|'.join(Hl7Highlighter.HL7_SEGMENTS)
        # Se usa un lookbehind negativo `(?<![A-Za-z])` para asegurar que el segmento
        # no es parte de una palabra más larga (ej. no encontrar 'LOC' en 'LOCAL').
        regex = re.compile(r"(?<![A-Za-z])(%s\|)" % segments_pattern)
        
        text_with_seps = regex.sub(lambda m: temp_sep + m.group(1), text)

        # 3. Dividir el texto por el separador, limpiar y unir con saltos de línea.
        parts = [part.strip() for part in text_with_seps.split(temp_sep) if part.strip()]
        formatted_message = '\n'.join(parts)

        if formatted_message and formatted_message != current_message:
            self.msg_text.setPlainText(formatted_message)
            self.set_status(self.tr("status_formatted"), 3000)
        else:
            self.set_status(self.tr("status_no_format"), 5000)

    def _read_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            return {"profiles": {}, "state": {}}
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.set_status(self.tr("status_read_settings_err").format(e), 5000)
            return {"profiles": {}, "state": {}}

    def _write_settings(self, settings):
        try:
            config_dir = os.path.dirname(SETTINGS_FILE)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
        except IOError as e:
            self.set_status(self.tr("status_write_settings_err").format(e), 5000)
    
    def load_settings_and_profiles(self):
        settings = self._read_settings()

        # --- Migration from old format ---
        if "profiles" not in settings:
            self.set_status(self.tr("status_migrating_settings"), 5000)
            migrated_profile = {
                "ip": settings.get("ip", "127.0.0.1"),
                "port": settings.get("port", "2575"),
                "timeout": settings.get("timeout", "10"),
                "encoding": settings.get("encoding", "utf-8"),
                "expect_ack": settings.get("expect_ack", True),
            }
            last_message = settings.get("last_message", "")
            
            settings = {
                "profiles": {"Default": migrated_profile},
                "state": {"last_profile": "Default", "last_message": last_message}
            }
            self._write_settings(settings)
        # --- End Migration ---

        self._populate_profiles_combo()

        last_profile_name = settings.get("state", {}).get("last_profile")
        if last_profile_name and last_profile_name in settings.get("profiles", {}):
            self.profiles_combo.setCurrentText(last_profile_name)
            self.load_profile()
        elif self.profiles_combo.count() > 0:
            self.profiles_combo.setCurrentIndex(0)
            self.load_profile()
        else:
            # No profiles exist, set default values
            self.ip_entry.setText("127.0.0.1")
            self.port_entry.setText("2575")
            self.timeout_entry.setText("10")
            self.encoding_combo.setCurrentText("utf-8")
            self.expect_ack_check.setChecked(True)

        self.msg_text.setText(settings.get("state", {}).get("last_message", ""))
        
        # Load splitter state
        splitter_sizes = settings.get("state", {}).get("splitter_sizes")
        if splitter_sizes:
            self.text_splitter.setSizes(splitter_sizes)
    
    def restore_window_geometry(self):
        """Restaura el tamaño y posición de la ventana desde la configuración."""
        settings = self._read_settings()
        geometry = settings.get("state", {}).get("window_geometry")
        
        if geometry:
            self.setGeometry(geometry["x"], geometry["y"], geometry["width"], geometry["height"])
        else:
            # Valores por defecto si no hay configuración guardada
            self.setGeometry(100, 100, 960, 700)
    
    def toggle_dark_mode(self):
        """Alterna entre modo claro y oscuro."""
        self.dark_mode = self.dark_mode_action.isChecked()
        self.apply_theme()
        
        # Guardar la preferencia
        settings = self._read_settings()
        if "state" not in settings:
            settings["state"] = {}
        settings["state"]["dark_mode"] = self.dark_mode
        self._write_settings(settings)
    
    def apply_theme(self):
        """Aplica el tema (claro u oscuro) a los cuadros de texto."""
        if self.dark_mode:
            # Modo oscuro (Fondo R=35 G=35 B=35)
            style = "QTextEdit { background-color: #232323; color: #d4d4d4; }"
        else:
            # Modo claro
            style = "QTextEdit { background-color: white; color: black; }"
        
        self.msg_text.setStyleSheet(style)
        self.resp_text.setStyleSheet(style)
        
        # Actualizar los highlighters
        self.hl7_highlighter.set_dark_mode(self.dark_mode)
        self.hl7_response_highlighter.set_dark_mode(self.dark_mode)

        self.hl7_response_highlighter.set_dark_mode(self.dark_mode)

    def change_language(self, lang_code):
        if lang_code == self.current_lang:
            return
            
        self.current_lang = lang_code
        self.retranslate_ui()
        self.update_lang_menu_state()
        
        # Guardar preferencia
        settings = self._read_settings()
        if "state" not in settings:
            settings["state"] = {}
        settings["state"]["language"] = self.current_lang
        self._write_settings(settings)

    def update_lang_menu_state(self):
        self.lang_es_action.setChecked(self.current_lang == "es")
        self.lang_en_action.setChecked(self.current_lang == "en")

    def tr(self, key):
        """Helper para obtener traducción."""
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS["es"]).get(key, key)

    def retranslate_ui(self):
        """Actualiza todos los textos de la interfaz."""
        self.setWindowTitle(self.tr("window_title"))
        
        # Grupos
        self.config_group.setTitle(self.tr("config_group"))
        self.profiles_group.setTitle(self.tr("profiles_group"))
        self.msg_group.setTitle(self.tr("msg_group"))
        self.resp_group.setTitle(self.tr("resp_group"))
        
        # Etiquetas
        self.host_label.setText(self.tr("host"))
        self.port_label.setText(self.tr("port"))
        self.timeout_label.setText(self.tr("timeout"))
        self.encoding_label.setText(self.tr("encoding"))
        self.profile_label.setText(self.tr("profile_label"))
        
        # Checkbox y Tooltips
        self.expect_ack_check.setText(self.tr("expect_ack"))
        self.profiles_combo.setToolTip(self.tr("profile_tooltip"))
        
        # Botones
        self.paste_clipboard_btn.setText(self.tr("paste_btn"))
        self.paste_clipboard_btn.setToolTip(self.tr("paste_tooltip"))
        self.format_msg_btn.setText(self.tr("format_btn"))
        self.test_conn_btn.setText(self.tr("test_btn"))
        self.send_btn.setText(self.tr("send_btn"))
        
        # Menús
        self.menuBar().actions()[0].setText(self.tr("menu_file"))
        self.menuBar().actions()[1].setText(self.tr("menu_msg"))
        self.menuBar().actions()[2].setText(self.tr("menu_conn"))
        self.menuBar().actions()[3].setText(self.tr("menu_profiles"))
        self.menuBar().actions()[4].setText(self.tr("menu_view"))
        
        # Acciones de menú (necesitamos referencias o buscarlas, pero como las creamos en create_menus, 
        # lo mejor es guardar referencias en create_menus o recrearlos. 
        # Para simplificar, actualizaremos las referencias que tenemos si las guardamos como self.
        # En este caso, voy a actualizar create_menus para guardar referencias a las acciones principales)
        
        # Actualizando textos de acciones guardadas (necesito modificar create_menus para guardar referencias)
        # Por ahora, recrearé los menús es una opción, pero perdería conexiones.
        # Mejor modificaré create_menus para guardar referencias a las acciones.
        
        self.file_menu.setTitle(self.tr("menu_file"))
        self.load_action.setText(self.tr("menu_load"))
        self.exit_action.setText(self.tr("menu_exit"))
        
        self.message_menu.setTitle(self.tr("menu_msg"))
        self.paste_action.setText(self.tr("menu_paste"))
        self.format_action.setText(self.tr("menu_format"))
        
        self.connection_menu.setTitle(self.tr("menu_conn"))
        self.test_action.setText(self.tr("menu_test"))
        self.send_action.setText(self.tr("menu_send"))
        
        self.profiles_menu.setTitle(self.tr("menu_profiles"))
        self.save_profile_action.setText(self.tr("menu_save_profile"))
        self.delete_profile_action.setText(self.tr("menu_del_profile"))
        
        self.view_menu.setTitle(self.tr("menu_view"))
        self.dark_mode_action.setText(self.tr("menu_dark_mode"))
        self.lang_menu.setTitle(self.tr("menu_lang"))

    def _populate_profiles_combo(self):
        self.profiles_combo.blockSignals(True)
        self.profiles_combo.clear()
        settings = self._read_settings()
        profiles = sorted(settings.get("profiles", {}).keys())
        self.profiles_combo.addItems(profiles)
        self.profiles_combo.blockSignals(False)

    def load_profile(self):
        profile_name = self.profiles_combo.currentText()
        if not profile_name:
            return

        settings = self._read_settings()
        profile = settings.get("profiles", {}).get(profile_name)

        if profile:
            self.ip_entry.setText(profile.get("ip", ""))
            self.port_entry.setText(profile.get("port", ""))
            self.timeout_entry.setText(profile.get("timeout", ""))
            self.encoding_combo.setCurrentText(profile.get("encoding", "utf-8"))
            self.expect_ack_check.setChecked(profile.get("expect_ack", True))
            self.set_status(self.tr("status_loaded").format(profile_name), 5000)

    def save_profile(self):
        profile_name, ok = QInputDialog.getText(self, self.tr("input_profile_title"), self.tr("input_profile_msg"))
        if ok and profile_name:
            settings = self._read_settings()
            
            if "profiles" not in settings:
                settings["profiles"] = {}

            settings["profiles"][profile_name] = {
                "ip": self.ip_entry.text(),
                "port": self.port_entry.text(),
                "timeout": self.timeout_entry.text(),
                "encoding": self.encoding_combo.currentText(),
                "expect_ack": self.expect_ack_check.isChecked(),
            }
            
            self._write_settings(settings)
            self._populate_profiles_combo()
            self.profiles_combo.setCurrentText(profile_name)
            self.set_status(self.tr("status_saved").format(profile_name), 5000)

    def delete_profile(self):
        profile_name = self.profiles_combo.currentText()
        if not profile_name:
            QMessageBox.warning(self, self.tr("warn_title"), self.tr("err_profile_none"))
            return

        reply = QMessageBox.question(self, self.tr("confirm_del_title"), 
                                     self.tr("confirm_del_msg").format(profile_name),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Leer configuración fresca
            settings = self._read_settings()
            
            # Verificar si el perfil existe en la configuración leída
            if "profiles" in settings and profile_name in settings["profiles"]:
                # Eliminar el perfil
                del settings["profiles"][profile_name]
                
                # Si el perfil eliminado era el último usado, limpiar esa referencia
                if settings.get("state", {}).get("last_profile") == profile_name:
                    settings["state"]["last_profile"] = ""
                
                # Guardar los cambios inmediatamente
                self._write_settings(settings)
                
                # Forzar una pequeña espera o recarga para asegurar persistencia (opcional, pero buena práctica si hay problemas de I/O)
                # En este caso, confiamos en _write_settings pero verificamos releyendo
                
                verification = self._read_settings()
                if profile_name not in verification.get("profiles", {}):
                    # Éxito confirmado
                    self.set_status(self.tr("status_deleted").format(profile_name), 5000)
                    
                    # Actualizar UI
                    self._populate_profiles_combo()
                    
                    # Cargar otro perfil o limpiar
                    if self.profiles_combo.count() > 0:
                        self.profiles_combo.setCurrentIndex(0)
                        self.load_profile()
                    else:
                        self.ip_entry.clear()
                        self.port_entry.clear()
                        self.timeout_entry.clear()
                        self.encoding_combo.setCurrentIndex(0)
                        self.expect_ack_check.setChecked(True)
                        self.set_status(self.tr("status_all_deleted"), 5000)
                else:
                    QMessageBox.critical(self, self.tr("critical_error_title"), self.tr("err_delete_profile_file").format(profile_name))
            else:
                # El perfil estaba en el combo pero no en el archivo (desincronización)
                QMessageBox.warning(self, self.tr("warn_title"), self.tr("err_profile_not_found").format(profile_name))
                self._populate_profiles_combo()

    def save_state(self):
        settings = self._read_settings()
        if "state" not in settings:
            settings["state"] = {}
        
        settings["state"]["last_profile"] = self.profiles_combo.currentText()
        settings["state"]["last_message"] = self.msg_text.toPlainText()
        settings["state"]["splitter_sizes"] = self.text_splitter.sizes()
        
        # Guardar geometría de la ventana
        geometry = self.geometry()
        settings["state"]["window_geometry"] = {
            "x": geometry.x(),
            "y": geometry.y(),
            "width": geometry.width(),
            "height": geometry.height()
        }
        
        self._write_settings(settings)

    def closeEvent(self, event):
        self.save_state()
        super().closeEvent(event)

    def test_connection(self):
        ip = self.ip_entry.text()
        try:
            port = int(self.port_entry.text())
            timeout = 5.0 # Usar un timeout fijo para la prueba de conexión
        except ValueError:
            QMessageBox.critical(self, self.tr("err_input_title"), self.tr("err_port_num"))
            return

        self.resp_text.clear() # Limpiar respuesta al probar conexión
        self.set_status(self.tr("status_conn_test").format(ip, port), timeout=0)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((ip, port))
            self.set_status(self.tr("status_conn_ok").format(ip, port), timeout=5000)
        except socket.timeout:
            self.set_status(self.tr("status_conn_timeout").format(ip, port), timeout=5000)
        except ConnectionRefusedError:
            self.set_status(self.tr("status_conn_refused").format(ip, port), timeout=5000)
        except Exception as e:
            self.set_status(self.tr("status_conn_error").format(ip, port, e), timeout=5000)

    def send_message(self):
        
        ip = self.ip_entry.text()
        try:
            port = int(self.port_entry.text())
            timeout = float(self.timeout_entry.text())
        except ValueError:
            QMessageBox.critical(self, self.tr("err_input_title"), self.tr("err_port_timeout_num"))
            return

        message = self.msg_text.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, self.tr("err_msg_empty_title"), self.tr("err_msg_empty"))
            return

        # Normalizar separadores de segmento a CR (\r) para compatibilidad con sistemas estrictos.
        message = message.replace('\r\n', '\r').replace('\n', '\r')

        encoding = self.encoding_combo.currentText()
        self.set_response_text("")  # Limpiar respuesta anterior
        self.set_status("")         # Limpiar barra de estado anterior

        # MLLP Wrapping
        VT = b'\x0b'
        FS = b'\x1c'
        CR = b'\x0d'
        
        try:
            wrapped_msg = VT + message.encode(encoding, errors='replace') + FS + CR
        except LookupError:
             QMessageBox.critical(self, self.tr("err_encoding_title"), self.tr("err_encoding_invalid").format(encoding))
             return
        except UnicodeEncodeError as e:
             QMessageBox.critical(self, self.tr("err_encoding_title"), self.tr("err_encoding_fail").format(encoding, e))
             return

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                # self.set_status(f"Enviando a {ip}:{port}...", timeout=0) # Removed this line as per user request
                s.connect((ip, port))
                
                sent_time = datetime.now()
                s.sendall(wrapped_msg)
                
                if self.expect_ack_check.isChecked():
                    response = s.recv(4096)
                    received_time = datetime.now()
                    response_time_ms = (received_time - sent_time).total_seconds() * 1000
                    
                    status_msg = (
                        f"Envío: {sent_time.strftime('%H:%M:%S.%f')[:-3]} | "
                        f"Recibido: {received_time.strftime('%H:%M:%S.%f')[:-3]} | "
                        f"Tiempo: {response_time_ms:.2f} ms"
                    )
                    self.set_status(status_msg)
                    
                    # MLLP Unwrapping
                    if response.startswith(VT) and response.endswith(FS + CR):
                        try:
                            ack_msg = response[1:-2].decode(encoding)
                            self.set_response_text(ack_msg)
                        except UnicodeDecodeError as e:
                            self.set_response_text(self.tr("ack_decoded").format(encoding, response[1:-2], e))
                    else:
                        self.set_response_text(self.tr("ack_raw").format(response))
                else:
                    self.set_status(self.tr("status_msg_sent").format(ip, port, sent_time.strftime('%H:%M:%S.%f')[:-3]))
                    
        except socket.timeout:
            self.set_status(self.tr("err_timeout"))
            self.set_response_text(self.tr("ack_timeout"))
        except ConnectionRefusedError:
            self.set_status(self.tr("err_refused"))
            self.set_response_text(self.tr("ack_refused"))
        except Exception as e:
            self.set_status(f"Error: {e}")
            self.set_response_text(str(e))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HL7SenderApp()
    window.show()
    sys.exit(app.exec())
