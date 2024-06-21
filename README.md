Wizardry Warzone Bot is an interactive Discord bot that facilitates duels between users with various commands for attacking, defending, and using special abilities.

## Features

- **Duel initiation**: Start a duel with another user.
- **Combat commands**: Perform actions like disarming, striking, shielding, etc.
- **Interactive counters**: Counter spells and attacks within a specified time window.
- **Statistics tracking**: Maintain and display the current status and stats of duel participants.

## Prerequisites

- Python 3.8+
- Discord.py
- Numpy

## Usage

Use the following commands in your Discord server to interact with the bot:

- `!duel @username` - Challenge a user to a duel.
- `!disarm` - Disarm your opponent. Costs 2 power points. Can be countered with `!shield` within 5 seconds. If not countered, opponent loses 3 strength points and cannot cast for 10 seconds.
- `!strike` - Strike your opponent. Costs 1 strength point. Deals 0-5 strength points damage to opponent, based on weighted probability.
- `!shield` - Shield yourself. Costs 1 power point. Can counter disarm attacks within 5 seconds.
- `!fire` - Cast a fire spell on your opponent. Costs 2 power points. Deals 3 strength and power points damage.
- `!heal` - Heal yourself. If you have burns, removes them and restores 1 strength and power point. Otherwise, costs 1 power point.
- `!energize` - Energize yourself. Restores 5 strength and power points. Limited to 3 uses per duel.
- `!dodge` - Attempt to dodge an attack. Costs 1 strength point. Success based on luck.
- `!quit` - Forfeit the duel.
- `!help` - Show available commands and their descriptions.
