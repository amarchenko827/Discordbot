import discord
from discord.ext import commands
from discord.utils import get


#Сетап Discord API
PREFIX = '!'
client = commands.Bot(command_prefix = PREFIX)
client.load_extension('Moderation')
client.load_extension('Music')

#Ключевые слова
#Запрещённые слова
bad_words = ['рыба', 'стул', 'машина']


#Подключение и статус
@client.event
async def on_ready():
	
	await client.change_presence(status=discord.Status.online,activity = discord.Game('!help'))
	print('Бот подключен')


#Проверка на ошибку
@client.event
async def on_command_error(ctx,error):

	if isinstance(error, commands.CommandNotFound):
		await ctx.send(embed = discord.Embed(description = 'Команда не найдена!', color = 0x0c0c0c))
	else: pass


#Автоматическая выдача роли
@client.event
async def on_member_join(member):

	role = get(member.guild.roles, name = 'User')
	await member.add_roles(role)
	print(f'[Log] {member} присоединился к серверу {member.guild.name}')

	for channel in member.guild.channels:
		if channel.name == 'general':
			await channel.send(embed = discord.Embed(description = f'Добро пожаловать на наш сервер, {member.mention}! Если нужна какая-то помощь - пиши !help в чат :flushed:', color = 0x0c0c0c))
	
	
#Фильтрация чата
@client.event
async def on_message(message):
	
	await client.process_commands(message)
	msg = message.content.lower()
	
	if msg in bad_words:
		await message.delete()
		await message.author.send(embed = discord.Embed(description = f'Не надо писать плохие слова... :flushed:', color = 0x0c0c0c))
	
	
#Приветствие
@client.command(aliases = ['hi'])
async def hello(ctx):
	
	author = ctx.message.author
	await ctx.send(f'Привет {author.mention}! Нужна помощь - пиши !help в чат')
	

#Команда !help	
client.remove_command('help')
@client.command()
async def help(ctx):
	
	emb = discord.Embed(title = 'Помощь')
	
	emb.add_field(name = '{}hello'.format(PREFIX), value = ' - Поздороваться с ботом')
	emb.add_field(name = '{}join'.format(PREFIX), value = ' - Добавить бота в голосовой канал')
	emb.add_field(name = '{}leave'.format(PREFIX), value = ' - Убрать бота из голосового канала')
	emb.add_field(name = '{}play'.format(PREFIX), value = ' - Включить музыкальный трек(по youtube-ссылке)')
	emb.add_field(name = '{}pause'.format(PREFIX), value = ' - Поставить трек на паузу')
	emb.add_field(name = '{}resume'.format(PREFIX), value = ' - Возобновить трек')
	emb.add_field(name = '{}queue'.format(PREFIX), value = ' - Добавить трек в очередь (по youtube-ссылке)')
	emb.add_field(name = '{}skip'.format(PREFIX), value = ' - Включить следующий трек')
	emb.add_field(name = '{}stop'.format(PREFIX), value = ' - Остановить всю музыку')
	
	await ctx.send(embed = emb)
		
	
#Включение
token = open('token.txt','r').readline()

client.run(token)