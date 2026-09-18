#!/bin/bash

CONTAINER="minecraft-forge"
STATE_FILE="$HOME/homelab/docker/minecraft-forge/.empty_since"
EMPTY_MINUTES=10

# Si Minecraft no está encendido, no hacemos nada
if [ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null)" != "true" ]; then
    rm -f "$STATE_FILE"
    exit 0
fi

# Consultar jugadores mediante RCON
PLAYERS=$(docker exec "$CONTAINER" rcon-cli list 2>/dev/null | grep -oP 'There are \K[0-9]+')

# Si no podemos obtener el número de jugadores, no hacemos nada
if [ -z "$PLAYERS" ]; then
    exit 0
fi

# Hay jugadores -> borrar contador
if [ "$PLAYERS" -gt 0 ]; then
    rm -f "$STATE_FILE"
    exit 0
fi

# No hay jugadores -> empezar/continuar contador
if [ ! -f "$STATE_FILE" ]; then
    date +%s > "$STATE_FILE"
    exit 0
fi

EMPTY_SINCE=$(cat "$STATE_FILE")
NOW=$(date +%s)
EMPTY_SECONDS=$((NOW - EMPTY_SINCE))

# 10 minutos vacío -> apagar
if [ "$EMPTY_SECONDS" -ge $((EMPTY_MINUTES * 60)) ]; then
    docker exec "$CONTAINER" rcon-cli "say §6[SERVER] §eNo hay jugadores. Apagando el servidor..." >/dev/null 2>&1
    sleep 5
    docker stop "$CONTAINER"
    rm -f "$STATE_FILE"
fi
