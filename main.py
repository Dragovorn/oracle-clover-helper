import json
import discord
from discord_slash import SlashCommand
from discord_slash.utils import manage_commands
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, JSONAttribute

type_dict = {
    'grass': 0x10c747,
    'electric': 0xd8e362,
    'fire': 0xFF7533,
    'water': 0x0af2f2,
    'dark': 0x3b0154,
    'fairy': 0xf77ce7,
    'normal': 0xc7c7c7,
    'flying': 0x66decc,
    'bug': 0xc0f545,
    'ice': 0xb3e7f2
}

with open('credentials.json', 'r') as cred:
    credentials = json.load(cred)

discord_token = credentials['discord_token']
aws_access = credentials['aws_access']
aws_secret_access = credentials['aws_secret_access']


class PokemonModel(Model):
    class Meta:
        table_name = 'pokemon'
        aws_access_key_id = aws_access
        aws_secret_access_key = aws_secret_access
    name = UnicodeAttribute(hash_key=True)
    game = UnicodeAttribute(null=True)
    region = UnicodeAttribute(null=True)
    type = JSONAttribute(null=True)
    display = JSONAttribute(null=True)
    evolution = JSONAttribute(null=True)
    stats = JSONAttribute(null=True)
    image_url = UnicodeAttribute(null=True)
    dex_number = NumberAttribute(null=True)


client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)
guild_ids = [461657565214801922, 796148649440313365]


@client.event
async def on_ready():
    print("Connected!")


@slash.slash(
    name='pokeinfo',
    description='Get information on a pokemon',
    options=[manage_commands.create_option(
        name='pokemon',
        description='Name of the pokemon',
        option_type=3,
        required=True
    )],
    guild_ids=guild_ids
)
async def _evolve(ctx, name: str):
    await ctx.respond()

    embed = discord.Embed(title=f'{name} Not Found in Database!', description='Please notify Andrew if the pokemon should exist', colour=0xFF0000)

    for pokemon in PokemonModel.query(name.lower()):
        embed.colour = type_dict[pokemon.first_type]
        embed.title = f'{pokemon.display_name}\'s (#{pokemon.dex_number}) Info:'
        embed.description = ''
        embed.add_field(name='Game', value=pokemon.display_game)
        embed.add_field(name='Region', value=pokemon.display_region)

        type_str = 'Type'

        if pokemon.second_type != 'NULL':
            type_str = 'Types'

        embed.add_field(name=type_str, value=pokemon.display_type)

        if pokemon.image_url != 'NULL':
            embed.set_image(url=pokemon.image_url)

        if pokemon.next_evolution_level > 0:
            embed.add_field(name='Evolves Into', value=f'{pokemon.next_evolution} @ lvl {pokemon.next_evolution_level}')

        if pokemon.previous_evolution_level > 0:
            embed.add_field(name='Evolves From', value=f'{pokemon.previous_evolution} @ lvl {pokemon.previous_evolution_level}')

    await ctx.send(embeds=[embed])

client.run(discord_token)
