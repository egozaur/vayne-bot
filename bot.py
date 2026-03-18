import os
import aiohttp
import discord
from discord.ext import commands

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
 

async def ask_ai(prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
      "model": "mistralai/mistral-7b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()
            print(f"OpenRouter response: {data}")
            return data["choices"][0]["message"]["content"].strip()


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
        answer = await ask_ai(prompt)
        embed = discord.Embed(
            title=f"⚔️ Vayne Top vs {champion}",
            description=answer,
            color=0xC89B3C,
        )
        embed.set_footer(text="Powered by Gemini AI • !vs [postać]")
        await loading_msg.delete()
        await ctx.send(embed=embed)

    except Exception as e:
        await loading_msg.edit(content=f"❌ Błąd: {e}")


@bot.command(name="pomoc")
async def pomoc(ctx):
    embed = discord.Embed(
        title="🏹 Vayne Top Bot - Pomoc",
        description="**Dostępne komendy:**\n\n`!vs [postać]` — porada jak grać Vayne Top vs daną postać\n`!pomoc` — ta wiadomość",
        color=0xC89B3C,
    )
    await ctx.send(embed=embed)


bot.run(DISCORD_TOKEN)
