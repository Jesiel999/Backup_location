# Backup_location

Backup Automation Tool
Este projeto é uma aplicação em Python que automatiza o processo de backup de dados. O objetivo é detectar a conexão de um HD externo e realizar backups automaticamente ou agendados. A aplicação suporta backups incrementais, copiando apenas arquivos modificados, e compactação em arquivos ZIP. Além disso, mantém as três versões mais recentes do backup.

Funcionalidades
Detecção Automática de HD Externo: Quando um HD externo é conectado, o backup é iniciado automaticamente.
Agendamento de Backup: Permite agendar backups para horários específicos.
Backup Incremental: Apenas arquivos modificados ou novos são copiados, economizando espaço e tempo.
Compactação em ZIP: O backup é compactado em um arquivo ZIP.
Manutenção de Versões: A aplicação mantém as três versões mais recentes do backup, excluindo versões mais antigas.
Pré-requisitos
Antes de rodar o projeto, é necessário ter o Python instalado. Você pode baixá-lo aqui.

Além disso, você deve instalar as dependências necessárias utilizando o pip:


pip install -r requirements.txt
Como Usar
Clonar o repositório:


git clone https://github.com/seu-usuario/backup-automation.git
cd backup-automation
Executar a aplicação:

Para iniciar o processo de backup, execute:


python backup.py
Agendar backups:

Para agendar backups, edite o arquivo config.json com os horários desejados ou use a interface de linha de comando.

Configuração do Backup
A configuração do caminho de origem (HD externo) e do destino do backup é feita no arquivo config.json.


{
   "source_directory": "C:/Path/To/External/Drive",
   "backup_directory": "C:/Path/To/Backup/Location",
   "keep_versions": 3
}
source_directory: Caminho onde os arquivos do HD externo estão localizados.
backup_directory: Caminho onde os backups serão salvos.
keep_versions: Quantidade de versões a manter.
Como Funciona
A aplicação monitora a conexão de dispositivos de armazenamento.
Quando um HD externo é conectado, ela começa a verificar os arquivos e realiza um backup incremental.
O backup é compactado em um arquivo ZIP.
A aplicação mantém no máximo 3 versões mais recentes e apaga as versões mais antigas.
Licença
Este projeto é licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.