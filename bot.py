import discord
from discord.ext import commands
from discord import ui
import pandas as pd
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
EXCEL_FILE = "data.xls"

ADMIN_ID = 1222370876952154115
ALLOWED_CHANNEL = 1517927198571364423

# Các cột chỉ số cơ bản — luôn hiển thị nếu có giá trị
BASE_COLUMNS = [
    "NAME", "AGE", "NATIONALITY", "FOOT", "HEIGHT",
    "WEAK FOOT ACCURACY", "WEAK FOOT FREQUENCY", "INJURY TOLERANCE",
    "POSITION", "ATTACK", "DEFENCE", "HEADER ACCURACY",
    "DRIBBLE ACCURACY", "SHORT PASS ACCURACY", "SHORT PASS SPEED",
    "LONG PASS ACCURACY", "LONG PASS SPEED", "SHOT ACCURACY",
    "PLACE KICKING", "SWERVE", "BALL CONTROLL", "GOAL KEEPING SKILLS",
    "RESPONSE", "EXPLOSIVE POWER", "DRIBBLE SPEED", "TOP SPEED",
    "BODY BALANCE", "STAMINA", "KICKING POWER", "JUMP",
    "TENACITY", "TEAMWORK", "CLUB TEAM",

]

# Cờ kỹ năng (S01-S26 = playing styles, P01-P18 = playstyles)
# Giá trị 1 = cầu thủ có kỹ năng này, 0 = không có
SKILL_COLUMNS = [
    "S01 1-TOUCH PLAY", "S02 OUTSIDE CURVE", "S03 LONG THROW", "S04 SUPER-SUB",
    "S05 SPEED MERCHANT", "S06 LONG RANGE DRIVE", "S07 SHOULDER FEINT SKILLS",
    "S08 TURNING SKILLS", "S09 ROULETTE SKILLS", "S10 FLIP FLAP SKILLS",
    "S11 FLICKING SKILLS", "S12 SCISSORS SKILLS", "S13 STEP ON SKILLS",
    "S14 DEFT TOUCH SKILLS", "S15 KNUCKLE SHOT", "S16 JUMPING VOLLEY",
    "S17 SCISSOR KICK", "S18 HEEL FLICK", "S19 WEIGHTED PASS",
    "S20 DOUBLE TOUCH", "S21 RUN AROUND", "S22 SOMBRERO", "S23 180 DRAG",
    "S24 LUNGING TACKLE", "S25 DIVING HEADER", "S26 GK LONG THROW",
    "P01 CLASSIC NO.10", "P02 ANCHOR MAN", "P03 TRICKSTER", "P04 DARTING RUN",
    "P05 MAZING RUN", "P06 PINPOINT PASS", "P07 EARLY CROSS", "P08 BOX TO BOX",
    "P09 INCISIVE RUN", "P10 LONG RANGER", "P11 ENFORCER", "P12 GOAL POACHER",
    "P13 DUMMY RUNNER", "P14 FREE ROAMING", "P15 TALISMAN",
    "P16 FOX IN THE BOX", "P17 OFFENSIVE SIDEBACK", "P18 TRACK BACK",

]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

_df_cache = None


def load_excel():
    """Load file .xls (đời cũ cần engine=xlrd), có cache để đỡ phải đọc lại 16MB mỗi lần."""
    global _df_cache
    if _df_cache is not None:
        return _df_cache
    try:
        df = pd.read_excel(EXCEL_FILE, engine="xlrd", sheet_name="Worksheet")
        df.columns = df.columns.str.strip()
        _df_cache = df
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Lỗi đọc file Excel: {e}")
        return None


def reload_excel():
    global _df_cache
    _df_cache = None
    return load_excel()


def search_players(name: str):
    """Tìm tất cả cầu thủ khớp tên (chứa chuỗi, không phân biệt hoa thường)."""
    df = load_excel()
    if df is None:
        return None
    mask = df["NAME"].astype(str).str.lower().str.contains(name.lower(), na=False)
    return df[mask]


def format_player(row: pd.Series) -> str:
    """Format thông tin cầu thủ theo hàng dọc: Field:Value"""
    lines = []

    for col in BASE_COLUMNS:
        if col not in row.index:
            continue
        val = row[col]
        if pd.isna(val):
            continue
        if isinstance(val, float) and val.is_integer():
            val = int(val)
        lines.append(f"**{col}**: {val}")

    # Kỹ năng có = 1
    owned_skills = []
    for col in SKILL_COLUMNS:
        if col not in row.index:
            continue
        val = row[col]
        if pd.notna(val) and int(val) == 1:
            # Bỏ mã số S01/P01 ở đầu, giữ lại tên kỹ năng cho gọn
            skill_name = col.split(" ", 1)[1] if " " in col else col
            owned_skills.append(skill_name)

    if owned_skills:
        lines.append("")
        lines.append(f"**SKILLS**: {', '.join(owned_skills)}")

    return "\n".join(lines)


class PlayerSelect(ui.Select):
    def __init__(self, matches: pd.DataFrame):
        self.matches = matches.reset_index(drop=True)
        options = []
        for i, row in self.matches.head(25).iterrows():  # Discord giới hạn 25 option
            club = row.get("CLUB TEAM", "")
            club = "" if pd.isna(club) else str(club)
            label = str(row["NAME"])[:100]
            desc = f"{club} | AGE: {row.get('AGE', '?')}"[:100]
            options.append(discord.SelectOption(label=label, description=desc, value=str(i)))

        super().__init__(placeholder="Chọn cầu thủ...", options=options)

    async def callback(self, interaction: discord.Interaction):
        idx = int(self.values[0])
        row = self.matches.iloc[idx]
        text = format_player(row)
        await interaction.response.edit_message(content=text, view=None)


class PlayerSelectView(ui.View):
    def __init__(self, matches: pd.DataFrame):
        super().__init__(timeout=60)
        self.add_item(PlayerSelect(matches))


@bot.event
async def on_ready():
    print(f"✅ Bot đã online: {bot.user}")
    df = load_excel()
    if df is not None:
        print(f"📊 Đã load {len(df)} cầu thủ từ {EXCEL_FILE}")
    else:
        print(f"⚠️ Không tìm thấy file {EXCEL_FILE}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()

    # Bỏ qua nếu là lệnh prefix !
    if not content.startswith("!"):
        matches = search_players(content)

        if matches is not None and not content == "":
            if len(matches) == 0:
                pass  # không khớp gì, im lặng để tránh spam khi người dùng chat chuyện khác
            elif len(matches) == 1:
                await message.reply(format_player(matches.iloc[0]))
            else:
                count = len(matches)
                note = f"🔎 Tìm thấy **{count}** cầu thủ khớp với \"{content}\"."
                if count > 25:
                    note += " (chỉ hiện 25 kết quả đầu, gõ tên cụ thể hơn để thu hẹp)"
                view = PlayerSelectView(matches)
                await message.reply(note, view=view)

    await bot.process_commands(message)


@bot.command(name="reload")
async def reload_cmd(ctx):
    """Reload lại dữ liệu từ file Excel sau khi cập nhật."""
    df = reload_excel()
    if df is None:
        await ctx.reply("❌ Không tìm thấy file `data.xls`.")
        return
    await ctx.reply(f"✅ Đã reload dữ liệu! Tổng cộng **{len(df)}** cầu thủ.")


@bot.command(name="help_bot", aliases=["huongdan", "hd"])
async def help_info(ctx):
    embed = discord.Embed(title="🤖 Hướng dẫn sử dụng Bot", color=0x00b4d8)
    embed.add_field(
        name="💬 Cách dùng",
        value="Gõ thẳng tên cầu thủ, ví dụ: `Messi` hoặc `Ronaldo`",
        inline=False
    )
    embed.add_field(
        name="⌨️ Lệnh",
        value="`!reload` — cập nhật dữ liệu sau khi sửa file Excel\n`!help_bot` — xem hướng dẫn",
        inline=False
    )
    await ctx.reply(embed=embed)

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )

Thread(target=run_web).start()

bot.run(TOKEN)
