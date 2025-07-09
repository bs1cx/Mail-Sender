import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import pandas as pd
from datetime import datetime

class SecureEmailSender:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Email Bot v4.0")
        self.root.geometry("900x750")
        
        # SMTP Configuration (Gmail with App Password)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465  # SSL port
        
        self.create_widgets()
        self.attachments = []
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Sender Frame
        sender_frame = ttk.LabelFrame(main_frame, text="Gönderici Bilgileri (Gmail with App Password)")
        sender_frame.pack(fill="x", pady=10)
        
        ttk.Label(sender_frame, text="Gmail Adresiniz:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.sender_email = ttk.Entry(sender_frame, width=40)
        self.sender_email.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(sender_frame, text="App Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.app_password = ttk.Entry(sender_frame, width=40, show="*")
        self.app_password.grid(row=1, column=1, padx=5, pady=5)
        
        # Email Content
        content_frame = ttk.LabelFrame(main_frame, text="E-posta İçeriği")
        content_frame.pack(fill="x", pady=10)
        
        ttk.Label(content_frame, text="Konu:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.subject = ttk.Entry(content_frame, width=60)
        self.subject.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        
        ttk.Label(content_frame, text="Mesaj:").grid(row=1, column=0, padx=5, pady=5, sticky="nw")
        self.body = tk.Text(content_frame, width=60, height=10)
        self.body.grid(row=1, column=1, padx=5, pady=5, columnspan=2)
        
        # Attachments
        attach_frame = ttk.LabelFrame(main_frame, text="Ekler")
        attach_frame.pack(fill="x", pady=10)
        
        self.attachment_list = tk.Listbox(attach_frame, height=4)
        self.attachment_list.pack(fill="x", padx=5, pady=5)
        
        btn_frame = ttk.Frame(attach_frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Dosya Ekle", command=self.add_attachment).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eki Kaldır", command=self.remove_attachment).pack(side="left", padx=5)
        
        # Recipients
        recipient_frame = ttk.LabelFrame(main_frame, text="Alıcı Listesi")
        recipient_frame.pack(fill="both", expand=True, pady=10)
        
        ttk.Button(recipient_frame, text="Excel Yükle", command=self.load_recipients).pack(pady=5)
        
        self.recipient_tree = ttk.Treeview(recipient_frame, columns=("Email", "Name"), show="headings")
        self.recipient_tree.heading("Email", text="E-posta")
        self.recipient_tree.heading("Name", text="Ad")
        self.recipient_tree.pack(fill="both", expand=True)
        
        # Send Button
        ttk.Button(main_frame, text="Güvenli Gönderim Yap (SSL)", command=self.send_emails).pack(pady=15)
        
        # Status
        self.status = ttk.Label(main_frame, text="Hazır")
        self.status.pack()
    
    def add_attachment(self):
        files = filedialog.askopenfilenames()
        for file in files:
            self.attachments.append(file)
            self.attachment_list.insert(tk.END, os.path.basename(file))
    
    def remove_attachment(self):
        selection = self.attachment_list.curselection()
        if selection:
            self.attachments.pop(selection[0])
            self.attachment_list.delete(selection[0])
    
    def load_recipients(self):
        file = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if file:
            try:
                df = pd.read_excel(file)
                self.recipient_tree.delete(*self.recipient_tree.get_children())
                
                for _, row in df.iterrows():
                    self.recipient_tree.insert("", tk.END, values=(row[0], row[1] if len(row) > 1 else ""))
                
                self.status.config(text=f"{len(df)} alıcı yüklendi")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya okunamadı: {e}")
    
    def send_emails(self):
        sender = self.sender_email.get()
        password = self.app_password.get()
        
        if not sender or not password:
            messagebox.showerror("Hata", "Gönderici bilgileri eksik!")
            return
        
        try:
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(sender, password)
            
            total = len(self.recipient_tree.get_children())
            success = 0
            
            for item in self.recipient_tree.get_children():
                recipient, name = self.recipient_tree.item(item)['values']
                
                msg = MIMEMultipart()
                msg['From'] = sender
                msg['To'] = recipient
                msg['Subject'] = self.subject.get()
                
                # Personalize message
                body = self.body.get("1.0", tk.END).replace("{name}", name)
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
                
                # Add attachments
                for file in self.attachments:
                    with open(file, "rb") as f:
                        part = MIMEApplication(f.read(), Name=os.path.basename(file))
                        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file)}"'
                        msg.attach(part)
                
                server.sendmail(sender, recipient, msg.as_string())
                success += 1
                self.status.config(text=f"Gönderiliyor... {success}/{total}")
                self.root.update()
            
            server.quit()
            messagebox.showinfo("Başarılı", f"{success}/{total} e-posta gönderildi")
            self.status.config(text="Gönderim tamamlandı")
            
        except Exception as e:
            messagebox.showerror("SMTP Hatası", f"Gönderim başarısız:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SecureEmailSender(root)
    root.mainloop()