import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import ffmpeg
import threading
import json
import os

# تعيين المسار إلى ffmpeg المضمن
ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')

# دالة لاختيار ملفات الإدخال
def select_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("Audio/Video Files", "*.mp3 *.wav *.flac *.m4a *.mp4 *.avi *.mkv *.mov")])
    if file_paths:
        input_listbox.delete(0, tk.END)
        for file_path in file_paths:
            input_listbox.insert(tk.END, file_path)

# دالة لتحويل الملفات الصوتية والفيديو
def convert_files():
    input_files = list(input_listbox.get(0, tk.END))
    output_dir = output_entry.get()
    selected_format = format_var.get()
    audio_bitrate = audio_bitrate_entry.get()
    video_bitrate = video_bitrate_entry.get()
    resolution = resolution_entry.get()

    if not input_files or not output_dir or not selected_format:
        messagebox.showerror("Error", "Please fill all fields")
        return

    if not audio_bitrate:
        audio_bitrate = '320k'

    if not video_bitrate:
        video_bitrate = '1M'  # 1 Megabit as default

    progress_bar['value'] = 0
    progress_bar['maximum'] = len(input_files)

    def perform_conversion():
        for i, input_file in enumerate(input_files):
            output_file = f"{output_dir}/{os.path.basename(input_file).split('.')[0]}.{selected_format}"
            try:
                stream = ffmpeg.input(input_file, cmd=ffmpeg_path)
                if selected_format in ['mp3', 'wav', 'flac', 'm4a']:
                    stream = ffmpeg.output(stream, output_file, audio_bitrate=audio_bitrate)
                else:
                    stream = ffmpeg.output(stream, output_file, video_bitrate=video_bitrate, vf=f'scale={resolution}')
                ffmpeg.run(stream)
                progress_bar['value'] += 1
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return

        messagebox.showinfo("Success", "All files converted successfully")
        save_settings()

    threading.Thread(target=perform_conversion).start()

# دالة لحفظ إعدادات المستخدم
def save_settings():
    settings = {
        "output_dir": output_entry.get(),
        "selected_format": format_var.get(),
        "audio_bitrate": audio_bitrate_entry.get(),
        "video_bitrate": video_bitrate_entry.get(),
        "resolution": resolution_entry.get()
    }
    with open("settings.json", "w") as f:
        json.dump(settings, f)

# دالة لتحميل إعدادات المستخدم
def load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            settings = json.load(f)
        output_entry.insert(0, settings["output_dir"])
        format_var.set(settings["selected_format"])
        audio_bitrate_entry.insert(0, settings["audio_bitrate"])
        video_bitrate_entry.insert(0, settings["video_bitrate"])
        resolution_entry.insert(0, settings["resolution"])

# إعداد واجهة المستخدم
root = tk.Tk()
root.title('Audio/Video Converter')
root.geometry('800x600')
root.configure(bg='#2c3e50')

style = {
    'bg': '#34495e',
    'fg': 'white',
    'font': ('Arial', 12)
}

tk.Label(root, text='Input Files:', **style).grid(row=0, column=0, padx=10, pady=10, sticky='w')
input_listbox = tk.Listbox(root, width=50, height=10, bg='#ecf0f1', fg='#2c3e50')
input_listbox.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text='Browse', command=select_files, bg='#1abc9c', fg='white', font=('Arial', 12)).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text='Output Directory:', **style).grid(row=1, column=0, padx=10, pady=10, sticky='w')
output_entry = tk.Entry(root, width=50, bg='#ecf0f1', fg='#2c3e50')
output_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text='Browse', command=lambda: output_entry.insert(0, filedialog.askdirectory()), bg='#1abc9c', fg='white', font=('Arial', 12)).grid(row=1, column=2, padx=10, pady=10)

tk.Label(root, text='Output Format:', **style).grid(row=2, column=0, padx=10, pady=10, sticky='w')
format_var = tk.StringVar(root)
format_options = ['mp3', 'wav', 'flac', 'm4a', 'mp4', 'avi', 'mkv', 'mov']
format_menu = tk.OptionMenu(root, format_var, *format_options)
format_menu.config(bg='#1abc9c', fg='white', font=('Arial', 12))
format_menu.grid(row=2, column=1, padx=10, pady=10)

tk.Label(root, text='Audio Bitrate (e.g., 320k):', **style).grid(row=3, column=0, padx=10, pady=10, sticky='w')
audio_bitrate_entry = tk.Entry(root, width=50, bg='#ecf0f1', fg='#2c3e50')
audio_bitrate_entry.grid(row=3, column=1, padx=10, pady=10)

tk.Label(root, text='Video Bitrate (e.g., 1M):', **style).grid(row=4, column=0, padx=10, pady=10, sticky='w')
video_bitrate_entry = tk.Entry(root, width=50, bg='#ecf0f1', fg='#2c3e50')
video_bitrate_entry.grid(row=4, column=1, padx=10, pady=10)

tk.Label(root, text='Resolution (e.g., 1920x1080):', **style).grid(row=5, column=0, padx=10, pady=10, sticky='w')
resolution_entry = tk.Entry(root, width=50, bg='#ecf0f1', fg='#2c3e50')
resolution_entry.grid(row=5, column=1, padx=10, pady=10)

tk.Button(root, text='Convert', command=convert_files, bg='#e74c3c', fg='white', font=('Arial', 12)).grid(row=6, column=1, padx=10, pady=20)

tk.Label(root, text='Conversion Progress:', **style).grid(row=7, column=0, padx=10, pady=10, sticky='w')
progress_bar = Progressbar(root, orient='horizontal', length=400, mode='determinate')
progress_bar.grid(row=7, column=1, padx=10, pady=10)

# تحميل إعدادات المستخدم عند بدء التشغيل
load_settings()

root.mainloop()
