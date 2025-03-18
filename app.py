import os
import zipfile
from datetime import datetime
import threading
import schedule
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Variáveis globais
source_dir = None
backup_zip_dir = None
backup_time = None
backup_status = "Aguardando configuração..."
status_label = None
progress_bar = None
painel = None

def selecionar_origem():
    global source_dir
    source_dir = filedialog.askdirectory()
    origem_entry.delete(0, tk.END)
    origem_entry.insert(0, source_dir)

def selecionar_destino():
    global backup_zip_dir
    backup_zip_dir = filedialog.askdirectory()
    destino_entry.delete(0, tk.END)
    destino_entry.insert(0, backup_zip_dir)

def configurar_backup():
    global backup_time, backup_status, painel
    backup_time = horario_entry.get()
    if not source_dir or not backup_zip_dir or not backup_time:
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos!")
        return
    os.makedirs(backup_zip_dir, exist_ok=True)
    schedule.clear()
    schedule.every().day.at(backup_time).do(realizar_backup)
    backup_status = f"Backup agendado para {backup_time}!"
    messagebox.showinfo("Sucesso", backup_status)
    painel.destroy()
    abrir_painel_status()

def iniciar_backup():
    global painel
    if not source_dir or not backup_zip_dir:
        messagebox.showerror("Erro", "Configure os diretórios primeiro!")
        return
    painel.destroy()
    abrir_painel_status()
    threading.Thread(target=realizar_backup).start()

def realizar_backup():
    global backup_status
    atualizar_status("Backup em andamento...")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_zip_path = os.path.join(backup_zip_dir, f"backup_{timestamp}.zip")
    os.makedirs(backup_zip_dir, exist_ok=True)
    
    files_to_backup = [os.path.join(root, file) for root, _, files in os.walk(source_dir) for file in files]
    total_files = len(files_to_backup)
    
    progress_bar.config(maximum=total_files)
    progress_bar['value'] = 0
    
    with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, file_path in enumerate(files_to_backup):
            zipf.write(file_path, os.path.relpath(file_path, source_dir))
            progress_bar['value'] = (i + 1)
            status_label.config(text=f"Processando {i+1}/{total_files} arquivos...")
            status_label.update()
    
    atualizar_status("Backup concluído com sucesso!")
    manter_apenas_tres_backups()

def atualizar_status(novo_status):
    status_label.config(text=novo_status)
    status_label.update()

def manter_apenas_tres_backups():
    backup_files = sorted(
        [f for f in os.listdir(backup_zip_dir) if f.endswith(".zip")],
        key=lambda x: os.path.getmtime(os.path.join(backup_zip_dir, x)),
        reverse=True
    )
    while len(backup_files) > 3:
        old_backup = os.path.join(backup_zip_dir, backup_files.pop())
        os.remove(old_backup)

def executar_agendador():
    while True:
        schedule.run_pending()
        time.sleep(60)

def abrir_painel_status():
    global status_label, progress_bar, painel
    painel = tk.Tk()
    painel.title("Status do Backup")
    painel.geometry("400x200")
    status_label = tk.Label(painel, text=backup_status, font=("Arial", 12))
    status_label.pack(pady=10)
    progress_bar = ttk.Progressbar(painel, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)
    painel.mainloop()

def abrir_painel_configuracao():
    global painel, origem_entry, destino_entry, horario_entry
    painel = tk.Tk()
    painel.title("Painel de Backup")
    painel.geometry("400x300")
    
    tk.Label(painel, text="Diretório de Origem:").pack()
    origem_entry = tk.Entry(painel, width=50)
    origem_entry.pack()
    tk.Button(painel, text="Selecionar", command=selecionar_origem).pack()
    
    tk.Label(painel, text="Diretório de Destino:").pack()
    destino_entry = tk.Entry(painel, width=50)
    destino_entry.pack()
    tk.Button(painel, text="Selecionar", command=selecionar_destino).pack()
    
    tk.Label(painel, text="Horário do Backup (HH:MM):").pack()
    horario_entry = tk.Entry(painel, width=10)
    horario_entry.pack()
    
    tk.Button(painel, text="Configurar Backup", command=configurar_backup).pack()
    tk.Button(painel, text="Iniciar Backup Agora", command=iniciar_backup).pack()
    
    threading.Thread(target=executar_agendador, daemon=True).start()
    painel.mainloop()

abrir_painel_configuracao()
