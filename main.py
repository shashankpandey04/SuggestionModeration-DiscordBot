import asyncio
import discord
import random
from discord.ext import commands
import os
import keep_alive
import json

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='?', intents=intents)

target_channel_id = {}
max_characters = 150


@bot.event
async def on_ready():
  print(f'Logged in as {bot.user.name} - {bot.user.id}')
  print('Bot is ready!')
  status = "/help"
  await bot.change_presence(activity=discord.Activity(
      type=discord.ActivityType.watching, name=status))
  await bot.tree.sync()


try:
  with open('config.txt', 'r') as file:
    data = json.load(file)
    target_channel_id = data.get('target_channel_id', {})
    max_characters = data.get('max_characters', 150)
except FileNotFoundError:
  target_channel_id = {}
  max_characters = 150


@bot.event
async def on_message(message):
  if message.author.bot:
    return

  server_id = message.guild.id
  if server_id in target_channel_id and message.channel.id == target_channel_id[
      server_id]:
    num_characters = len(message.content)

    if num_characters > max_characters:
      warning_embed = discord.Embed(
          title='Your suggestion exceeds maximum character limit',
          description=
          'The suggestion which you posted is a violation of our maximum character rule. Please cut out the unwanted characters from your suggestion.\n\nYour suggestion will be deleted in 1 minute. You can copy it somewhere to preserve your message and post it later.',
          color=discord.Color.red())
      warning_embed.set_footer(text='Message will self-delete in 1 minute.')

      warning_message = await message.channel.send(f'{message.author.mention}',
                                                   embed=warning_embed)

      await asyncio.sleep(60)
      try:
        await message.delete()
        await warning_message.delete()
      except discord.errors.NotFound:
        pass
      return

  await bot.process_commands(message)


@bot.tree.command()
@commands.has_permissions(administrator=True)
async def set_channel(interaction: discord.Interaction,
                      channel: discord.TextChannel):
  server_id = interaction.guild.id
  target_channel_id[server_id] = channel.id
  save_config()  # Save configurations on each modification
  await interaction.response.send_message(
      f'Bot will now monitor the channel: {channel.mention}')


@bot.tree.command()
@commands.has_permissions(administrator=True)
async def set_max_characters(interaction: discord.Interaction, limit: int):
  global max_characters
  max_characters = limit
  save_config()  # Save configurations on each modification
  await interaction.response.send_message(
      f'Maximum character limit set to: {limit}')


@bot.tree.command()
async def ping(interaction: discord.Interaction):
  '''Check the bot's ping.'''
  latency = round(bot.latency * 1000)
  await interaction.response.send_message(f'Pong! Latency: {latency}ms')


@bot.tree.command()
async def help(interaction: discord.Interaction):
  '''Link to Support Server'''
  embed = discord.Embed(
      title="Need Assistance?",
      description=
      f"Join our Support Discord Server and our support team will help you with your problem. [Click Here](https://discord.gg/Z53qMbuB)",
      color=60407)
  await interaction.response.send_message(embed=embed)


def save_config():
  data = {
      'target_channel_id': target_channel_id,
      'max_characters': max_characters
  }
  with open('config.txt', 'w') as file:
    json.dump(data, file, indent=4)


keep_alive.keep_alive()
my_secret = os.environ['TOKEN']
bot.run(my_secret)
