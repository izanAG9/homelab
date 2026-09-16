#!/bin/bash

BACKUP_DIR="$HOME/homelab/docker/minecraft-forge/backups"
WORLD_DIR="$HOME/homelab/docker/minecraft-forge/data/world"
DATE=$(date +%Y-%m-%d_%H-%M-%S)

mkdir -p "$BACKUP_DIR"

docker exec minecraft-forge rcon-cli "say §6[BACKUP] §eGuardando el mundo..."

docker exec minecraft-forge rcon-cli save-all flush

tar -czf "$BACKUP_DIR/world-$DATE.tar.gz" -C "$WORLD_DIR" .

find "$BACKUP_DIR" -type f -name "world-*.tar.gz" -mtime +3 -delete

echo "Backup created: $BACKUP_DIR/world-$DATE.tar.gz"
echo "Old backups (>3 days) removed."

docker exec minecraft-forge rcon-cli "say §a[BACKUP] §fBackup completado correctamente."
