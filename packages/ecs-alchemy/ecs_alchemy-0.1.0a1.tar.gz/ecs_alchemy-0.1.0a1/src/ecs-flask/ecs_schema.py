from odnd_tools.crud import *

def init_components():
    create_component("name","Name","name_data", "A name that the Entity calls itself or is called by others.")
    create_component("ability", "Ability Score", "ability_data", "A particular ability rated on a scale from 3-18.")
    create_component("moneybag", "Moneybag", "moneybag_data", "Pointer to an entity that has one or more Currency components.")
    create_component("currency", "Currency", "currency_data", "A certain amount of a particular currency.")

@click.command('init-components')
def init_components_command():
    init_components()
    click.echo('Initialized the components.')

def init_app(app):
    app.cli.add_command(init_components_command)