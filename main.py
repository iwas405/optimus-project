import threading
import speech_recognition as sr
import google.generativeai as genai
import pyttsx3
import os
from kivy.app import App
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

# --- KOMUTANIN STRATEJİK AYARLARI ---
API_KEY = "AIzaSyC5a0NpmkqFFSYaQVV3AG2V1vJTDVs1OyE" # Gemini API anahtarınızı buraya koyun
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

class OptimusEkran(ModalView):
    def _init_(self, **kwargs):
        super()._init_(**kwargs)
        self.background_color = [0, 0, 0, 1]  # Tamamen Siyah
        self.size_hint = (1, 1)
        self.auto_dismiss = False
        # Beyaz font ile OPTIMUS yazısı
        self.label = Label(
            text="OPTIMUS", 
            font_size='60sp', 
            color=[1, 1, 1, 1], 
            bold=True
        )
        self.add_widget(self.label)

class OptimusAsistan(App):
    def build(self):
        # Uygulama simgesi ve çerçeve ayarları
        Window.borderless = True
        self.overlay = OptimusEkran()
        self.engine = pyttsx3.init()
        
        # Arka planda gizli dinleme timini başlat
        threading.Thread(target=self.pusuda_bekle, daemon=True).start()
        return Label(text="") # Ana ekran boş kalır

    def sesli_cevap(self, metin):
        self.engine.say(metin)
        self.engine.runAndWait()

    def sistem_dosya_tarama(self, komut):
        # Sistem dosyalarına sızma ve analiz yeteneği
        if "dosya" in komut or "sistem" in komut:
            # Android ana depolama dizini
            yol = "/storage/emulated/0/" 
            try:
                dosyalar = os.listdir(yol)
                return f"Komutanım, sistem dizininde {len(dosyalar)} birim tespit ettim. Analiz ediliyor."
            except:
                return "Sistem dosyalarına erişim izni bekleniyor komutanım."
        return None

    def pusuda_bekle(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            while True:
                try:
                    # Gürültü ayarı ve dinleme
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio = r.listen(source)
                    text = r.recognize_google(audio, language="tr-TR").lower()
                    
                    if "optimus" in text:
                        # 1. Ekranı Karart ve Yazıyı Getir
                        Clock.schedule_once(lambda dt: self.overlay.open())
                        
                        # 2. Sistem Dosyası Kontrolü
                        cevap = self.sistem_dosya_tarama(text)
                        
                        # 3. Değilse Gemini Zekasını Kullan
                        if not cevap:
                            response = model.generate_content(text)
                            cevap = response.text
                        
                        # 4. Sesli Bildirim
                        self.sesli_cevap(cevap)
                        
                        # 5. İş