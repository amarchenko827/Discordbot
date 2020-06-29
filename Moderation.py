import discord
from discord.ext import commands
from discord.utils import get


class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client


    ####################################################################################################################
    # Команда выдачи мута (доступна только администраторам)
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def mute(self, ctx, member: discord.Member):

        admin_role = discord.utils.get(ctx.message.guild.roles, name='admin')
        user_role = discord.utils.get(ctx.message.guild.roles, name='User')
        mute_role = discord.utils.get(ctx.message.guild.roles, name='mute')
        if admin_role in member.roles:
            await ctx.send(embed = discord.Embed(description = 'Команды модерирования неприменимы к администрации!', color = 0x0c0c0c))
        else:
            await member.remove_roles(user_role)
            await member.add_roles(mute_role)
            await ctx.send(embed = discord.Embed(description = f'{member.mention} получил мут! :shushing_face:', color = 0x0c0c0c))


    # Команда удаления мута (доступна только администраторам)
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def unmute(self, ctx, member: discord.Member):

        admin_role = discord.utils.get(ctx.message.guild.roles, name='admin')
        user_role = discord.utils.get(ctx.message.guild.roles, name='User')
        mute_role = discord.utils.get(ctx.message.guild.roles, name='mute')
        if admin_role in member.roles:
            await ctx.send(embed = discord.Embed(description = 'Команды модерирования неприменимы к администрации!', color = 0x0c0c0c))
        else:
            await member.remove_roles(mute_role)
            await member.add_roles(user_role)
            await ctx.send(embed = discord.Embed(description = f'{member.mention} снова может говорить! :open_mouth:', color = 0x0c0c0c))


    # Команда выдачи кика (доступна только администраторам)
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def kick(self, ctx, member: discord.Member, *, reason = 'Нет'):

        admin_role = discord.utils.get(ctx.message.guild.roles, name='admin')

        if admin_role in member.roles:
            await ctx.send(embed = discord.Embed(description = 'Команды модерирования неприменимы к администрации!', color = 0x0c0c0c))
        else:
            await member.send(f'Вы были кикнуты с сервера {member.guild.name}. Причина: {reason}')
            await member.kick(reason = reason)
            await ctx.send(embed = discord.Embed(description = f'{member.mention} был кикнут с нашего сервера. :confused:', color = 0x0c0c0c))


    # Команда выдачи бана (доступна только администраторам)
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def ban(self, ctx, member: discord.Member, *, reason='Нет'):

        admin_role = discord.utils.get(ctx.message.guild.roles, name='admin')

        if admin_role in member.roles:
            await ctx.send(embed = discord.Embed(description = 'Команды модерирования неприменимы к администрации!', color = 0x0c0c0c))
        else:
            await member.send(f'Вы были забанены на сервере {member.guild.name}. Причина: {reason}')
            await member.ban(reason = reason)
            await ctx.send(embed = discord.Embed(description = f'{member.mention} был забанен на нашем сервере. :cold_sweat:', color = 0x0c0c0c))


    # Команда удаления бана (доступна только администраторам)
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def unban(self, ctx, *, member):

        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(embed = discord.Embed(description = f'{user.mention} был разбанен на нашем сервере. :thinking:', color = 0x0c0c0c))
                return
            else:
                await ctx.send(
                    embed=discord.Embed(description='Такого пользователя нет в списке. :thinking:',
                                        color=0x0c0c0c))
                return


    # Команда для получения списка забаненных пользователей (доступна только администраторам)
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def banlist(self, ctx):

        banned_users = await ctx.guild.bans()
        pretty_list = ['{0.name}#{0.discriminator} | '.format(entry.user) + 'Причина: {0.reason}'.format(entry) for entry in banned_users]

        await ctx.send(embed = discord.Embed(description = 'Бан лист: \n{}'.format('\n'.join(pretty_list)), color = 0x0c0c0c))


    # Команда очистки чата (доступна только администраторам)
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, amount: int):

        await ctx.channel.purge(limit = amount)

        amount = str(amount)
        await ctx.send(embed = discord.Embed(description = 'Сообщений очищено: ' + amount, color = 0x0c0c0c))


    ####################################################################################################################
    # Работа с ошибками
    # Очистка чата
    @clear.error
    async def clear_error(self, ctx, error):

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(description='Не указано количество сообщений, которые нужно удалить!',
                                               color=0x0c0c0c))

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(description='У вас недостаточно прав для использования этой команды!',
                                               color=0x0c0c0c))


    # Мут/размут
    @mute.error
    async def mute_error(self, ctx, error):

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(description='Укажите, кому нужно дать мут!',
                                               color=0x0c0c0c))

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(description='У вас недостаточно прав для использования этой команды!',
                                               color=0x0c0c0c))

    @unmute.error
    async def unmute_error(self, ctx, error):

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(description='Укажите, у кого нужно убрать мут!',
                                               color=0x0c0c0c))

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(description='У вас недостаточно прав для использования этой команды!',
                                               color=0x0c0c0c))

    # Кик
    @kick.error
    async def kick_error(self, ctx, error):

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(description='Укажите, кого нужно кикнуть!',
                                               color=0x0c0c0c))

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(description='У вас недостаточно прав для использования этой команды!',
                                               color=0x0c0c0c))

    # Бан/разбан/бан-лист
    @ban.error
    async def ban_error(self, ctx, error):

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(description='Укажите, кого нужно забанить!',
                                               color=0x0c0c0c))

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(description='У вас недостаточно прав для использования этой команды!',
                                               color=0x0c0c0c))

    @unban.error
    async def unban_error(self, ctx, error):

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(description='Напишите, кого нужно разбанить (никнейм#тэг)!',
                                               color=0x0c0c0c))

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(description='У вас недостаточно прав для использования этой команды!',
                                               color=0x0c0c0c))

    @banlist.error
    async def banlist_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(description='У вас недостаточно прав для использования этой команды!',
                                               color=0x0c0c0c))

########################################################################################################################


def setup(client):
    client.add_cog(Moderation(client))