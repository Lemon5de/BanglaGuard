# 🛡️ BanglaGuard

**BanglaGuard** is an automated Discord moderation bot engineered to detect and filter obfuscated Bangla slurs, offensive language, and leetspeak variations in real-time.

---

## ✨ Features

- **Advanced Pattern Matching:** Detects exact matches, leetspeak character replacements (`@` -> `a`, `3` -> `e`), vowel duplication, and skeleton word roots.
- **Dynamic Blacklist:** Add or remove slurs on the fly via slash commands without restarting the bot.
- **Role-Based Access Control:** Restricts administrative commands to specific server roles (`Admin`, `Developer`, `Officer`, `Creator`) or users with `Manage Messages` permissions.
- **Auto-Moderation:** Automatically deletes detected messages and sends an ephemeral, self-destructing notice to the user.

---

## 🛠️ Slash Commands

| Command | Description | Permission Required |
| :--- | :--- | :--- |
| `/help` | Displays the help menu with all available commands. | Everyone |
| `/addslur <word>` | Adds a new slur/word to the filtering engine. | Authorized Roles / Manage Messages |
| `/removeslur <word>` | Removes a slur/word from the filtering engine. | Authorized Roles / Manage Messages |
| `/listslurs` | Displays an embed listing all blacklisted words. | Authorized Roles / Manage Messages |

---

## ⚙️ Configuration

To adapt the bot for your own server, update the configuration block near the top of `bot.py`[cite: 34]:

```python
# Allowed administrative roles (Names or IDs)
ALLOWED_ROLE_NAMES = {"Admin", "Developer", "Officer", "Creator"}
ALLOWED_ROLE_IDS = {1561711906472071288, 1561842901011664906}

# Categories where slur moderation is ignored (IDs or Lowercase Names)
IGNORED_CATEGORIES = {
    1561711922477273090,  # Category ID
    "information", "staff", "support"  # Lowercase Category Names
}
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- A Discord Bot Token from the [Discord Developer Portal](https://discord.com/developers/applications)

### Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Lemon5de/BanglaGuard.git](https://github.com/Lemon5de/BanglaGuard.git)
   cd BanglaGuard
   ```

2. **Set up a virtual environment:**

   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

   - **Windows:**
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   
   Copy `.env.example` to create your local `.env` file:
   
   - **Linux / macOS:**
     ```bash
     cp .env.example .env
     ```

   - **Windows:**
     ```cmd
     copy .env.example .env
     ```

   Open `.env` and set your token:
   ```env
   DISCORD_TOKEN=your_actual_bot_token_here
   ```

5. **Run the bot:**
   ```bash
   python bot.py
   ```

---

## 🌐 Deployment Options

### Option 1: VPS / Linux Server Deployment (PM2)

1. Clone the repository and navigate into the project directory:
   ```bash
   git clone [https://github.com/Lemon5de/BanglaGuard.git](https://github.com/Lemon5de/BanglaGuard.git)
   cd BanglaGuard
   ```

2. Create virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Set up your `.env` file:
   ```bash
   cp .env.example .env
   nano .env
   ```

4. Run continuously using PM2:
   ```bash
   pm2 start bot.py --name "BanglaGuard" --interpreter ./venv/bin/python
   ```

### Option 2: Docker Container Deployment

1. Build the Docker image:
   ```bash
   docker build -t banglaguard .
   ```

2. Run the container:
   ```bash
   docker run -d --name banglaguard --env-file .env banglaguard
   ```

---

## 📜 Version History

See [CHANGELOG.md](CHANGELOG.md) for full details on releases and updates.