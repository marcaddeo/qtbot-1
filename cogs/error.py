#!/bin/env python

import discord.ext
import sys
import traceback


class ErrorHandler:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        """ Handle command errors more gracefully """

        if isinstance(error, discord.ext.commands.CommandNotFound):
            return

        if isinstance(error, discord.ext.commands.errors.NotOwner):
            return await ctx.send('Sorry, only the owner of qtbot may run this command.')

        if isinstance(error, discord.ext.commands.CommandOnCooldown):
            return await ctx.send(f'This command is on cooldown. Please retry in `{error.retry_after:.0f}` second(s).')

        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            return await ctx.send(f'Command missing required argument `{error.param}`.')

        if isinstance(error, discord.ext.commands.errors.MissingPermissions):
            return await ctx.send(f'Sorry you need permissions: `{",".join(error.missing_perms)}` to do that.')

        if isinstance(error, discord.ext.commands.errors.BotMissingPermissions):
            return await ctx.send(f'Sorry I need permissions: `{",".join(error.missing_perms)}` to do that.')

        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
