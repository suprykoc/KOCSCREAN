import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import pyautogui
import threading
import time
import numpy as np


class EkranKaydediciUygulama:
    def __init__(self, root):
        self.root = root
        self.root.title("Ekran Kaydedici")
        self.root.geometry("400x500")  # Daha kompakt boyut
        self.root.resizable(False, False)
        self.root.configure(bg="#121212")  # Minimalist koyu arka plan

        # Durum değişkenleri
        self.kayit_durumu = False
        self.dosya_adi = ""
        self.webcam_acik = False

        # Başlık ve logo
        self.baslik_frame = tk.Frame(self.root, bg="#121212")
        self.baslik_frame.pack(pady=20)

        self.logo = tk.Label(
            self.baslik_frame,
            text="🎥",  # Logo emojisi
            font=("Segoe UI", 50),
            bg="#121212",
            fg="#FFD700",  # Altın renk
        )
        self.logo.pack()

        self.baslik = tk.Label(
            self.baslik_frame,
            text="Ekran Kaydedici",
            font=("Segoe UI", 18, "bold"),
            bg="#121212",
            fg="#FFFFFF",
        )
        self.baslik.pack()

        # Buton çerçevesi
        self.buton_cerceve = tk.Frame(self.root, bg="#121212")
        self.buton_cerceve.pack(pady=20)

        # Butonlar
        self.baslat_buton = self.buton_olustur("▶  Kaydı Başlat", self.kaydi_baslat, "#4CAF50")
        self.durdur_buton = self.buton_olustur("⏸  Kaydı Durdur", self.kaydi_durdur, "#FF9800", "disabled")
        self.bitir_buton = self.buton_olustur("✅  Kaydı Bitir", self.kaydi_bitir, "#2196F3", "disabled")
        self.webcam_buton = self.buton_olustur("📸  Webcam Aç/Kapat", self.webcam_toggle, "#F44336")

        # Butonları yerleştir
        self.baslat_buton.pack(pady=10, fill="x", padx=40)
        self.durdur_buton.pack(pady=10, fill="x", padx=40)
        self.bitir_buton.pack(pady=10, fill="x", padx=40)
        self.webcam_buton.pack(pady=10, fill="x", padx=40)

        # Video kaydedici
        self.video_writer = None
        self.ekran_thread = None
        self.webcam = None

    def buton_olustur(self, text, command, color, state="normal"):
        """Modern tasarımlı buton."""
        button = tk.Button(
            self.buton_cerceve,
            text=text,
            command=command,
            height=2,  # Modern oran
            bg=color,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            state=state,
            cursor="hand2",
            activebackground="#444444",
            activeforeground="white",
            bd=0,  # Çerçevesiz
        )
        # Hover efekti
        button.bind("<Enter>", lambda e: button.config(bg=self.renk_acik(color)))
        button.bind("<Leave>", lambda e: button.config(bg=color))
        return button

    @staticmethod
    def renk_acik(renk):
        """Renk tonunu hafif açar."""
        renk = renk.lstrip("#")
        rgb = tuple(int(renk[i:i + 2], 16) for i in (0, 2, 4))
        yeni_rgb = tuple(min(255, int(c * 1.2)) for c in rgb)
        return f"#{yeni_rgb[0]:02X}{yeni_rgb[1]:02X}{yeni_rgb[2]:02X}"

    def webcam_toggle(self):
        """Webcam aç/kapat."""
        if self.webcam_acik:
            self.webcam_durdur()
        else:
            self.webcam_baslat()

    def webcam_baslat(self):
        """Webcam başlatma."""
        self.webcam = cv2.VideoCapture(0)
        if not self.webcam.isOpened():
            messagebox.showerror("Hata", "Webcam açılamadı!")
            return

        self.webcam_acik = True
        self.webcam_buton.config(text="❌  Webcam Kapat")
        while self.webcam_acik:
            ret, frame = self.webcam.read()
            if not ret:
                break
            cv2.imshow("Webcam", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    def webcam_durdur(self):
        """Webcam durdurma."""
        self.webcam_acik = False
        if self.webcam:
            self.webcam.release()
        cv2.destroyAllWindows()
        self.webcam_buton.config(text="📸  Webcam Aç/Kapat")

    def kaydi_baslat(self):
        """Ekran kaydını başlatma."""
        dosya_yolu = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("AVI dosyaları", "*.avi")])
        if not dosya_yolu:
            messagebox.showwarning("Hata", "Lütfen geçerli bir dosya yolu seçin.")
            return

        self.kayit_durumu = True
        self.dosya_adi = dosya_yolu
        self.baslat_buton.config(state="disabled")
        self.durdur_buton.config(state="normal")
        self.bitir_buton.config(state="normal")

        ekran_boyutu = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.video_writer = cv2.VideoWriter(self.dosya_adi, fourcc, 20.0, ekran_boyutu)

        self.ekran_thread = threading.Thread(target=self.ekran_yakala)
        self.ekran_thread.start()

    def ekran_yakala(self):
        """Ekranı yakala."""
        while self.kayit_durumu:
            ekran_goruntusu = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(ekran_goruntusu), cv2.COLOR_RGB2BGR)
            self.video_writer.write(frame)
            time.sleep(0.05)

    def kaydi_durdur(self):
        """Kaydı durdur."""
        self.kayit_durumu = False
        self.baslat_buton.config(state="normal")
        self.durdur_buton.config(state="disabled")

        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

    def kaydi_bitir(self):
        """Kaydı bitir ve kaydet."""
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            messagebox.showinfo("Başarılı", f"Kayıt başarıyla kaydedildi: {self.dosya_adi}")
        else:
            messagebox.showwarning("Hata", "Kayıt kaydedilemedi.")

        self.bitir_buton.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = EkranKaydediciUygulama(root)
    root.mainloop()
