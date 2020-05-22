from datetime import datetime, timedelta
import shelve
import sys
import traceback


from discord.ext import commands
from datetimerange import DateTimeRange
from timefhuman import timefhuman

from scheduler.scheduler import find_times, filter_times


SIXTY_SIX = "https://pa1.narvii.com/7235/5ceb289c2b7953a679dafaf9fc7f4f6ab0afc394r1-480-208_hq.gif"

class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.errors = 0
        self.players = shelve.open("shelf", writeback=True)

    @commands.command()
    async def free(self, ctx, *, when):
        """specify a time range when you are free

        e.g. "$free tomorrow 10am-12pm" or "$free friday 5:30-7pm"
        """
        try:
            result = timefhuman(when)
            if not result:
                raise Exception(f"no times found ({when})")
            if not isinstance(result, tuple) or len(result) != 2 or result[0] >= result[1]:
                raise Exception(f"can't make range ({result})")
            timerange = DateTimeRange(*result)
            week = DateTimeRange(datetime.now(), datetime.now() + timedelta(days=7))
            if timerange not in week:
                raise Exception(f"range outside of next 7 days ({timerange})")
        except Exception as exc:
            print(f"error: {exc} ({when}):")
            traceback.print_exc(file=sys.stdout)
            return await ctx.send(f"error: {exc}")

        if self.players.get(ctx.message.author.name, None):
            self.players[ctx.message.author.name].append(timerange)
        else:
            self.players[ctx.message.author.name] = [timerange]

        return await ctx.send(f"added: {timerange}")

    @commands.command()
    async def when(self, ctx, people=4, duration=1.5):
        """find times that work for multiple people

        this will timeranges of at least <duration> length in which at
        least <people> number of players are free

        e.g. "$when" "$when 3", or "$when 2 4"
        """
        if people == 66:
            return await ctx.send(SIXTY_SIX)

        result = filter_times(find_times(self.players, people), duration)

        sorted_result = {}
        for k in sorted(result, key=len, reverse=True):
            sorted_result[k] = result[k]

        msg = [f"possible times for ⩾**{people}** players for ⩾**{duration}**h:\n"]
        for players, times in sorted_result.items():
            msg.append(f"_{', '.join(players)}_ at:")
            msg.extend(format_ranges(times))

        return await ctx.send("\n".join(msg))

    @commands.command()
    async def list(self, ctx, who=None):
        """list when you or others are marked as free

        e.g. "$list" "$list Jon", or "$list all"
        """
        if not who:
            who = [ctx.message.author.name]
        elif who == "all":
            who = self.players.keys()
        else:
            who = [who]

        msg = [f"possible times:\n"]
        for player in who:
            msg.append(f"_{player}_ at:")
            msg.extend(format_ranges(self.players[player]))

        await ctx.send("\n".join(msg))

    @commands.command()
    async def delete(self, ctx, which, who=None):
        """delete when you or others are marked as free

        e.g. "$delete 1", "$delete all", "$delete 1 Jon"
        """
        if not who:
            who = ctx.message.author.name
        if which == "all":
            self.players[who].clear()
            await ctx.send(f"removed: all")
        else:
            timerange = self.players[who].pop(int(which) - 1)
            await ctx.send(f"removed: {timerange}")


def format_ranges(ranges):
    msg = list()

    if not ranges:
        msg.append("• none")
        return msg

    for i, timerange in enumerate(ranges):

        timerange.start_time_format = "%a"
        day = timerange.get_start_time_str()

        timerange.start_time_format = "%d"
        date = timerange.get_start_time_str()
        date_suffix = (
            "th"
            if 11 <= int(date) <= 13
            else {1: "st", 2: "nd", 3: "rd"}.get(int(date) % 10, "th")
        )

        timerange.start_time_format = "%H:%M"
        timerange.end_time_format = "%H:%M"
        time_start = timerange.get_start_time_str()
        time_end = timerange.get_end_time_str()

        msg.append(
            f" • `{i+1:02}`  {day} {date}{date_suffix} @ {time_start} - {time_end}"
        )
    return msg