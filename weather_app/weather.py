import tkinter as tk
from tkinter import tkk, messagebox
import requests
# from datetime import datetime
import threading
from PIL import Image, ImageTk
import io
import urllib,requests

# API CONFIGURE:
apiKey = "4780165e19fc8f6720e66f953c6746a8"
baseURL = "https://api.openweathermap.org/data/2.5"
iconURL = "https://openweathermap.org/img/wn/{}@2x.png"


Colors = {
    "bg_color" :'#66cdaa',
    "bg_color2" : "#165a43",
    "bg_cardOptions" : '#458b00',
    "searchButton": '#66cd00',
    "textBlack": "#000000",
    "textInside": '#ffc125',
    "success"     : "#64ffda",
    "warning"     : "#ffd700",
    "card_border" : "#1e4080",
}

FONTS = {
    "title"   : ("Helvetica", 28, "bold"),
    "subtitle": ("Helvetica", 14),
    "heading" : ("Helvetica", 16, "bold"),
    "body"    : ("Helvetica", 12),
    "small"   : ("Helvetica", 10),
    "temp"    : ("Helvetica", 48, "bold"),
    "large"   : ("Helvetica", 20, "bold"),
}