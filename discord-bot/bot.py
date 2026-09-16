import os
import asyncio
import docker
import discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

docker_client = docker.from_env()


@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot conectado como {client.user}")


async def wait_for_minecraft_ready(container, timeout=300):
    """
    Espera hasta que Minecraft Forge termine de arrancar.
    Busca el mensaje 'Done' en los logs.
    """

    start_time = asyncio.get_event_loop().time()

    while asyncio.get_event_loop().time() - start_time < timeout:

        container.reload()

        if container.status != "running":
            return False

        logs = container.logs(tail=100).decode("utf-8", errors="ignore")

        if "Done (" in logs or "Done!" in logs:
            return True

        await asyncio.sleep(3)

    return False


@tree.command(
    name="minecraft",
    description="Control del servidor Minecraft"
)
@app_commands.describe(action="Acción que quieres realizar")
@app_commands.choices(action=[
    app_commands.Choice(name="status", value="status"),
    app_commands.Choice(name="start", value="start"),
    app_commands.Choice(name="stop", value="stop"),
    app_commands.Choice(name="restart", value="restart"),
])
async def minecraft(
    interaction: discord.Interaction,
    action: app_commands.Choice[str]
):

    await interaction.response.defer()

    try:
        container = docker_client.containers.get("minecraft-forge")
        container.reload()

        # ---------------- STATUS ----------------

        if action.value == "status":

            if container.status == "running":
                message = (
                    "🟢 **Minecraft Forge**\n"
                    "Estado: **ONLINE**"
                )
            else:
                message = (
                    "🔴 **Minecraft Forge**\n"
                    "Estado: **OFFLINE**"
                )

        # ---------------- START ----------------

        elif action.value == "start":

            if container.status == "running":

                message = (
                    "🟢 **Minecraft Forge** ya está **ONLINE**."
                )

            else:

                await interaction.edit_original_response(
                    content=(
                        "🚀 **Iniciando Minecraft Forge...**\n"
                        "⏳ Cargando Forge, mods y mundo..."
                    )
                )

                container.start()

                ready = await wait_for_minecraft_ready(container)

                if ready:
                    message = (
                        "✅ **Minecraft Forge se ha iniciado correctamente.**\n"
                        "🎮 ¡El servidor ya está listo para jugar!"
                    )
                else:
                    message = (
                        "⚠️ **Minecraft Forge está tardando más de lo esperado.**\n"
                        "Comprueba los logs del servidor."
                    )

        # ---------------- STOP ----------------

        elif action.value == "stop":

            if container.status != "running":

                message = (
                    "🔴 **Minecraft Forge** ya está **OFFLINE**."
                )

            else:

                await interaction.edit_original_response(
                    content=(
                        "🛑 **Apagando Minecraft Forge...**\n"
                        "⏳ Guardando y cerrando el servidor..."
                    )
                )

                container.stop()

                message = (
                    "🔴 **Minecraft Forge se ha apagado correctamente.**"
                )

        # ---------------- RESTART ----------------

        elif action.value == "restart":

            await interaction.edit_original_response(
                content=(
                    "🔄 **Reiniciando Minecraft Forge...**\n"
                    "⏳ Cargando Forge, mods y mundo..."
                )
            )

            container.restart()

            ready = await wait_for_minecraft_ready(container)

            if ready:
                message = (
                    "✅ **Minecraft Forge se ha reiniciado correctamente.**\n"
                    "🎮 ¡El servidor ya está listo para jugar!"
                )
            else:
                message = (
                    "⚠️ **Minecraft Forge está tardando más de lo esperado.**\n"
                    "Comprueba los logs del servidor."
                )

        await interaction.edit_original_response(content=message)

    except docker.errors.NotFound:

        await interaction.edit_original_response(
            content="❌ No encuentro el contenedor `minecraft-forge`."
        )

    except Exception as e:

        await interaction.edit_original_response(
            content=f"❌ **Error:** `{e}`"
        )


client.run(TOKEN)
