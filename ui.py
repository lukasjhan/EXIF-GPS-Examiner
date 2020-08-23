import sys
from fractions import Fraction

import piexif
import folium
from geopy.geocoders import Nominatim
import webbrowser

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QFileDialog

def to_deg(value, loc):
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60, 5)
    return (deg, min, sec, loc_value)

def change_to_rational(number):
    f = Fraction(str(number))
    return (f.numerator, f.denominator)

def set_gps_location(file_name, lat, lng, altitude):
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])

    exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
    exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
        piexif.GPSIFD.GPSAltitudeRef: b'\x01',
        piexif.GPSIFD.GPSAltitude: change_to_rational(altitude),
        piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
        piexif.GPSIFD.GPSLatitude: exiv_lat,
        piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
        piexif.GPSIFD.GPSLongitude: exiv_lng,
    }

    exif_dict = {"GPS": gps_ifd}
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_name)

class Form(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.filepath = ""
        self.lat = 0.0
        self.log = 0.0
        self.al = 0.0
        self.ready = False

        self.ui = uic.loadUi("main.ui", self)
        self.setWindowTitle("JPG GPS Verifier")

        self.ui.LoadButton.clicked.connect(self.load_button_clicked)
        self.ui.SaveButton.clicked.connect(self.save_button_clicked)
        self.ui.VerifyButton.clicked.connect(self.verify_button_clicked)
        self.ui.CheckLocButton.clicked.connect(self.checkloc_button_clicked)

        self.ui.show()

    @pyqtSlot()
    def load_button_clicked(self):
        self.filepath = QFileDialog.getOpenFileName(self)[0]
        if len(self.filepath) == 0:
            return
        
        exif_dict = piexif.load("test.jpg")

        lat_ref = ''
        lat = 0.0
        log_ref = ''
        log = 0.0
        al = 0.0

        for tag in exif_dict["GPS"]:
            if piexif.TAGS["GPS"][tag]["name"] == 'GPSLatitude':
                e = exif_dict["GPS"][tag]
                lat = float(e[0][0]/e[0][1]) + (float(e[1][0]/e[1][1]) / 60) + (float(e[2][0]/e[2][1]) / 3600)
            elif piexif.TAGS["GPS"][tag]["name"] == 'GPSLatitudeRef':
                lat_ref = exif_dict["GPS"][tag]
            elif piexif.TAGS["GPS"][tag]["name"] == 'GPSLongitude':
                e = exif_dict["GPS"][tag]
                log = float(e[0][0]/e[0][1]) + (float(e[1][0]/e[1][1]) / 60) + (float(e[2][0]/e[2][1]) / 3600)
            elif piexif.TAGS["GPS"][tag]["name"] == 'GPSLongitudeRef':
                log_ref = exif_dict["GPS"][tag]
            elif piexif.TAGS["GPS"][tag]["name"] == 'GPSAltitude':
                e = exif_dict["GPS"][tag]
                al = float(e[0]/e[1])

        if lat_ref == b'S':
            lat = -lat
        if log_ref == b'W':
            log = -log

        self.ui.latTextEdit.setText(str(lat))
        self.ui.logTextEdit.setText(str(log))
        self.ui.alTextEdit.setText(str(al))

        self.lat = lat
        self.log = log
        self.al = al
        self.ui.StatusLabel.setText("로드 완료")
        self.ready = True

    @pyqtSlot()
    def save_button_clicked(self):
        if self.ready == False:
            return

        self.lat = float(self.ui.latTextEdit.text())
        self.log = float(self.ui.logTextEdit.text())
        self.al = float(self.ui.alTextEdit.text())

        set_gps_location(self.filepath, self.lat, self.log, self.al)
        self.ui.StatusLabel.setText("저장완료")

    @pyqtSlot()
    def verify_button_clicked(self):
        if self.ready == False:
            return

        geolocator = Nominatim(user_agent="test_app_for_bob")
        try:
            location = geolocator.reverse(str(self.lat) + ', ' + str(self.log), timeout=10)
        except:
            self.ui.StatusLabel.setText("타임아웃. 다시 시도해주세요")
        
        if abs(location.altitude - self.al) < 3:
            self.ui.StatusLabel.setText("조작되지 않은 정보입니다.")
        else:
            self.ui.StatusLabel.setText("조작된 정보입니다.")
    
    @pyqtSlot()
    def checkloc_button_clicked(self):
        if self.ready == False:
            return

        my_map = folium.Map(location=[self.lat, self.log], zoom_start=20)
        my_map.save("loc.html")
        webbrowser.open("loc.html")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Form()
    sys.exit(app.exec())