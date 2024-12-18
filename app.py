import sys
import logging
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSystemTrayIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage

class WhatsAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WhatsApp Web")
        self.setGeometry(100, 100, 1400, 900)

        # Set up logger
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        # Create the Web Engine View
        self.browser = QWebEngineView()

        # Custom user agent and profile settings
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/90.0.4430.212 Safari/537.36"
        )

        # Load WhatsApp Web
        self.browser.setUrl(QUrl("https://web.whatsapp.com/"))

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect load finished signal
        self.browser.loadFinished.connect(self.on_load_finished)

        # Setup desktop notifications
        self.setup_notifications()

    def setup_notifications(self):
        """Setup desktop notification mechanism"""
        # Enable notifications in WebEngine
        self.browser.page().featurePermissionRequested.connect(self.permission_requested)

    def permission_requested(self, url, feature):
        """Handle permission requests"""
        if feature == QWebEnginePage.Notifications:
            self.browser.page().setFeaturePermission(
                url, 
                feature, 
                QWebEnginePage.PermissionGrantedByUser
            )

    def on_load_finished(self, ok):
        """Handle page load and start notification listener"""
        if ok:
            self.logger.info("WhatsApp Web loaded")
            # Inject notification listener
            self.inject_notification_listener()
        else:
            self.logger.error("Failed to load WhatsApp Web")

    def inject_notification_listener(self):
        """Inject JavaScript to listen for new messages and trigger desktop notifications"""
        notification_script = """
        // Function to send message to PyQt application
        function sendNotificationToPyQt(title, body) {
            window.pyqt_bridge.notify(title, body);
        }

        // Observe new message notifications
        function observeNewMessages() {
            const chatListSelector = '._3q9s-';
            const unreadSelector = '._1pJ9J';
            
            const chatList = document.querySelector(chatListSelector);
            if (chatList) {
                const unreadBadges = chatList.querySelectorAll(unreadSelector);
                
                unreadBadges.forEach(badge => {
                    const chatItem = badge.closest('._2WP9Q');
                    if (chatItem) {
                        const chatName = chatItem.querySelector('._2_szb');
                        const lastMessage = chatItem.querySelector('._3LaIj');
                        
                        if (chatName && lastMessage) {
                            sendNotificationToPyQt(
                                chatName.innerText, 
                                lastMessage.innerText
                            );
                        }
                    }
                });
            }
        }

        // Setup MutationObserver to watch for new messages
        const observer = new MutationObserver(observeNewMessages);
        observer.observe(document.body, { 
            childList: true, 
            subtree: true 
        });
        """
        
        # Inject the JavaScript to the page
        self.browser.page().runJavaScript(notification_script)

    def notify(self, title, message):
        """Desktop notification method"""

        # Create system tray icon for notifications
        tray_icon = QSystemTrayIcon(self)
        tray_icon.show()

        # Display notification
        tray_icon.showMessage(
            title,  # Sender's name
            message,  # Message preview
            QSystemTrayIcon.Information,
            3000  # Display duration in milliseconds
        )

def main():
    app = QApplication(sys.argv)
    window = WhatsAppWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
