import json
import discord
from discord_slash import SlashCommand
from discord_slash.utils import manage_commands
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute

type_dict = {
    'fire': 0xFF7533
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
    first_type = UnicodeAttribute(null=True)
    second_type = UnicodeAttribute(null=True)
    display_name = UnicodeAttribute(null=True)
    display_game = UnicodeAttribute(null=True)
    display_region = UnicodeAttribute(null=True)
    display_type = UnicodeAttribute(null=True)
    next_evolution = UnicodeAttribute(null=True)
    previous_evolution = UnicodeAttribute(null=True)
    image_url = UnicodeAttribute(null=True)
    next_evolution_level = NumberAttribute(null=True)
    previous_evolution_level = NumberAttribute(null=True)
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