import tkinter as tk
from tkinter import scrolledtext
import re
from collections import Counter

# Ana uygulama penceresi oluşturma
root = tk.Tk()
root.title("Mesajlaşma Uygulaması")

# Pencere boyutu ayarlama
root.geometry("400x400")

# Mesaj girişi alanı
entry = tk.Entry(root, width=50)
entry.pack(pady=10)

# Tahmin edilen kelimenin gösterileceği alan
suggestion_label = tk.Label(root, text="", fg="grey")
suggestion_label.pack()

# Mesajları listeleyen alan (scrollable text area)
message_list = scrolledtext.ScrolledText(root, width=50, height=15, state='disabled')
message_list.pack(pady=10)

# Mesaj gönderme işlevi
def send_message():
    message = entry.get()
    if message:
        # Mesajları listeleme alanına ekleme
        message_list.configure(state='normal')
        message_list.insert(tk.END, f"You: {message}\n")
        message_list.configure(state='disabled')
        
        # Mesajı dosyaya kaydetme
        with open("messages.txt", "a") as file:
            file.write(f"You: {message}\n")
        
        # Kelimeleri işleme ve dosyaya kaydetme
        process_words(message)
        
        # Metin giriş alanını temizleme
        entry.delete(0, tk.END)
        suggestion_label.config(text="")

# Geçmiş mesajları yükleme işlevi
def load_messages():
    try:
        with open("messages.txt", "r") as file:
            messages = file.readlines()
            message_list.configure(state='normal')
            for message in messages:
                message_list.insert(tk.END, message)
            message_list.configure(state='disabled')
    except FileNotFoundError:
        # Eğer dosya bulunamazsa, hiçbir şey yapma
        pass

# Kelimeleri işleme ve dosyaya kaydetme işlevi
def process_words(message):
    # Mesajı kelimelere bölme ve kurallara göre filtreleme
    words = re.findall(r'\b\w+\b', message.lower())
    words = [word for word in words if len(word) >= 3]
    
    # Mevcut kelime sayılarını yükleme
    try:
        with open("word_counts.txt", "r") as file:
            lines = file.readlines()
            word_counts = Counter(dict(line.strip().split(': ') for line in lines))
            word_counts = Counter({k: int(v) for k, v in word_counts.items()})
    except FileNotFoundError:
        word_counts = Counter()
    
    # Yeni kelimeleri ekleyerek güncelleme
    word_counts.update(words)
    
    # Kelime sayılarını dosyaya kaydetme
    with open("word_counts.txt", "w") as file:
        for word, count in word_counts.items():
            file.write(f"{word}: {count}\n")

# Tahmin işlevi
def predict_word(event):
    input_text = entry.get()
    if len(input_text) < 3:
        suggestion_label.config(text="")
        return
    
    try:
        with open("word_counts.txt", "r") as file:
            lines = file.readlines()
            word_counts = Counter(dict(line.strip().split(': ') for line in lines))
            word_counts = Counter({k: int(v) for k, v in word_counts.items()})
    except FileNotFoundError:
        word_counts = Counter()
    
    predictions = [word for word in word_counts if word.startswith(input_text.lower())]
    if predictions:
        best_prediction = max(predictions, key=lambda x: word_counts[x])
        suggestion = best_prediction[len(input_text):]
        suggestion_label.config(text=suggestion)
    else:
        suggestion_label.config(text="")

# Tahmini kelimeyi tamamlama işlevi
def complete_prediction(event):
    input_text = entry.get()
    suggestion = suggestion_label.cget("text")
    if suggestion:
        entry.insert(tk.END, suggestion)
        suggestion_label.config(text="")
    return "break"

# Uygulama başladığında geçmiş mesajları yükleme
load_messages()

# Mesaj gönderme butonu
send_button = tk.Button(root, text="Mesaj Gönder", command=send_message)
send_button.pack(pady=10)

# Metin girişine tahmin işlevi ekleme
entry.bind("<KeyRelease>", predict_word)
entry.bind("<Tab>", complete_prediction)

# Ana döngüyü başlatma
root.mainloop()
