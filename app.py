from flask import Flask, render_template, jsonify
import os
import zipfile
from datetime import datetime
import threading
import schedule
import time

app = Flask(__name__)

# Diretórios de origem e destino
source_dir = r"C:\REBOCOPY\DISCK 1"
backup_zip_dir = r"C:\REBOCOPY\DISCK 2\backups"

# Criar diretório de backups ZIP se não existir
os.makedirs(backup_zip_dir, exist_ok=True)

def realizar_backup():
    """ Função que compacta diretamente os arquivos sem copiá-los """
    print(f"[{datetime.now()}] 🔹 Iniciando backup...")

    # Criar um nome único para o backup com data e hora
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_zip_path = os.path.join(backup_zip_dir, f"backup_{timestamp}.zip")

    # Garantir que o diretório de backup existe
    os.makedirs(backup_zip_dir, exist_ok=True)

    # Compactar apenas os arquivos do DISCK 1
    with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, source_dir))

    print(f"[{datetime.now()}] ✅ Backup concluído e salvo em {backup_zip_path}")

    # Manter apenas os 3 backups mais recentes
    backup_files = sorted(
        [f for f in os.listdir(backup_zip_dir) if f.endswith(".zip")],
        key=lambda x: os.path.getmtime(os.path.join(backup_zip_dir, x)),
        reverse=True
    )

    while len(backup_files) > 3:
        old_backup = os.path.join(backup_zip_dir, backup_files.pop())
        os.remove(old_backup)
        print(f"[{datetime.now()}] 🗑 Backup antigo removido: {old_backup}")

    print(f"[{datetime.now()}] 🎯 Processo de backup finalizado!\n")

# Agendar o backup para rodar todos os dias às 14h
schedule.every().day.at("21:00").do(realizar_backup)

print("✅ Agendamento configurado. O script ficará rodando em segundo plano...")

# Loop infinito para manter o script rodando
while True:
    schedule.run_pending()
    time.sleep(60)  # Verifica a cada minuto

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
