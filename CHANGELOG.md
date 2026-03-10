# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0] - 2025-12-03

### Características Principales

#### Envío de Mensajes HL7
- Envío de mensajes HL7 a través del protocolo MLLP (Minimal Lower Layer Protocol)
- Soporte completo para ACK/NACK
- Timeout configurable para conexiones
- Múltiples codificaciones: UTF-8, ISO-8859-1, CP1252, ASCII

#### Interfaz de Usuario
- Interfaz gráfica moderna con PyQt6
- Resaltado de sintaxis para mensajes HL7 (segmentos, números, separadores)
- Modo oscuro y claro para mejor ergonomía visual
- Diseño responsive con splitter ajustable
- Atajos de teclado para acciones comunes

#### Gestión de Configuración
- Sistema de perfiles de conexión
- Guardado automático de la última configuración utilizada
- Persistencia de mensajes entre sesiones
- Restauración de geometría de ventana

#### Idiomas
- Soporte multiidioma (Español e Inglés)
- Persistencia de preferencia de idioma

#### Herramientas
- Test de conectividad antes del envío
- Formateo automático de mensajes HL7
- Carga de mensajes desde archivo
- Pegar desde portapapeles con limpieza automática
- Servidor mock incluido para pruebas locales (`mock_server.py`)

#### Empaquetado
- Configuración de PyInstaller para generar aplicación standalone
- Icono personalizado de aplicación
- Bundle identifier: `com.vchac.hl7sender`

### Detalles Técnicos
- Python 3.8+
- PyQt6 6.4+
- Licencia: GPL-3.0
- Configuración guardada en ubicaciones estándar del sistema operativo

---

**Nota**: Esta es la versión inicial (1.0) del proyecto HL7 Sender.
