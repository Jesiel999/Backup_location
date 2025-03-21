import os
import zipfile
from datetime import datetime, timedelta
import threading
import schedule
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import psutil
import customtkinter as ctk
import re


source_dir = None
backup_zip_dir = None
backup_time = None
backup_status = "Aguardando configuração..."
status_label = None
progress_bar = None
painel = None
cpu_label = None
mem_label = None
backup_pid = None 

def atualizar_monitoramento():
    """Atualiza o uso de CPU e memória do processo do backup na interface."""
    global backup_pid

    if backup_pid:
        try:
            processo = psutil.Process(backup_pid)
            uso_cpu = processo.cpu_percent(interval=1)
            uso_memoria = processo.memory_info().rss / (1024 * 1024) 

            cpu_label.config(text=f"CPU : {uso_cpu:.2f}%", fg="red" if uso_cpu > 80 else "black")
            mem_label.config(text=f"Memória : {uso_memoria:.2f} MB", fg="red" if uso_memoria > 500 else "black")

        except psutil.NoSuchProcess:
            cpu_label.config(text="CPU : N/A", fg="black")
            mem_label.config(text="Memória : N/A", fg="black")
            backup_pid = None 

    painel.after(1000, atualizar_monitoramento) 

def abrir_painel_status():
    global status_label, progress_bar, progress_label, painel, cpu_label, mem_label

    painel = tk.Toplevel()
    # painel.iconbitmap('assents/memory-card.png') #alterar
    painel.title("Backup")
    painel.configure(bg="#f0f0f0")

    largura_tela = painel.winfo_screenwidth()
    altura_tela = painel.winfo_screenheight()
    largura_painel = 230
    altura_painel = 550
    x_pos = largura_tela - largura_painel - 10 
    y_pos = altura_tela - altura_painel - 50  
    painel.geometry(f"{largura_painel}x{altura_painel}+{x_pos}+{y_pos}")

    status_label = tk.Label(painel, text=backup_status, font=("Arial", 12), bg="#f0f0f0")
    status_label.pack(pady=10)

    progress_bar = ttk.Progressbar(painel, orient="vertical", length=400, mode="determinate")
    progress_bar.pack(pady=10, fill='y', expand=True)
    
    progress_label = tk.Label(painel, text="0%", font=("Arial", 10), bg="#f0f0f0")
    progress_label.pack()

    cpu_label = tk.Label(painel, text="Uso da CPU: 0%", font=("Arial", 10), bg="#f0f0f0")
    cpu_label.pack()

    mem_label = tk.Label(painel, text="Uso da Memória: 0%", font=("Arial", 10), bg="#f0f0f0")
    mem_label.pack()

    atualizar_monitoramento()
    
def atualizar_progresso(valor, total):
    percentual = int((valor / total) * 100)
    progress_bar["value"] += 1
    progress_label.config(text=f"{percentual}%")
    progress_label.update()
    painel.update_idletasks()


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
    backup_time = horario_entry.get().strip()

    if not source_dir or not backup_zip_dir or not backup_time:
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos!")
        return

    # Validação do formato do horário (HH:MM)
    if not re.match(r'^\d{2}:\d{2}$', backup_time):
        messagebox.showerror("Erro", "Formato do horário inválido! Use HH:MM")
        return

    os.makedirs(backup_zip_dir, exist_ok=True)
    schedule.clear()
    schedule.every().day.at(backup_time).do(realizar_backup)

    backup_status = f"Backup agendado: {backup_time}!"
    messagebox.showinfo("Sucesso", backup_status)
    abrir_painel_status()

    # Garante que o agendador está rodando
    threading.Thread(target=executar_agendador, daemon=True).start()

from datetime import datetime, timedelta

def iniciar_backup():
    global backup_time

    if not source_dir or not backup_zip_dir:
        messagebox.showerror("Erro", "Configure os diretórios primeiro!")
        return

    abrir_painel_status()
    threading.Thread(target=realizar_backup, daemon=True).start()

    now = datetime.now()
    backup_time = now.strftime("%H:%M")  

    schedule.clear()
    schedule.every().day.at(backup_time).do(realizar_backup)
    salvar_log(f"Próximo backup agendado: {backup_time} ")

def realizar_backup():
    global backup_status, backup_pid
    backup_pid = os.getpid()  

    atualizar_status("Backup em andamento...")
    status_label.config(text=backup_status)
    status_label.update()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_zip_path = os.path.join(backup_zip_dir, f"backup_{timestamp}.zip")
    os.makedirs(backup_zip_dir, exist_ok=True)

    files_to_backup = [os.path.join(root, file) for root, _, files in os.walk(source_dir) for file in files]
    total_files = len(files_to_backup)

    progress_bar["value"] = 0 
    progress_bar.config(maximum=total_files)

    with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, file_path in enumerate(files_to_backup):
            zipf.write(file_path, os.path.relpath(file_path, source_dir))
            progress_bar["value"] = (i + 1)
            status_label.config(text=f"{i+1}/{total_files}")
            status_label.update()
            atualizar_progresso(i + 1, total_files)
            painel.update_idletasks()  

    manter_apenas_tres_backups()
    salvar_log(f"Backup concluído: {backup_zip_path}")
    atualizar_status("Backup concluído!")
    painel.after(5000, resetar_interface)
    status_label.config(text=backup_status)
    progress_label.config(text="100%")
    progress_bar["value"] = 5000

    painel.after(5000, painel.destroy) 
    
def resetar_interface():
    # painel.iconbitmap('assents/memory-card.png') #alterar
    progress_bar["value"] = 0
    atualizar_status(f"Backup agendado: {backup_time}")

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
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(script_dir, "backup_log.txt")  # Caminho do log no mesmo diretório do app.py

    with open(log_path, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {mensagem}\n")

def executar_agendador():
    while True:
        schedule.run_pending()  # Executa tarefas agendadas
        time.sleep(30)  # Reduz a carga na CPU



def abrir_painel_configuracao():
    global painel, origem_entry, destino_entry, horario_entry
    painel = tk.Toplevel()
    # painel.iconbitmap('assents/memory-card.png') #alterar
    painel.title("BACKUP")
    painel.geometry("300x370")
    painel.configure(bg="#ffffff")

    tk.Label(painel, text="Diretório de Origem:", bg="#ffffff", font=("Arial", 10, "bold"), fg="#333333").pack(pady=(10, 2))
    origem_entry = ctk.CTkEntry(painel, width=200, font=("Arial", 10), fg_color="#f8f8f8", text_color="#333333",
                                corner_radius=10, border_width=2, border_color="#cccccc")
    origem_entry.pack(pady=5)
    ctk.CTkButton(painel, text="Selecionar", command=selecionar_origem, fg_color="#303030", 
                  text_color="white", corner_radius=10).pack(pady=2)

    tk.Label(painel, text="Diretório de Destino:", bg="#ffffff", font=("Arial", 10, "bold"), fg="#333333").pack(pady=(10, 2))
    destino_entry = ctk.CTkEntry(painel, width=200, font=("Arial", 10), fg_color="#f8f8f8", text_color="#333333",
                                 corner_radius=10, border_width=2, border_color="#cccccc")
    destino_entry.pack(pady=5)
    ctk.CTkButton(painel, text="Selecionar", command=selecionar_destino, fg_color="#303030", 
                  text_color="white", corner_radius=10).pack(pady=2)

    tk.Label(painel, text="Horário do Backup (HH:MM):", bg="#ffffff", font=("Arial", 10, "bold"), fg="#333333").pack(pady=(10, 2))
    horario_entry = ctk.CTkEntry(painel, width=100, font=("Arial", 10), fg_color="#f8f8f8", text_color="#333333",
                                 corner_radius=10, border_width=2, border_color="#cccccc")
    horario_entry.pack(pady=5)

    ctk.CTkButton(painel, text="Configurar Backup", command=configurar_backup, fg_color="#000000", 
                  text_color="white", corner_radius=10).pack(pady=5)
    ctk.CTkButton(painel, text="Iniciar Backup Agora", command=iniciar_backup, fg_color="#000000", 
                  text_color="white", corner_radius=10).pack(pady=5)


root = tk.Tk()
root.withdraw()
abrir_painel_configuracao()
root.mainloop()
