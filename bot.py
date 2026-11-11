
import os
import random

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


WEATHER_CODES = {
    0: "Céu limpo ☀️",
    1: "Predominantemente limpo 🌤️",
    2: "Parcialmente nublado ⛅",
    3: "Nublado ☁️",
    45: "Nevoeiro 🌫️",
    48: "Nevoeiro com geada 🌫️",
    51: "Garoa leve 🌧️",
    61: "Chuva leve 🌧️",
    63: "Chuva moderada 🌧️",
    65: "Chuva forte ⛈️",
    71: "Neve leve ❄️",
    80: "Pancadas de chuva 🌦️",
    95: "Trovoadas ⛈️",
}

DICAS = [
    "Economize energia elétrica sempre que possível. 💡",
    "Evite desperdício de água. 💧",
    "Prefira caminhar ou utilizar bicicleta em trajetos curtos. 🚲",
    "Separe corretamente os resíduos recicláveis. ♻️",
    "Evite produtos descartáveis quando houver alternativas. 🌱",
    "Plante e preserve árvores e áreas verdes. 🌳",
]


async def buscar_json(url, params):
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()


@bot.event
async def on_ready():
    print(f"ClimateAI conectado como {bot.user}")
    print("Bot pronto para uso!")


@bot.tree.command(
    name="clima",
    description="Consulta as condições meteorológicas de uma cidade."
)
@app_commands.describe(cidade="Nome da cidade que deseja consultar")
async def clima(interaction: discord.Interaction, cidade: str):
    await interaction.response.defer()

    try:
        geo = await buscar_json(
            "https://geocoding-api.open-meteo.com/v1/search",
            {
                "name": cidade,
                "count": 1,
                "language": "pt",
                "format": "json"
            }
        )

        resultados = geo.get("results", [])

        if not resultados:
            await interaction.followup.send(
                "❌ Não encontrei essa cidade. Verifique o nome e tente novamente."
            )
            return

        local = resultados[0]

        dados = await buscar_json(
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": local["latitude"],
                "longitude": local["longitude"],
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "precipitation,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": "auto"
            }
        )

        atual = dados["current"]
        codigo = atual["weather_code"]

        condicao = WEATHER_CODES.get(
            codigo, "Condição meteorológica não identificada"
        )

        embed = discord.Embed(
            title=f"🌎 ClimateAI | {local['name']}",
            description=condicao,
            color=discord.Color.green()
        )

        embed.add_field(
            name="🌡️ Temperatura",
            value=f"{atual['temperature_2m']} °C",
            inline=True
        )

        embed.add_field(
            name="💧 Umidade",
            value=f"{atual['relative_humidity_2m']}%",
            inline=True
        )

        embed.add_field(
            name="🌬️ Vento",
            value=f"{atual['wind_speed_10m']} km/h",
            inline=True
        )

        embed.add_field(
            name="🌡️ Sensação térmica",
            value=f"{atual['apparent_temperature']} °C",
            inline=True
        )

        embed.add_field(
            name="🌧️ Precipitação",
            value=f"{atual['precipitation']} mm",
            inline=True
        )

        embed.add_field(
            name="📍 Localização",
            value=(
                f"{local.get('admin1', 'Região não informada')}, "
                f"{local.get('country', 'País não informado')}"
            ),
            inline=False
        )

        embed.set_footer(
            text="Dados meteorológicos: Open-Meteo | Não representa previsão climática de longo prazo."
        )

        await interaction.followup.send(embed=embed)

    except (aiohttp.ClientError, KeyError, ValueError):
        await interaction.followup.send(
            "⚠️ Não foi possível consultar os dados. Tente novamente mais tarde."
        )


@bot.tree.command(
    name="dica",
    description="Receba uma dica para ajudar o meio ambiente."
)
async def dica(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌱 Dica sustentável",
        description=random.choice(DICAS),
        color=discord.Color.green()
    )

    embed.set_footer(text="Pequenas atitudes podem gerar grandes mudanças!")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(
    name="sobre",
    description="Conheça o projeto ClimateAI."
)
async def sobre(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌎 ClimateAI",
        description=(
            "Um projeto de conscientização ambiental desenvolvido "
            "para o Hackathon de mudanças climáticas."
        ),
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Objetivo",
        value="Facilitar o acesso a informações meteorológicas e incentivar atitudes sustentáveis.",
        inline=False
    )

    embed.add_field(
        name="Tecnologias",
        value="Python • Discord.py • Open-Meteo API",
        inline=False
    )

    embed.add_field(
        name="Comandos",
        value="`/clima` • `/dica` • `/sobre`",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


class ClimateAIBot(commands.Bot):
    async def setup_hook(self):
        await self.tree.sync()
        print("Comandos sincronizados!")


if not TOKEN:
    raise RuntimeError("Configure DISCORD_TOKEN no arquivo .env")

# Inicia o bot
bot.setup_hook = ClimateAIBot.setup_hook.__get__(bot, commands.Bot)
bot.run(TOKEN)
