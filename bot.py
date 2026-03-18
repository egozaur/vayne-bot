import os
import discord
from discord.ext import commands
from google import genai

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

client_ai = genai.Client(api_key=GEMINI_API_KEY)

MODELS = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


async def ask_gemini(prompt: str) -> str:
    last_error = None
    for model in MODELS:
        try:
            print(f"Próbuję model: {model}")
            response = client_ai.models.generate_content(
                model=model,
                contents=prompt,
            )
            print(f"Sukces z modelem: {model}")
            return response.text.strip()
        except Exception as e:
            print(f"Model {model} nie działa: {e}")
            last_error = e
            continue
    raise last_error


@bot.event
async def on_ready():
    print(f"Bot zalogowany jako {bot.user}")


@bot.command(name="vs")
async def vs(ctx, *, champion: str = None):
    if not champion:
        await ctx.send("❌ Podaj postać! Przykład: `!vs Tryndamere`")
        return

    champion = champion.strip().title()
    loading_msg = await ctx.send(f"🎯 Analizuję matchup Vayne Top vs **{champion}**...")

    prompt = f"""Jesteś ekspertem League of Legends. Odpowiedz TYLKO po polsku.
Jak grać Vayne Top vs {champion}?
Podaj dokładnie 5 punktów w formacie:
1. [punkt]
2. [punkt]
3. [punkt]
4. [punkt]
5. [punkt]
Każdy punkt max 2 zdania. Bez wstępu, bez podsumowania - tylko 5 punktów."""

    try:
        answer = await ask_gemini(prompt)

        embed = discord.Embed(
            title=f"⚔️ Vayne Top vs {champion}",
            description=answer,
            color=0xC89B3C,
        )
        embed.set_footer(text="Powered by Gemini AI • !vs [postać]")

        await loading_msg.delete()
        await ctx.send(embed=embed)

    except Exception as e:
        await loading_msg.edit(content=f"❌ Wszystkie modele niedostępne: {e}")


@bot.command(name="pomoc")
async def pomoc(ctx):
    embed = discord.Embed(
        title="🏹 Vayne Top Bot - Pomoc",
        description="**Dostępne komendy:**\n\n`!vs [postać]` — porada jak grać Vayne Top vs daną postać\n`!pomoc` — ta wiadomość",
        color=0xC89B3C,
    )
    await ctx.send(embed=embed)


bot.run(DISCORD_TOKEN)
