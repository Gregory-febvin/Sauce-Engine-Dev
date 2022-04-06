from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QLabel, QFileDialog, QComboBox, QLineEdit
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import uic
from PyQt5 import QtGui
import sys
import re
from pathlib import Path

from multiprocessing.pool import ThreadPool

from tkinter import filedialog
from tkinter import *
from bs4 import BeautifulSoup

import urllib.request
import requests
import json


class UI(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("Interface.ui", self)

        self.setWindowIcon(QtGui.QIcon('thumb.ico'))

        self.labelSauce = self.findChild(QLabel, "LabelPath")
        self.buttonPath = self.findChild(QPushButton, "ButtonPath")
        self.ButtonPreview = self.findChild(QPushButton, "ButtonPreview")
        self.ButtonDl = self.findChild(QPushButton, "ButtonDownload")
        self.ComboBox = self.findChild(QComboBox, "URLsite")
        self.LabelNum = self.findChild(QLineEdit, "SauceInput")

        self.erreur = self.findChild(QLabel, "erreur")
        self.erreur2 = self.findChild(QLabel, "erreur2")

        self.ImgCover = self.findChild(QLabel, "ImgCover")
        self.Labeltitre = self.findChild(QLabel, "Label_Titre")
        self.LabelDate = self.findChild(QLabel, "Label_Date")
        self.LabelFavorie = self.findChild(QLabel, "Label_Favorie")
        self.LabelPage = self.findChild(QLabel, "Label_Page")

        self.buttonPath.clicked.connect(self.ChoosePath)
        self.ButtonPreview.clicked.connect(self.SelectDoujhin)
        self.ButtonDl.clicked.connect(self.MultiProcesing)

        self.show()

    def SelectDoujhin(self):

        self.erreur.setText(f"")
        self.erreur2.setText(f"")

        SauceInput = self.LabelNum.text()
        URLsite = self.ComboBox.currentText()

        if URLsite == "3hentai":
            URLsite = "https://3hentai.net/d/"

        if URLsite == "Nhentai":
            URLsite = "https://nhentai.net/g/"


        url = URLsite + SauceInput
        TestSauce = requests.get(url)
        if not TestSauce.status_code == 200:
            self.erreur.setText(f"Error : Can't find the Sauce")
            self.erreur.setStyleSheet("color: rgb(255, 255, 255); font-family: ARIAL; font-size: 12px;")
            return

        global URLtoDownload
        URLtoDownload.clear()

        r = requests.get(url)

        Image = BeautifulSoup( r.text, "html.parser" )
        for CumComming in Image.find_all("noscript"):

            if not CumComming.findChildren("img"):
                continue
            url = CumComming.findChildren("img")[0].get("src")

            if not url.endswith(".jpg") or url.endswith(".png"):
                continue

            if "t" in url:
                url = url.replace( "t.jpg", ".jpg" )

            if not "thumb" in url:
                if not url.endswith( "cover.jpg" ):
                    m = re.search( r".*\/(.*)\/(.+).jpg", url )
                    URLtoDownload.append( ( m.group( 1 ) + "/" + m.group( 2 ) + ".jpg", url ) )
                else:
                    m = re.search( r".*\/(.*)\/(.+).jpg", url )
                    URLtoDownload.append( ( m.group( 1 ) + "/" + "cover.jpg", url ) )

        print( URLtoDownload )

        if URLsite == "https://3hentai.net/d/":
            for CumComming in Image.find_all("h1"):
                Title = CumComming.findChildren("span")[0].text
                print(Title)

                # Label Titre
                self.Labeltitre.setText(f"Title : " + Title)
                self.Labeltitre.setStyleSheet("color: rgb(255, 255, 255); font-family: ARIAL; font-size: 12px;")


        if URLsite == "https://nhentai.net/g/":
            strData = r.text.split( "window._gallery = JSON.parse(\"" )[1].split( '");' )[0]

            if not strData:
                return False

            strData = strData.replace( "\\u0022", '"' )

            data = json.loads( strData )

            if not data:
                return False

            title       = data[ "title" ][ "english" ]
            uploaded    = data[ "upload_date" ]
            favorites   = data[ "num_favorites" ]
            pages       = data[ "num_pages" ]
            print("Titre : " + title)
            print("Date Upload  :" + uploaded)
            print("Nb favorite : " + favorites)
            print("Nb page : " + pages)


            self.Labeltitre.setText(f"Title : " + title)

            self.Labeltitre.setText(f"Date Upload : " + uploaded )

            self.Labeltitre.setText(f"Favorite : " + favorites)

            self.Labeltitre.setText(f"Nb Page : " + pages)

        path, url = URLtoDownload[ 0 ]

        image = QImage()
        image.loadFromData( requests.get( url ).content )

        ImgResize = image.scaled(180,220)
        self.ImgCover.setPixmap(QPixmap(ImgResize))

    def DlDoujhin( self, URI ):

        path, URL = URI

        response = requests.get( URL )

        if response.status_code == 200:
            Path( folder_path + "/" + re.search( r"(.+)\/", path ).group( 1 ) ).mkdir( parents=True, exist_ok=True )

            with open( folder_path + "/" + path, "wb") as f:
                f.write( response.content )



    def MultiProcesing(self):

        if len( URLtoDownload ) == 0:
            self.erreur2.setText(f"You don't have select the sauce")
            self.erreur2.setStyleSheet("color: rgb(255, 255, 255); font-family: ARIAL; font-size: 12px;")


        results = ThreadPool( 40 ).imap_unordered( self.DlDoujhin, URLtoDownload )



        for response in results:
            print(response)

        URLtoDownload.clear()


    def ChoosePath(self):
        global folder_path
        filename = QFileDialog.getExistingDirectory(self, "Open file", "./")
        folder_path = filename

        self.labelSauce.setText(f"Path : " + filename)
        self.labelSauce.setStyleSheet("color: rgb(255, 255, 255); font-family: Tahoma; font-size: 12px;")


folder_path = "./"
URLtoDownload = []


app = QApplication(sys.argv)
UIWindow = UI()
sys.exit(app.exec())