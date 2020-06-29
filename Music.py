import discord
import shutil
import youtube_dl
import os
import sqlite3
from discord.ext import commands
from discord.utils import get
from os import system


#Сетап БД
DIR = os.path.dirname(__file__)
db = sqlite3.connect(os.path.join(DIR, 'MultiBOT_DB.db'))
SQL = db.cursor()


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client


    # Присоединение бота к голосовому чату
    @commands.command(pass_context=True)
    async def join(self, ctx):

        ###############################################################################################################################

        # Работа с БД
        SQL.execute('create table if not exists Music('
                    '"Num" integer not null primary key autoincrement, '
                    '"Guild_ID" integer, '
                    '"Guild_Name" text, '
                    '"Channel_ID" integer, '
                    '"Channel_Name" text, '
                    '"Username" text, '
                    '"Queue_Next" integer, '
                    '"Queue_Name" text, '
                    '"Song_Name" text'
                    ')')

        guild_id = ctx.guild.id
        guild_n = str(ctx.guild)

        SQL.execute(f'delete from Music where Guild_ID = "{guild_id}" and Guild_Name = "{guild_n}"')
        db.commit()

        channel_id = ctx.message.author.voice.channel.id
        channel_n = str(ctx.message.author.voice.channel)
        user_n = str(ctx.message.author)
        q_num = 1
        q_name = f'Queue#{guild_id}'
        song_n = f'Song#{guild_id}'

        SQL.execute(
            'insert into Music(Guild_ID, Guild_Name, Channel_ID, Channel_Name, Username, Queue_Next, Queue_Name, Song_Name) values(?,?,?,?,?,?,?,?)',
            (guild_id, guild_n, channel_id, channel_n, user_n, q_num, q_name, song_n))
        db.commit()

        ###############################################################################################################################


        channel = ctx.message.author.voice.channel
        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
        await ctx.send(embed=discord.Embed(description=f'Бот присоединился к каналу {channel}', color=0x0c0c0c))


    # Отсоединение бота от голосового чата
    @commands.command(pass_context=True)
    async def leave(self, ctx):

        ################################################################################################################################

        guild_id = ctx.guild.id
        guild_n = str(ctx.guild)
        channel_id = ctx.message.author.voice.channel.id
        channel_n = str(ctx.message.author.voice.channel)

        SQL.execute(
            f'delete from Music where Guild_ID = "{guild_id}" and Guild_Name = "{guild_n}" and Channel_ID = "{channel_id}" and Channel_Name = "{channel_n}"')
        db.commit()

        ################################################################################################################################


        channel = ctx.message.author.voice.channel
        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.disconnect()
            await ctx.send(embed=discord.Embed(description='Бот покинул канал', color=0x0c0c0c))
        else:
            await ctx.send(embed=discord.Embed(description='Бот не в канале!', color=0x0c0c0c))


    ####################################################################################################################################
    # Включить музыку
    @commands.command(pass_context=True)
    async def play(self, ctx, url: str):

        ################################################################################################################################

        guild_id = ctx.guild.id
        guild_n = str(ctx.guild)
        channel_id = ctx.message.author.voice.channel.id
        channel_n = str(ctx.message.author.voice.channel)

        try:
            SQL.execute(f'select Song_Name from Music where Guild_ID = "{guild_id}" and Guild_Name = "{guild_n}" and Channel_ID = "{channel_id}" and Channel_Name = "{channel_n}"')
            n_song = SQL.fetchone()
            SQL.execute(f'select Guild_Name from Music where Guild_ID = "{guild_id}" and Guild_Name = "{guild_n}"')
            n_guild = SQL.fetchone()
        except:
            return



        ################################################################################################################################

        def check_queue(self):

            ############################################################################################################################

            DIR = os.path.dirname(__file__)
            db = sqlite3.connect(os.path.join(DIR, 'MultiBOT_DB.db'))
            SQL = db.cursor()
            SQL.execute(f'select Queue_Name from Music where Guild_ID = "{guild_id}" and Guild_Name = "{guild_n}"')
            name_q = SQL.fetchone()
            SQL.execute(f'select Guild_Name from Music where Guild_ID = "{guild_id}" and Guild_Name = "{guild_n}"')
            n_guild = SQL.fetchone()

            ############################################################################################################################

            q_infile = os.path.isdir('./Queues')

            if q_infile is True:
                DIR = os.path.abspath(os.path.realpath('Queues'))
                q_main = os.path.join(DIR, name_q[0])
                # length = len(os.listdir(q_main))
                # still_q = length - 1
                q_main_infile = os.path.isdir(q_main)

                if q_main_infile is True:
                    length = len(os.listdir(q_main))
                    still_q = length - 1
                    try:
                        first_file = os.listdir(q_main)[0]
                        song_num = first_file.split('-')[0]
                    except:
                        print('[Log] Музыка: нет треков в очереди')
                        db.commit()
                        return

                    main_location = os.path.dirname(os.path.realpath(__file__))
                    song_path = os.path.abspath(os.path.realpath(q_main) + '\\' + first_file)

                    if length != 0:
                        print('[Log] Музыка: трек закончился, играет следующий')
                        print(f'[Log] Музыка: треков в очереди: {still_q}')
                        track_exist = os.path.isfile(f'{n_song[0]}({n_guild[0]}).mp3')

                        if track_exist:
                            os.remove(f'{n_song[0]}({n_guild[0]}).mp3')

                        shutil.move(song_path, main_location)

                        for file in os.listdir('./'):

                            if file == f'{song_num}-{n_song[0]}({n_guild[0]}).mp3':
                                os.rename(file, f'{n_song[0]}({n_guild[0]}).mp3')

                        voice.play(discord.FFmpegPCMAudio(f'{n_song[0]}({n_guild[0]}).mp3'),
                                   after=lambda e: check_queue(self))
                        voice.source = discord.PCMVolumeTransformer(voice.source)
                        voice.source.volume = 0.05

                    else:
                        SQL.execute('update Music set Queue_Next = 1 where Guild_ID = ? and Guild_Name = ?',
                                    (guild_id, guild_n))
                        db.commit()
                        return

                else:
                    SQL.execute('update Music set Queue_Next = 1 where Guild_ID = ? and Guild_Name = ?',
                                (guild_id, guild_n))
                    db.commit()
                    print('[Log] Музыка: в очереди не появлялось никаких треков')
            else:
                SQL.execute('update Music set Queue_Next = 1 where Guild_ID = ? and Guild_Name = ?',
                            (guild_id, guild_n))
                db.commit()
                print('[Log] Музыка: в очереди не появлялось никаких треков')


        track_exist = os.path.isfile(f'{n_song[0]}({n_guild[0]}).mp3')

        try:
            if track_exist:
                os.remove(f'{n_song[0]}({n_guild[0]}).mp3')
                SQL.execute('update Music set Queue_Next = 1 where Guild_ID = ? and Guild_Name = ?', (guild_id, guild_n))
                db.commit()
                print('[Log] Старый файл удалён')
        except PermissionError:
            print('[Log] Нельзя удалить трек, который проигрывается')
            await ctx.send(embed=discord.Embed(description='Музыка: ошибка: трек проигрывается', color=0x0c0c0c))
            return

        SQL.execute(f'select Queue_Name from Music where Guild_ID = "{guild_id}" and Guild_Name = "{guild_n}"')
        name_q = SQL.fetchone()
        q_infile = os.path.isdir('./Queues')

        if q_infile is True:
            DIR = os.path.abspath(os.path.realpath('Queues'))
            q_main = os.path.join(DIR, name_q[0])
            q_main_infile = os.path.isdir(q_main)

            if q_main_infile is True:
                print('[Log] Музыка: старая папка удалена')
                shutil.rmtree(q_main)

        await ctx.send(embed=discord.Embed(description='Музыка: ожидайте...', color=0x0c0c0c))

        voice = get(self.client.voice_clients, guild=ctx.guild)
        song_path = f'./{n_song[0]}({n_guild[0]}).mp3'

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': song_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print('[Log] Загружаем аудио')
                ydl.download([url])
            await ctx.send(embed=discord.Embed(description='Музыка: играет', color=0x0c0c0c))
            print('[Log] Музыка: играет')
        except:
            await ctx.send(embed=discord.Embed(description='Музыка: бот не поддерживает такие ссылки', color=0x0c0c0c))

        voice.play(discord.FFmpegPCMAudio(f'{n_song[0]}({n_guild[0]}).mp3'), after=lambda e: check_queue(self))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.05


    # Поставить музыку на паузу
    @commands.command(pass_context=True)
    async def pause(self, ctx):

        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            voice.pause()
            await ctx.send(embed=discord.Embed(description='Музыка: пауза', color=0x0c0c0c))
            print('[Log] Музыка: пауза')

        else:
            await ctx.send(embed=discord.Embed(description='Музыка: нечего ставить на паузу!', color=0x0c0c0c))
            print('[Log] Музыка: нечего ставить на паузу!')


    # Возобновить музыку
    @commands.command(pass_context=True)
    async def resume(self, ctx):

        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_paused():
            voice.resume()
            await ctx.send(embed=discord.Embed(description='Музыка: возобновлена', color=0x0c0c0c))
            print('[Log] Музыка: возобновлена')

        else:
            await ctx.send(embed=discord.Embed(description='Музыка: нечего возобновлять!', color=0x0c0c0c))
            print('[Log] Музыка: нечего возобновлять!')


    # Стоп музыки
    @commands.command(pass_context=True)
    async def stop(self, ctx):

        ################################################################################################################################

        guild_id = ctx.guild.id
        guild_n = str(ctx.guild)
        SQL.execute('update Music set Queue_Next = 1 where Guild_ID = ? and Guild_Name = ?', (guild_id, guild_n))
        db.commit()
        SQL.execute(f'select Queue_Name from Music where Guild_ID = "{guild_id}" and Guild_Name = "{guild_n}"')
        name_q = SQL.fetchone()

        ################################################################################################################################

        q_infile = os.path.isdir('./Queues')

        if q_infile is True:
            DIR = os.path.abspath(os.path.realpath('Queues'))
            q_main = os.path.join(DIR, name_q[0])
            q_main_infile = os.path.isdir(q_main)

            if q_main_infile is True:
                shutil.rmtree(q_main)

        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            voice.stop()
            await ctx.send(embed=discord.Embed(description='Музыка: стоп', color=0x0c0c0c))
            print('[Log] Музыка: стоп')

        else:
            await ctx.send(embed=discord.Embed(description='Музыка: нечего останавливать!', color=0x0c0c0c))
            print('[Log] Музыка: нечего останавливать!')

    # Очередь музыки
    @commands.command(pass_context=True)
    async def queue(self, ctx, url: str):

        ################################################################################################################################

        guild_id = ctx.guild.id
        guild_n = str(ctx.guild)
        try:
            SQL.execute(f'select Queue_Name from Music where Guild_ID = "{guild_id}" and Guild_Name = "{guild_n}"')
            name_q = SQL.fetchone()
            SQL.execute(f'select Song_Name from Music where Guild_ID = "{guild_id}" and Guild_Name = "{guild_n}"')
            n_song = SQL.fetchone()
            SQL.execute(f'select Queue_Next from Music where Guild_ID = "{guild_id}" and Guild_Name = "{guild_n}"')
            q_num = SQL.fetchone()
        except:
            return

        ################################################################################################################################

        q_infile = os.path.isdir('./Queues')

        if q_infile is False:
            os.mkdir('Queues')

        DIR = os.path.abspath(os.path.realpath('Queues'))
        q_main = os.path.join(DIR, name_q[0])
        q_main_infile = os.path.isdir(q_main)

        if q_main_infile is False:
            os.mkdir(q_main)

        SQL.execute(f'select Guild_Name from Music where Guild_ID = "{guild_id}" and Guild_Name = "{guild_n}"')
        n_guild = SQL.fetchone()
        queue_path = os.path.abspath(os.path.realpath(q_main) + f'\\{q_num[0]}-{n_song[0]}({n_guild[0]}).mp3')

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': queue_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print('[Log] Загружаем аудио')
                ydl.download([url])
            await ctx.send(
                embed=discord.Embed(description='Музыка: трек добавлен в очередь под номером ' + str(q_num[0]),
                                    color=0x0c0c0c))
            print('[Log] Музыка: трек добавлен в очередь')
        except:
            await ctx.send(embed=discord.Embed(description='Музыка: бот не поддерживает такие ссылки', color=0x0c0c0c))

        SQL.execute('update Music set Queue_Next = Queue_Next + 1 where Guild_ID = ? and Guild_Name = ?',
                    (guild_id, guild_n))

    # Следующий трек
    @commands.command(pass_context=True)
    async def skip(self, ctx):

        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            print('[Log] Музыка: следующий трек')
            voice.stop()
            await ctx.send(embed=discord.Embed(description='Музыка: следующий трек', color=0x0c0c0c))
            if voice and voice.is_playing():
                pass
            else:
                await ctx.send(embed=discord.Embed(description='Музыка: нет треков в очереди', color=0x0c0c0c))
                print('[Log] Музыка: нет треков в очереди')

        else:
            await ctx.send(embed=discord.Embed(description='Музыка: музыка не играет!', color=0x0c0c0c))
            print('[Log] Музыка: музыка не играет!')

# Работа с ошибками
    # Очистка чата
    @play.error
    async def play_error(self, ctx, error):

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(description='Укажите ссылку!',color=0x0c0c0c))

    @queue.error
    async def queue_error(self, ctx, error):

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(description='Укажите ссылку!', color=0x0c0c0c))


def setup(client):
    client.add_cog(Music(client))