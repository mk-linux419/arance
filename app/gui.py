# Third-Party Library
import gi

# Gtk Library
gi.require_versions({"Gtk": "3.0", "WebKit2": "4.0"})
from gi.repository import Gtk, WebKit2

class WebRenderer(Gtk.Window):
    def __init__(self, url):
        super().__init__()
        self.connect("destroy", Gtk.main_quit)

        Web = WebKit2.WebView()
        Web.load_uri(url)

        self.add(Web)
        self.show_all()

def open(url):
    WebRenderer(url)
    Gtk.main()
