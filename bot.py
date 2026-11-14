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
MOD_CONFIG_FILE = 'mod_config.json'

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


def load_mod_config() -> dict:
    if os.path.exists(MOD_CONFIG_FILE):
        with open(MOD_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"server disabled" : False, "disabled_channels" : []}

def save_mod_config(config: dict) -> None:
    with open(MOD_CONFIG_FILE, "w") as f:
         json.dump(config, f, indent=4)
mod_config = load_mod_config()

def get_guild_config(guild_id: int) -> dict:
    gid = str(guild_id)
    if gid not in mod_config:
        mod_config[gid] = {
            "server_disabled": False,
            "disabled_channels": []
        }
        save_mod_config(mod_config)
    return mod_config[gid]

def clean_text(text: str) -> str:
    decoded = text.lower().translate(CHAR_MAP)
    normalized = re.sub(r'[^a-z0-9]', '', decoded)
    return normalized

def get_skeleton(text: str) -> str:
    return re.sub(r'[aeiou]', '', text)

def contains_slur(raw: str) -> bool:
    # Pair each raw word with its cleaned version so we never lose the original text
    tokens = []
    for raw_w in raw.split():
        cleaned_w = clean_text(raw_w)
        if cleaned_w:
            tokens.append({
                "raw": raw_w,
                "clean": cleaned_w,
                "duped_v": re.sub(r'([aeiou])\1+', r'\1', cleaned_w),
                #"duped_a": re.sub(r'(.)\1+', r'\1', cleaned_w),
                "skele": get_skeleton(cleaned_w)
            })

    if not tokens:
        return False

    cleaned_spaced = " ".join(t["clean"] for t in tokens)
    for word in slurs:
        cleaned_word = clean_text(word)
        if not cleaned_word:
            continue

        # Long Slurs Check (>= 5 characters)
        if len(cleaned_word) >= 5:
            if cleaned_word in cleaned_spaced:
                # tokens that triggered the match, either by containing the cleaned_word or being contained by it
                matched_tokens = [t for t in tokens if cleaned_word in t["clean"] or t["clean"] in cleaned_word]
                raw_str = " ".join(t["raw"] for t in matched_tokens) or raw
                clean_str = " ".join(t["clean"] for t in matched_tokens) or cleaned_spaced
                print(f"Long slur detected: '{raw_str}' -> rebuilt as '{clean_str}' -> matched '{word}'")
                return True

            word_skele = get_skeleton(cleaned_word)
            if len(word_skele) >= 4:
                for t in tokens:
                    if word_skele == t["skele"] or (word_skele in t["skele"] and len(t["clean"]) >= 6):
                        print(f"Skeleton slur detected: '{t['raw']}' -> rebuilt as '{t['clean']}' (skele: '{t['skele']}') -> matched '{word}'")
                        return True

        # Short Slurs Check (< 5 characters)
        else:
            for t in tokens:
                if cleaned_word in (t["clean"], t["duped_v"]):
                    # Show the exact proccessed version of the word that matched the slur for debugging purposes
                    rebuilt = t["clean"] if cleaned_word == t["clean"] else t["duped_v"]
                    print(f"Short slur detected: '{t['raw']}' -> rebuilt as '{rebuilt}' -> matched '{word}'")
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

    # 1. Per-Server Moderation Toggle
    guild_cfg = get_guild_config(message.guild.id)
    if guild_cfg.get("server_disabled", False):
        await bot.process_commands(message)
        return

    # 2. Per-Channel Moderation Toggle
    if message.channel.id in guild_cfg.get("disabled_channels", []):
        await bot.process_commands(message)
        return
    
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
    name="togglemoderation",
    description="⏯️ Toggle slur moderation on/off for this channel or the entire server"
)
@app_commands.describe(
    scope="Choose whether to toggle moderation for this channel or the entire server"
)
@app_commands.choices(
    scope=[
        app_commands.Choice(name="Currrent Channel", value="channel"),
        app_commands.Choice(name="Entire Server", value="server"),
        app_commands.Choice(name="Check Current Status", value="status")
    ]
)
@is_authed()
async def toggle_moderation(interaction: discord.Interaction, scope: app_commands.Choice[str]):
    if not interaction.guild_id:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    
    guild_cfg = get_guild_config(interaction.guild_id)

    if scope.value == "status":
        server_state = "DISABLED 🔴" if guild_cfg.get("server_disabled", False) else "ENABLED 🟢"
        channel_disabled = interaction.channel_id in guild_cfg.get("disabled_channels", [])
        channel_state = "DISABLED 🔴" if channel_disabled else "ENABLED 🟢"

        disabled_list = guild_cfg.get("disabled_channels", [])
        disabled_mentions = ", ".join(f"<#{cid}>" for cid in disabled_list) if disabled_list else "None"

        embed_color = discord.Color.red() if (guild_cfg.get("server_disabled", False) or channel_disabled) else discord.Color.green()
         
        embed = discord.Embed(
            title="🛡️ Moderation Status",
            description=(
                f"• **Server-wide:** {server_state}\n"
                f"• **This Channel (<#{interaction.channel_id}>):** {channel_state}\n"
                f"• **All Disabled Channels:** {disabled_mentions}"
            ),
            color=embed_color
        )
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if scope.value == "server":
        guild_cfg["server disabled"] = not guild_cfg.get("server disabled", False)
        save_mod_config(mod_config)

        status = "DISABLED 🔴" if guild_cfg["server_disabled"] else "ENABLED 🟢"
        await interaction.response.send_message(
            f"Slur moderation in now **{status}** server-wide",
            ephemeral=True
        )

    elif scope.value == "channel":
        channel_id = interaction.channel_id
        disabled_channels = guild_cfg.setdefault("disabled_channels", [])
        if channel_id in disabled_channels:
            mod_config["disabled_channels"].remove(channel_id)
            save_mod_config(mod_config)
            await interaction.response.send_message(
                f"Slur moderation **ENABLED 🟢** for <#{channel_id}>.",
                ephemeral=True
            )
        else:
            disabled_channels.append(channel_id)
            save_mod_config(mod_config)
            await interaction.response.send_message(
                f"Slur moderation **DISABLED 🔴** for <#{channel_id}>.",
                ephemeral=True
            )


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
