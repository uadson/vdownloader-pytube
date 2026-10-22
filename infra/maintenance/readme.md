# Rotinas de Manutenção e Limpeza - vDownloader

Este diretório contém os scripts e serviços systemd para manutenção preventiva do ambiente de containers Docker do vDownloader.

## Conteúdo
- `docker-cleanup.sh`: Script bash responsável por remover containers finalizados, imagens órfãs (dangling), volumes sem uso e arquivos temporários de downloads antigos.
- `docker-cleanup.service`: Definição de unidade do systemd do tipo `oneshot` para executar o script.
- `docker-cleanup.timer`: Timer do systemd agendado para rodar diariamente.

## Como Ativar no Servidor Host (Linux com Systemd)

1. Copie os arquivos de serviço e timer para a pasta do systemd:
   ```bash
   sudo cp infra/maintenance/docker-cleanup.service /etc/systemd/system/
   sudo cp infra/maintenance/docker-cleanup.timer /etc/systemd/system/
   ```

2. Recarregue os daemons do systemd:
   ```bash
   sudo systemctl daemon-reload
   ```

3. Habilite e inicie o timer:
   ```bash
   sudo systemctl enable --now docker-cleanup.timer
   ```

4. Verifique o status da execução:
   ```bash
   systemctl list-timers | grep docker-cleanup
   ```
