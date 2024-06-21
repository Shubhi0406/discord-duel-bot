# required dependencies
import discord
from discord.ext import commands
from Buttons import *
import stats
import numpy

# bot token
from apikeys import BOTTOKEN

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
client.remove_command('help')

@client.event
async def on_ready():
    print("The bot is ready!")
    print("------------------------------")
    await client.tree.sync()

# reduce strength for burns injury
@client.event
async def on_command(ctx):
    if ctx.channel in settings.duels and ctx.author in settings.duels[ctx.channel]["members"] \
        and "Disarmed" not in settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]:
        if "Burns" in settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]:
            settings.duels[ctx.channel]["player_stats"][ctx.author]["curr_str"] \
                -= settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]["Burns"][1]
            if await stats.check_end(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"]):
                return

# resend stats to keep them visible
@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.channel in settings.duels and "message_count" in settings.duels[message.channel]:
        settings.duels[message.channel]["message_count"] += 1
        
        if settings.duels[message.channel]["message_count"] > 5:
            await stats.send_stats(message.channel, settings.duels[message.channel]["members"], \
                                   settings.duels[message.channel]["player_stats"], resend=True)

@client.hybrid_command(name="duel", description="Sets up a duel with another user.")
async def duel(ctx, member: discord.Member):
    if str(ctx.channel.type) == "public_thread" or str(ctx.channel.type) == "private_thread":
        await ctx.reply("Sorry, you cannot create a duel in a thread.")
        return
    initiator = ctx.author
    
    if initiator == member:
        await ctx.reply("You cannot duel yourself.")
        return
    # bot ID
    elif ctx.guild.get_member(1239440944408039485) == member:
        await ctx.reply("Sorry, you cannot duel me. That wouldn't be fair to you.")
        return
    else:
        duel_message = f"{initiator.name} has challenged {member} to a duel!"
        await ctx.reply(duel_message + f" {member.mention}, do you accept?", view=Buttons(ctx, member))
        return

@client.command()
async def disarm(ctx):
    if ctx.channel in settings.duels and ctx.author in settings.duels[ctx.channel]["members"] \
        and "Disarmed" not in settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]:
        settings.duels[ctx.channel]["player_stats"][ctx.author]["curr_pow"] -= 2
        if await stats.check_end(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"]):
            return
        
        victim = [member for member in settings.duels[ctx.channel]["members"] if member != ctx.author][0]
        if "Disarmed" in settings.duels[ctx.channel]["player_stats"][victim]["injuries"]:
            await ctx.send(f"{victim.name} is already disarmed.")
            return
        
        # wait 5 secs for counterspell
        settings.duels[ctx.channel]["player_stats"][victim]["injuries"]["Disarmed?"] = ('5 secs', 0, datetime.now())
        await stats.send_stats(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"])

        await asyncio.sleep(5)
        if "Disarmed?" not in settings.duels[ctx.channel]["player_stats"][victim]["injuries"]:
            return
        del settings.duels[ctx.channel]["player_stats"][victim]["injuries"]["Disarmed?"]
        settings.duels[ctx.channel]["player_stats"][victim]["injuries"]["Disarmed"] = ('10 secs', 3, datetime.now())
        settings.duels[ctx.channel]["player_stats"][victim]["curr_str"] -= 3
        if await stats.check_end(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"]):
            return
        await ctx.send(f"{victim.name} is disarmed and cannot cast for 10 seconds.")
        await asyncio.sleep(10)

        # remove disarmed injury after 10 secs
        del settings.duels[ctx.channel]["player_stats"][victim]["injuries"]["Disarmed"]
        await ctx.send(f"{victim.name} is no longer disarmed.")
        await stats.send_stats(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"])


@client.command()
async def shield(ctx):
    if ctx.channel in settings.duels and ctx.author in settings.duels[ctx.channel]["members"] \
        and "Disarmed" not in settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]:
        settings.duels[ctx.channel]["player_stats"][ctx.author]["curr_pow"] -= 1
        # blocks potential disarm injury
        if "Disarmed?" in settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]:
            del settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]["Disarmed?"]
        if await stats.check_end(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"]):
            return

@client.command()
async def fire(ctx):
    if ctx.channel in settings.duels and ctx.author in settings.duels[ctx.channel]["members"] \
        and "Disarmed" not in settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]:
        settings.duels[ctx.channel]["player_stats"][ctx.author]["curr_pow"] -= 2
        if await stats.check_end(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"]):
            return
        victim = [member for member in settings.duels[ctx.channel]["members"] if member != ctx.author][0]
        # adds potential burns injury
        settings.duels[ctx.channel]["player_stats"][victim]["injuries"]["Burns?"] = ('5 secs', 0, datetime.now())
        await stats.send_stats(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"])
        await asyncio.sleep(5)
        if "Burns?" not in settings.duels[ctx.channel]["player_stats"][victim]["injuries"]:
            return
        
        # confirms burns injury after 5 secs
        del settings.duels[ctx.channel]["player_stats"][victim]["injuries"]["Burns?"]
        if "Burns" in settings.duels[ctx.channel]["player_stats"][victim]["injuries"]:
            curr_dec = settings.duels[ctx.channel]["player_stats"][victim]["injuries"]["Burns"][1]
            if curr_dec < 3:
                settings.duels[ctx.channel]["player_stats"][victim]["injuries"]["Burns"] \
                    = (f'{curr_dec + 1} strength penalty', curr_dec + 1)
        else:
            settings.duels[ctx.channel]["player_stats"][victim]["injuries"]["Burns"] = ('1 strength penalty', 1, datetime.now())
        settings.duels[ctx.channel]["player_stats"][victim]["curr_str"] -= 3
        settings.duels[ctx.channel]["player_stats"][victim]["curr_pow"] -= 3
        if await stats.check_end(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"]):
            return

@client.command()
async def heal(ctx):
    if ctx.channel in settings.duels and ctx.author in settings.duels[ctx.channel]["members"] \
        and "Disarmed" not in settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]:
        # removes burns and inc strength and power
        if "Burns" in settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]:
            del settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]["Burns"]
            settings.duels[ctx.channel]["player_stats"][ctx.author]["curr_str"] += 1
            settings.duels[ctx.channel]["player_stats"][ctx.author]["curr_pow"] += 1
            await stats.send_stats(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"])
        else:
            # penalty for using heal without burns
            settings.duels[ctx.channel]["player_stats"][ctx.author]["curr_pow"] -= 1
            if await stats.check_end(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"]):
                return
            
@client.command()
async def strike(ctx):
    if ctx.channel in settings.duels and ctx.author in settings.duels[ctx.channel]["members"]:
        settings.duels[ctx.channel]["player_stats"][ctx.author]["curr_str"] -= 1

        # damage based on weighted probability
        damage = numpy.random.choice(numpy.arange(0, 6), p=[0.1, 0.2, 0.3, 0.25, 0.1, 0.05])
        victim = [member for member in settings.duels[ctx.channel]["members"] if member != ctx.author][0]
        settings.duels[ctx.channel]["player_stats"][victim]["curr_str"] -= damage
        if await stats.check_end(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"]):
            return

@client.command()
async def energize(ctx):
    if ctx.channel in settings.duels and ctx.author in settings.duels[ctx.channel]["members"]:
        # Can use this spell 3 times max
        if settings.duels[ctx.channel]["player_stats"][ctx.author]["energy"] <= 0:
            await ctx.reply("You have exhausted all your energy spell casts.")
            return
        
        # energizes and decreases number of casts left
        settings.duels[ctx.channel]["player_stats"][ctx.author]["curr_str"] += 5
        settings.duels[ctx.channel]["player_stats"][ctx.author]["curr_pow"] += 5
        settings.duels[ctx.channel]["player_stats"][ctx.author]["energy"] -= 1
        await stats.send_stats(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"])
        

@client.command()
async def dodge(ctx):
    if ctx.channel in settings.duels and ctx.author in settings.duels[ctx.channel]["members"]:
        settings.duels[ctx.channel]["player_stats"][ctx.author]["curr_str"] -= 1
        if await stats.check_end(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"]):
            return
        
        # uses random to decide success of dodge - based on luck
        if numpy.random.choice(numpy.arange(1, 101)) > settings.duels[ctx.channel]["player_stats"][ctx.author]["luck"]:
            return
        
        # decreases luck by 10, minimum 40
        if settings.duels[ctx.channel]["player_stats"][ctx.author]["luck"] >= 50:
            settings.duels[ctx.channel]["player_stats"][ctx.author]["luck"] -= 10

        # successfully dodges the first cast injury
        first_inj = None
        if "Disarmed?" in settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]:
            first_inj = "Disarmed?"
        if "Burns?" in settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]:
            if (not first_inj) or settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]["Burns?"][2] \
                < settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"][first_inj][2]:
                first_inj = "Burns?"
        if first_inj and first_inj in settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"]:
            del settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"][first_inj]
        await stats.send_stats(ctx, settings.duels[ctx.channel]["members"], settings.duels[ctx.channel]["player_stats"])

@client.command()
async def luck(ctx):
    if ctx.channel in settings.duels and ctx.author in settings.duels[ctx.channel]["members"] \
        and "Disarmed" not in settings.duels[ctx.channel]["player_stats"][ctx.author]["injuries"] \
            and not settings.duels[ctx.channel]["player_stats"][ctx.author]["get_lucky"]:
        # increases luck to 100 and marks this spell as used
        settings.duels[ctx.channel]["player_stats"][ctx.author]["luck"] = 100
        settings.duels[ctx.channel]["player_stats"][ctx.author]["get_lucky"] = True

@client.hybrid_command(name="quit", description="Forfeits the current duel.")
async def quit(ctx):
    if ctx.channel in settings.duels and ctx.author in settings.duels[ctx.channel]["members"]:
        winner = [member for member in settings.duels[ctx.channel]["members"] if ctx.author != member][0]
        await ctx.send(f"{ctx.author.mention} has forfeited. {winner.mention} has won!")
        del settings.duels[ctx.channel]

@client.hybrid_command(name='help', description="Learn about the available commands.")
async def help(ctx):
    embed = discord.Embed(title="Bot Commands", description="", color=discord.Color.blue())
    
    # Categories and commands
    commands_info = [
        {"name": "duel", "description": "Sets up a duel with another user. Also available as a slash command. Cannot be used in a thread.", "usage": "!duel @username"},
        {},
        {"name": "quit", "description": "Forfeits the current duel. Also available as a slash command.", "usage": "!quit"},
        {"name": "disarm", "description": "Disarm an opponent. Costs 2 power to cast. Can be countered with shield if cast within 5 seconds. Can dodge within 5 seconds but success is based on chance. Decreases strength if failed to counter and stops opponent from casting for 10 seconds.", "usage": "!disarm"},
        {"name": "shield", "description": "Shield yourself. Costs 1 power to cast. Can counter 'disarm' spell if cast within 5 seconds.", "usage": "!shield"},
        {"name": "fire", "description": "Cast a fire spell on an opponent. Costs 2 power to cast. Can dodge within 5 seconds but success is based on chance. Reduces opponent's strength and power penalties and inflicts lasting burns causing strength penalty on every turn.", "usage": "!fire"},
        {"name": "heal", "description": "Heal yourself. Removes burn effect and slightly increases strength and power. If no burns, costs 1 power to cast.", "usage": "!heal"},
        {"name": "strike", "description": "Strike an opponent. Costs 1 strength to cast. Deals 0-5 damage to the opponent with variable probability.", "usage": "!strike"},
        {"name": "energize", "description": "Energize yourself. Increases strength and power by 5. Can be used up to 3 times.", "usage": "!energize"},
        {"name": "dodge", "description": "Dodge an attack. Costs 1 strength. Success is based on luck. Each successful dodge reduces luck.", "usage": "!dodge"},
        {"name": "luck", "description": "Significantly increase your luck for the next dodge. Can be used once.", "usage": "!luck"}
    ]
    
    for cmd in commands_info:
        if cmd == {}:
            embed.add_field(name=f"**\nMid-Duel Commands:**", value=f"", inline=False)
            continue
        embed.add_field(name=f"{cmd['name']}", value=f"{cmd['description']}\nUsage: `{cmd['usage']}`", inline=False)
    
    await ctx.send(embed=embed)

client.run(BOTTOKEN)
