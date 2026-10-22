import os
import re
import json
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN")
SLURS_FILE = 'slurs.json'

# ------------------------------ CHANGE THIS SECTION TO VALUES ACCORDING TO YOUR SERVER -----------------------------------
ALLOWED_ROLE_NAMES = {"Admin", "Developer", "Officer", "Creator"}
ALLOWED_ROLE_IDS = {1561711906472071288,1561842901011664906,1561817331301355590,1561817027788673114}
IGNORED_CATEGORIES = {
    1561711922477273090, # Information ID
    1561712022175883396, # Staff ID
    1561712014752227451, # Support ID
    "information",       # Category Name
    "staff",             # Category Name
    "support"            # Category Name
}
# -------------------------------------------------------------------------------------------------------------------------

default_slurs = [
    "madarchod", "madarchood", "bonchod", "heda", "kutta", "bokachoda", "bainchod", "boonchod", "khanki",
    "khankimagi", "khankii", "bocchoda", "bochoda", "baalchoda", "balchoda", "bessha", "beshya", "bhesya",
    "bessharpula", "bessharpola", "bessharpo", "gandmara", "gandmarani", "baal", "bal", "baler", "balchhal",
    "balsaal", "balchal", "chut", "chuti", "chud", "chuda", "chudi", "chudidani", "chudani",
    "chudmarani", "chudna", "chudne", "foda", "fud", "fudi", "fudirpula", "gand", "gandu",
    "gandoo", "magi", "magirpula", "magirpola", "magirpo", "magirbacha", "haramjada", "haramjadi", "kuttarpula",
    "kuttarbaccha", "kuttarpo", "kutti", "suar", "shuor", "shua", "dhon", "shuarerpola", "shuarerbacha",
    "shuarerpo", "shuarerpula", "khankirpula", "khankirpola", "khankirpo", "khankirbacha", "chodna", "chodni"
]
CHAR_MAP = str.maketrans({
    '@': 'a', '4': 'a', '3': 'e', '1': 'i', '!': 'i',
    '0': 'o', '$': 's', '5': 's', '7': 't', 'v': 'u',
    '1': 'l', '!': 'l'
})

def load_slurs() -> set:
    if os.path.exists(SLURS_FILE):
        with open(SLURS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    else:
        save_slurs(default_slurs)
        return set(default_slurs)

def save_slurs(data):
    with open(SLURS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data), f, indent=4)

slurs = load_slurs()

def clean_text(text: str) -> str:
    decoded = text.lower().translate(CHAR_MAP)
    normalized = re.sub(r'[^a-z0-9]', '', decoded)
    return normalized

def get_skeleton(text: str) -> str:
    return re.sub(r'[aeiou]', '', text)

def contains_slur(raw: str) -> bool:
    cleaned = clean_text(raw)
    for word in slurs:
        if len(word) >= 5 and word in cleaned:
            print(f'Detected long slur: {word}')
            return True

    msg_skele = get_skeleton(cleaned)
    for word in slurs:
        if len(word) >= 5:
            word_skele = get_skeleton(word)
            if len(word_skele) >= 3 and word_skele in msg_skele:
                print(f'Detected long slur (skeleton match): {word}')
                return True

    individual_words = [clean_text(w) for w in raw.split() if clean_text(w) ]
    duped_vowels = [re.sub(r'([aeiou])\1+', r'\1', w) for w in individual_words]
    duped_all = [re.sub(r'(.)\1+', r'\1', w) for w in individual_words]
    for word in slurs:
        cleaned_word = clean_text(word)
        if not cleaned_word:
          continue
        if len(cleaned_word) < 5 and (cleaned_word in individual_words or cleaned_word in duped_vowels or cleaned_word in duped_all):
            print(f'Detected short slur: {word}')
            return True

    return False

def is_authed():
    async def predicate(interaction: discord.Interaction) -> bool:
        if not isinstance(interaction.user, discord.Member):
            return False
        if interaction.user.guild_permissions.manage_messages:
            return True
        for role in interaction.user.roles:
            if role.name in ALLOWED_ROLE_NAMES or role.id in ALLOWED_ROLE_IDS:
                return True
        raise app_commands.CheckFailure("You do not have permission or an authorized role to use this command.")
    return app_commands.check(predicate)

def is_category_ignored(channel) -> bool:
    category = getattr(channel, 'category', None)
    if not category:
        return False
    return(
        category.id in IGNORED_CATEGORIES or 
        category.name.lower() in IGNORED_CATEGORIES
    )
# -------------------- USED TO IGNORE HIGH STATUS MEMBERS(NO USE CURRENTLY)----------------------------
# def is_member_ignored(author) -> bool:
#     if not isinstance(author, discord.Member):
#         return False
#     if author.guild_permissions.manage_messages or author.guild_permissions.administrator:
#         return True
#     return any(
#         role.name in ALLOWED_ROLE_NAMES or role.id in ALLOWED_ROLE_IDS
#         for role in author.roles
#     )
    

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    activity = discord.Activity(
        type=discord.ActivityType.watching, 
        name="your messages 👀"
    )
    await bot.change_presence(activity=activity)

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")


@bot.event
async def on_message(message: discord.Message):
    # Ignore Bot msg and DM
    if message.author.bot or not message.guild:
        return

    # Test Command
    if message.content.startswith('!hello'):
        await message.channel.send("HELLO")

    # Ignore Category Filtering but still proccess commands
    if is_category_ignored(message.channel):
        channel_name = getattr(message.channel, 'name', 'no-name')
        category = getattr(message.channel, 'category', None)
        category_name = getattr(category, 'name', 'No Category')
        print(f"msg ignored in {channel_name} under {category_name}")
        await bot.process_commands(message)
        return

    # Filtering in ALL user Channels for All users
    if contains_slur(message.content):
        await message.delete()
        await message.channel.send(
            f"{message.author.mention}, Chi chi, pocha kotha bolte neii🤫🤫",
            delete_after=5
        )
        return

    # Proccess Commands in valid msgs
    await bot.process_commands(message)


@bot.tree.command(
    name="addslur",
    description="➕ Add a new word to the slur filter list."
)
@is_authed()
async def add_slur(interaction: discord.Interaction, word: str):
    cleaned = clean_text(word)
    if not cleaned:
        await interaction.response.send_message(
            f"Invalid word given.",
            ephemeral=True
        )
    if cleaned in slurs:
        await interaction.response.send_message(
            f"`{cleaned}` already exists in the filter list.",
            ephemeral=True
        )       
    else:
        slurs.add(cleaned)
        save_slurs(slurs)
        await interaction.response.send_message(
            f"Added `{cleaned}` to the filter list.", 
            ephemeral=True
        )

@bot.tree.command(
    name="removeslur", 
    description="❌ Remove an existing word from the slur filter list."
)
@is_authed()
async def remove_slur(interaction: discord.Interaction, word: str):
    cleaned_word = clean_text(word)
    if cleaned_word in slurs:
        slurs.remove(cleaned_word)
        save_slurs(slurs)
        await interaction.response.send_message(
            f"Removed `{cleaned_word}` from the filter list.", 
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"`{cleaned_word}` was not found in the filter list.", 
            ephemeral=True
        )

@bot.tree.command(
    name="listslurs",
    description="📜 Display all currently blacklisted words."
)
@is_authed()

async def list_slurs(interaction: discord.Interaction):
    if not slurs:
        await interaction.response.send_message(
            "The slur filter list is currently empty.", 
            ephemeral=True
        )
        return
    sorted_slurs = sorted(list(slurs))
    formatted_list = ", ".join(f"`{word}`" for word in sorted_slurs)
    if len(formatted_list) > 3800:
        formatted_list = formatted_list[:3800] + "...\n*(List truncated due to length limits)*"

    embed = discord.Embed(
        title="📜 BanglaGuard - Blacklisted Language Filter",
        description=f"**Total Slurs Blocked ({len(slurs)}):**\n\n{formatted_list}",
        color=discord.Color.blue()  # Accent color strip on the left
    )
    
    embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(
        name="help",
        description="👷Shows the list of commands this bot provides"
)
async def help_menu(interaction: discord.Interaction):
    commands_list = bot.tree.get_commands()
    help_list = []
    for cmd in commands_list:
        description = getattr(cmd, "description", "No description provided.")
        help_list.append(f"**`/{cmd.name}`**  {description}")
    description_content = "\n".join(help_list)
    embed = discord.Embed(
        title="📃 List of commands",
        description=description_content,
        color=discord.Color.blue()  
    )
    embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    


@add_slur.error
@remove_slur.error
async def slash_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message(str(error), ephemeral=True)

@list_slurs.error
async def list_slurs_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message(str(error), ephemeral=True)

if not TOKEN:
    raise ValueError("Error: DISCORD_TOKEN environment variable not found in .env")

bot.run(TOKEN)
