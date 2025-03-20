import os
import zipfile
from datetime import datetime
import threading
import schedule
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import psutil

# Variáveis globais
source_dir = None
backup_zip_dir = None
backup_time = None
backup_status = "Aguardando configuração..."
status_label = None
progress_bar = None
painel = None
cpu_label = None
mem_label = None

def atualizar_monitoramento():
    """Atualiza o uso de CPU e memória na interface gráfica."""
    if cpu_label and mem_label:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()

        cpu_label.config(text=f"Uso da CPU: {cpu_usage}%", fg="red" if cpu_usage > 80 else "black")
        mem_label.config(text=f"Uso da Memória: {memory_info.percent}%", fg="red" if memory_info.percent > 90 else "black")

    painel.after(1000, atualizar_monitoramento)  # Atualiza a cada 1 segundo

def abrir_painel_status():
    global status_label, progress_bar, painel, cpu_label, mem_label

    painel = tk.Toplevel()
    painel.title("Status do Backup")
    painel.geometry("400x250")

    status_label = tk.Label(painel, text=backup_status, font=("Arial", 12))
    status_label.pack(pady=10)

    progress_bar = ttk.Progressbar(painel, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)

    cpu_label = tk.Label(painel, text="Uso da CPU: 0%", font=("Arial", 10))
    cpu_label.pack()

    mem_label = tk.Label(painel, text="Uso da Memória: 0%", font=("Arial", 10))
    mem_label.pack()

    atualizar_monitoramento()

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
    abrir_painel_status()

def iniciar_backup():
    if not source_dir or not backup_zip_dir:
        messagebox.showerror("Erro", "Configure os diretórios primeiro!")
        return
    abrir_painel_status()
    threading.Thread(target=realizar_backup, daemon=True).start()

def realizar_backup():
    global backup_status
    atualizar_status("Backup em andamento...")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_zip_path = os.path.join(backup_zip_dir, f"backup_{timestamp}.zip")
    os.makedirs(backup_zip_dir, exist_ok=True)

    files_to_backup = [os.path.join(root, file) for root, _, files in os.walk(source_dir) for file in files]
    total_files = len(files_to_backup)

    progress_bar.config(maximum=total_files)
    progress_bar["value"] = 0

    with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, file_path in enumerate(files_to_backup):
            zipf.write(file_path, os.path.relpath(file_path, source_dir))
            progress_bar["value"] = (i + 1)
            status_label.config(text=f"Processando {i+1}/{total_files} arquivos...")
            status_label.update()

    manter_apenas_tres_backups()
    salvar_log(f"Backup concluído: {backup_zip_path}")
    atualizar_status("Backup concluído com sucesso!")
    painel.after(5000, resetar_interface)

def resetar_interface():
    progress_bar["value"] = 0
    atualizar_status(f"Backup agendado para {backup_time}")

def atualizar_status(novo_status):
    if status_label:
        status_label.config(text=novo_status)
        status_label.update()

def manter_apenas_tres_backups():
    backup_files = sorted(
        [f for f in os.listdir(backup_zip_dir) if f.endswith(".zip")],
        key=lambda x: os.path.getmtime(os.path.join(backup_zip_dir, x)),
        reverse=True
    )
    while len(backup_files) > 3:
        os.remove(os.path.join(backup_zip_dir, backup_files.pop()))

def salvar_log(mensagem):
    log_path = os.path.join(backup_zip_dir, "backup_log.txt")
    with open(log_path, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {mensagem}\n")

def executar_agendador():
    while True:
        schedule.run_pending()
        time.sleep(60)

def abrir_painel_configuracao():
    global painel, origem_entry, destino_entry, horario_entry
    painel = tk.Toplevel()
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

# Criando a janela principal
root = tk.Tk()
root.withdraw()
abrir_painel_configuracao()
root.mainloop()