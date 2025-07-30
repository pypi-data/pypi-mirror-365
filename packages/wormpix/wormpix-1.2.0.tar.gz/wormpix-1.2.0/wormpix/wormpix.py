#!/usr/bin/env python3
"""
WormPix - Advanced Eye Comfort Tool
Author: Lunar Labs (GitHub: LunarLumos)
"""

import sys, os, json, subprocess, webbrowser
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QCheckBox,
    QSystemTrayIcon, QMenu, QMessageBox, QHBoxLayout, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

CONFIG = os.path.expanduser("~/.wormpix_config.json")
ICON_PATH = os.path.join(os.path.dirname(__file__), "wormpix_icon.png")
GITHUB_URL = "https://github.com/LunarLumos/wormpix"

def run(cmd): subprocess.call(cmd, shell=True)
def get_display():
    out = os.popen("xrandr --query | grep ' connected'").read().split()
    return out[0] if out else None
def set_gamma(r,g,b):
    disp = get_display()
    if disp: run(f"xrandr --output {disp} --gamma {r}:{g}:{b}")
def set_brightness(val):
    disp = get_display()
    if disp: run(f"xrandr --output {disp} --brightness {val}")

class WormPix(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐉 WormPix - Eye Comfort")
        self.setMinimumSize(460, 400)
        self.setWindowIcon(QIcon(ICON_PATH) if os.path.exists(ICON_PATH) else QIcon())

        self.setStyleSheet("""
            QWidget { background:#1a1a1a; color:#00ff99; font-size:15px; }
            QPushButton { background:#004d33; color:white; border-radius:5px; padding:6px; }
            QPushButton:hover { background:#009966; }
        """)

        layout = QVBoxLayout()

        # Title
        title = QLabel("🐉 WormPix")
        title.setStyleSheet("font-size:28px; color:#00ffaa; font-weight:bold;")
        layout.addWidget(title)

        # Warmth Slider
        self.label = QLabel("Warmth: 50%")
        layout.addWidget(self.label)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0,100); self.slider.setValue(50)
        self.slider.valueChanged.connect(self.update_warmth)
        layout.addWidget(self.slider)

        # Presets
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Presets:")
        self.presets = QComboBox()
        self.presets.addItems(["Cool", "Normal", "Warm", "Night"])
        self.presets.currentTextChanged.connect(self.apply_preset)
        preset_layout.addWidget(preset_label); preset_layout.addWidget(self.presets)
        layout.addLayout(preset_layout)

        # Brightness
        self.brightness_label = QLabel("Brightness: 100%")
        layout.addWidget(self.brightness_label)
        self.bright_slider = QSlider(Qt.Orientation.Horizontal)
        self.bright_slider.setRange(30,150); self.bright_slider.setValue(100)
        self.bright_slider.valueChanged.connect(self.update_brightness)
        layout.addWidget(self.bright_slider)

        # Reading Mode
        self.reading = QCheckBox("Enable Reading Mode")
        self.reading.stateChanged.connect(self.toggle_reading)
        layout.addWidget(self.reading)

        # Eye Rest Alarm
        alarm_layout = QHBoxLayout()
        self.alarm_time = QSpinBox()
        self.alarm_time.setRange(5, 120)
        self.alarm_time.setValue(20)
        self.alarm_time.setSuffix(" min")
        alarm_layout.addWidget(QLabel("Eye Rest Interval:"))
        alarm_layout.addWidget(self.alarm_time)
        self.btn_alarm = QPushButton("Enable Eye Rest Alarm")
        self.btn_alarm.clicked.connect(self.toggle_alarm)
        alarm_layout.addWidget(self.btn_alarm)
        layout.addLayout(alarm_layout)

        self.alarm_on = False
        self.alarm_timer = QTimer()
        self.alarm_timer.timeout.connect(self.eye_alarm)

        # GitHub Button
        github_btn = QPushButton("🌐 View on GitHub")
        github_btn.clicked.connect(lambda: webbrowser.open(GITHUB_URL))
        layout.addWidget(github_btn)

        # Branding
        branding = QLabel("Made by Lunar Lumos")
        branding.setStyleSheet("font-size:14px; color:#00cc88;")
        layout.addWidget(branding)

        # Exit
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)

        self.setLayout(layout)

        # Tray Icon
        self.tray = QSystemTrayIcon(QIcon(ICON_PATH) if os.path.exists(ICON_PATH) else QIcon())
        self.tray.setToolTip("WormPix Running")
        self.tray.setVisible(True)
        menu = QMenu()
        menu.addAction("Restore", self.show)
        menu.addAction("Quit", self.close)
        self.tray.setContextMenu(menu)

        self.load_config()

    def update_warmth(self,val):
        if self.reading.isChecked(): return
        r = round(0.8+(val/100)*0.6,2); g=1.0; b=round(1.2-(val/100)*0.5,2)
        set_gamma(r,g,b)
        self.label.setText(f"Warmth: {val}%")
        self.save_config()

    def update_brightness(self,val):
        set_brightness(val/100)
        self.brightness_label.setText(f"Brightness: {val}%")
        self.save_config()

    def toggle_reading(self):
        if self.reading.isChecked():
            set_gamma(1.2,1.0,0.8); self.slider.setEnabled(False)
        else:
            self.slider.setEnabled(True); self.update_warmth(self.slider.value())
        self.save_config()

    def apply_preset(self,preset):
        modes = {"Cool":(0.9,1.0,1.1),"Normal":(1.0,1.0,1.0),
                 "Warm":(1.15,1.0,0.85),"Night":(1.25,1.0,0.7)}
        r,g,b = modes[preset]; set_gamma(r,g,b)
        self.label.setText(f"Preset Applied: {preset}")
        self.save_config()

    def toggle_alarm(self):
        if self.alarm_on:
            self.alarm_timer.stop()
            self.alarm_on=False
            self.btn_alarm.setText("Enable Eye Rest Alarm")
        else:
            minutes = self.alarm_time.value()
            self.alarm_timer.start(minutes * 60 * 1000)
            self.alarm_on=True
            self.btn_alarm.setText("Disable Eye Rest Alarm")

    def eye_alarm(self):
        QMessageBox.information(self,"Eye Rest Reminder",
                                "⏳ Time to rest your eyes!\nFollow the 20-20-20 rule.")

    def save_config(self):
        cfg = {
            "warmth": self.slider.value(),
            "brightness": self.bright_slider.value(),
            "reading": self.reading.isChecked(),
            "alarm_time": self.alarm_time.value()
        }
        with open(CONFIG,"w") as f: json.dump(cfg,f)

    def load_config(self):
        if os.path.exists(CONFIG):
            cfg=json.load(open(CONFIG))
            self.slider.setValue(cfg.get("warmth",50))
            self.bright_slider.setValue(cfg.get("brightness",100))
            self.reading.setChecked(cfg.get("reading",False))
            self.alarm_time.setValue(cfg.get("alarm_time",20))

def main():
    app = QApplication(sys.argv)
    w = WormPix()
    w.show()
    sys.exit(app.exec())
