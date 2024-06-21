import discord
import settings

async def send_stats(ctx, members, player_stats, resend=False):
    # do not allow stats to be greater than max
    for member in members:
        if player_stats[member]["curr_str"] > player_stats[member]["total_str"]:
            player_stats[member]["curr_str"] = player_stats[member]["total_str"]
        if player_stats[member]["curr_pow"] > player_stats[member]["total_pow"]:
            player_stats[member]["curr_pow"] = player_stats[member]["total_pow"]

        # create stats embed for each member
        embed=create_stat_embed(player_stats[member]["curr_str"], player_stats[member]["total_str"], \
                                player_stats[member]["curr_pow"], player_stats[member]["total_pow"])
        embed.set_author(name=member.name, url=None, icon_url=member.avatar)
        injuries = ', '.join([f'{key} ({value[0]})' if value[0] is not None else key for key, value in \
                              player_stats[member]["injuries"].items()])
        if player_stats[member]["injuries"] == {}:
            injuries = "-"
        embed.add_field(name="Injuries", value=injuries)

        # if change in stats, edit previous message
        if "message" in player_stats[member] and not resend:
            await player_stats[member]["message"].edit(embed=embed)
        else:
            # if resending to keep stats visible, delete and resend
            if resend:
                await player_stats[member]["message"].delete()
            player_stats[member]["message"] = await ctx.send(embed=embed)
            if type(ctx) == discord.Thread:
                settings.duels[ctx]["message_count"] = 0
            else:
                settings.duels[ctx.channel]["message_count"] = 0

async def check_end(ctx, members, player_stats):
    loser = []
    for member in members:
        # if stats 0 or below, declare loser
        if player_stats[member]["curr_str"] <= 0:
            loser.append(member)
            player_stats[member]["curr_str"] = 0
        if player_stats[member]["curr_pow"] <= 0:
            loser.append(member)
            player_stats[member]["curr_pow"] = 0
    await send_stats(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"])   

    # if both have a statistic as 0, declare tie
    if len(loser) == 2:
        await ctx.send(f"Both players {loser[0].mention} and {loser[1].mention} have depleted their strength or power. It's a tie.")
        del settings.duels[ctx.channel]
        return True
    # end game by declaring winner
    elif len(loser) == 1:
        winner = [member for member in members if loser[0] != member][0]
        await ctx.send(f"{winner.mention} has won! Better luck next time, {loser[0].mention}")
        del settings.duels[ctx.channel]
        return True
    return False

def create_stat_embed(current_strength, total_strength, current_power, total_power):
    # create bars to depict remaining strength and power in embed
    percentage = current_strength / total_strength
    white_length = int(percentage * 20)
    gray_length = 20 - white_length

    white_bar = '█' * white_length
    gray_bar = '░' * gray_length

    embed = discord.Embed(title="Player Stats", color=discord.Color.blue())
    embed.add_field(name=f"Strength: {current_strength} / {total_strength}", value=f"{white_bar}{gray_bar}", inline=False)

    percentage = current_power / total_power
    white_length = int(percentage * 20)
    gray_length = 20 - white_length

    white_bar = '█' * white_length
    gray_bar = '░' * gray_length

    embed.add_field(name=f"Power: {current_power} / {total_power}", value=f"{white_bar}{gray_bar}", inline=False)

    return embed

def create_user_stats(member_list, thread):
    settings.duels[thread]["player_stats"] = {}
    for member in member_list:
        settings.duels[thread]["player_stats"][member] = {
        "curr_str": 50,
        "total_str": 50,
        "curr_pow": 50,
        "total_pow": 50,
        "luck": 90,
        "injuries": {},
        # "message": 8563498 -> not real data: will be added in other code
        "energy": 3,
        "get_lucky": False,
    }