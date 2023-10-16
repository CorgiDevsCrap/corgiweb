#   imports
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtNetwork import QNetworkAccessManager
from PyQt5 import QtWidgets
from abpy import Filter
import breeze_resources
import os
import sys
import platform 

#   version number
version = "1.41"

#   adblock manager
class MyNetworkAccessManager(QNetworkAccessManager):
    def createRequest(self, op, request, device=None):
        url = request.url().toString()
        doFilter = adblockFilter.match(url)
        if doFilter:
            return QNetworkAccessManager.createRequest(self, self.GetOperation, QNetworkRequest(QUrl()))
        else:
            QNetworkAccessManager.createRequest(self, op, request, device)
            
            myNetworkAccessManager = MyNetworkAccessManager()

#   main app
class MainWindow(QMainWindow):

    #   creates app window
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
 
        #   tabs class
        class initTabs:
            #   set titlebar icon to ir.png
            self.setWindowIcon(QIcon('./assets/icon/ir.png'))
            #   create tabs bar
            self.tabs = QTabWidget()
            #   enable document editing mode
            self.tabs.setDocumentMode(True)
            #   double click on tabs bar to open new tab
            self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
            #   change tabs if pressed on other tab
            self.tabs.currentChanged.connect(self.current_tab_changed)
            #   make tabs closable
            self.tabs.setTabsClosable(True)
            #   makes pressing "X" actually close the tab
            self.tabs.tabCloseRequested.connect(self.close_current_tab)
            #   central the tabs bar
            self.setCentralWidget(self.tabs)
            #   add status bar
            self.status = QStatusBar()
            #   set status bar
            self.setStatusBar(self.status)
 
        #   navtb class
        class initNavTB: 
            #   create navtb bar
            navtb = QToolBar("Navigation")
            #   add navtb bar
            self.addToolBar(Qt.BottomToolBarArea, navtb)
            #   add back button image
            back_btn = QAction(QIcon('./assets/buttons/back.png'), "Back to previous page", self)
            #   make back button work
            back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
            #   add back button to navtb
            navtb.addAction(back_btn)
            #   add forward button image
            next_btn = QAction(QIcon('./assets/buttons/forward.png'), "Forward to next page", self)
            #   make forward button work
            next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
            #   add forward button to navtb
            navtb.addAction(next_btn)
            #   add reload button image
            reload_btn = QAction(QIcon('./assets/buttons/reload.png'), "Reload page", self)
            #   make reload button work
            reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
            #   add reload button to navtb
            navtb.addAction(reload_btn)
             #   add home button image
            home_btn = QAction(QIcon('./assets/buttons/home.png'),"Go home", self)
            #   make home button work
            home_btn.triggered.connect(self.navigate_home)
            #   add home button to navtb
            navtb.addAction(home_btn)
            #   add seperator
            navtb.addSeparator()
            #   create url bar
            self.urlbar = QLineEdit()
            #   make url bar work
            self.urlbar.returnPressed.connect(self.navigate_to_url)
            #   add url bar
            navtb.addWidget(self.urlbar)
            #   add stop button image
            stop_btn = QAction(QIcon('./assets/buttons/stop.png'), "Stop loading current page", self)
            #   make stop button work
            stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
            #   add stop button to navtb
            navtb.addAction(stop_btn)
 
        #   set home page to https://librex.zzls.xyz/
        self.add_new_tab(QUrl('https://librex.zzls.xyz/'), 'Homepage')
        #   make browser window show
        self.show()
        #   set window name
        self.setWindowTitle("CorgiWeb " + version)
        #   init classes
        initNavTB()
        initTabs()
 
    #   adding tabs
    def add_new_tab(self, qurl = None, label ="Blank"):
        #   set newtab homepage to https://librex.zzls.xyz/
        if qurl is None:
            qurl = QUrl('https://librex.zzls.xyz/k')
        #   set browser engine to QWebEngineView
        browser = QWebEngineView()
        #   set network manager to the adblock one
        self.qnam = MyNetworkAccessManager()
        #   set useragent
        if os.name == "nt":
            browser.page().profile().setHttpUserAgent("Mozilla/5.0 (" + platform.system() + " " + platform.machine() + "; " + platform.version().split('.')[2] + ") CorgiWeb " + version)
        else:
            print("Other system detected, Skipping custom User-Agent")
        #   set url to default one
        browser.setUrl(qurl)
        #   add new tab by default
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        #   set url changable
        browser.urlChanged.connect(lambda qurl, browser = browser:
                                   self.update_urlbar(qurl, browser))
        #   set url loadable
        browser.loadFinished.connect(lambda _, i = i, browser = browser:
                                     self.tabs.setTabText(i, browser.page().title()))
                                     
    #   make tabs openable by double clicking
    def tab_open_doubleclick(self, i):
        #   check if i != 1 and if is then add new tab
        if i == -1:
            self.add_new_tab()
    #   make tabs changable
    def current_tab_changed(self, i):
        #   setting url
        qurl = self.tabs.currentWidget().url()
        #   updating urlbar
        self.update_urlbar(qurl, self.tabs.currentWidget())
        #   updating title
        self.update_title(self.tabs.currentWidget())
    
    def close_current_tab(self, i):
        #check if i is bigger then 2 or else return
        if self.tabs.count() < 2:
            return
        #   remove tab
        self.tabs.removeTab(i)
    #   update title
    def update_title(self, browser):
        #   idfk
        if browser != self.tabs.currentWidget():
            return
 
        title = self.tabs.currentWidget().page().title()
 
        self.setWindowTitle("% s - CorgiWeb" % title)
    #navigating home
    def navigate_home(self):
        #   sets url to https://librex.zzls.xyz/
        self.tabs.currentWidget().setUrl(QUrl("https://librex.zzls.xyz/"))
    #   navigating to url 
    def navigate_to_url(self):
        #   text in url bar 
        q = QUrl(self.urlbar.text())
        #   automatically add http
        if q.scheme() == "":
            q.setScheme("http")
        #   setting url
        self.tabs.currentWidget().setUrl(q)
    #   updating url bar
    def update_urlbar(self, q, browser = None):
        #   idfk
        if browser != self.tabs.currentWidget():
 
            return
 
        self.urlbar.setText(q.toString())
 
        self.urlbar.setCursorPosition(0)
#   setting app to QApplication
app = QApplication(sys.argv)
#   setting theme
file = QFile(":/dark/stylesheet.qss")
#   making file read only and making sure it knows its text
file.open(QFile.ReadOnly | QFile.Text)
#   adding stream
stream = QTextStream(file)
#   settings stylesheet
app.setStyleSheet(stream.readAll())
#   setting title
app.setApplicationName("CorgiWeb " + version)
#   create window
window = MainWindow()
#   init app
app.exec_()
