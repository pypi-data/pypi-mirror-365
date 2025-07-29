import click
from pathlib import Path
from .cli_handler import CliHandler
from srtify.core.translator import TranslatorApp
from srtify.core.settings import SettingsManager
from srtify.core.prompts import PromptsManager


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """ Gemini SRT Translator - Translate subtitle files using AI """
    if ctx.invoked_subcommand is None:
        settings = SettingsManager()
        prompts = PromptsManager()
        cli_handler = CliHandler(settings, prompts)
        cli_handler.handle_main_menu()


@cli.command()
@click.option('--input', '-i', type=click.Path(path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output directory (default: from settings)')
@click.option('--language', '-l', help='Target language (default: from settings)')
@click.option('--file', '-f', help='Specific file to translate (default: all .srt files)')
@click.option('--prompt', '-p', help='Search for a specific prompt by name')
@click.option('--custom-prompt', help='Use a custom prompt')
@click.option('--batch-size', '-b', type=int, help='Batch size for translation')
@click.option('-quick', '-q', is_flag=True, help='Quick translation with default prompt')
def translate(input, output, language, file, prompt, custom_prompt, batch_size, quick):
    """ Translate SRT files from INPUT_PATH """
    settings = SettingsManager()
    prompts = PromptsManager()

    app = TranslatorApp(settings, prompts)

    options = {
        'input_path': input,
        'output_path': output,
        'language': language,
        'file': file,
        'prompt': prompt,
        'custom_prompt': custom_prompt,
        'batch_size': batch_size,
        'quick': quick
    }

    app.run_translation(options)


@cli.command()
def interactive():
    """ Start interactive translation mode ."""
    settings = SettingsManager()
    prompts = PromptsManager()
    cli_handler = CliHandler(settings, prompts)
    cli_handler.handle_main_menu()


@cli.command()
def settings():
    """ Configure application settings. """
    settings = SettingsManager()
    prompts = PromptsManager()
    cli_handler = CliHandler(settings, prompts)
    cli_handler.handle_settings_menu()


@cli.command()
def prompts():
    """ Manage translation prompts. """
    settings = SettingsManager()
    prompts = PromptsManager()
    cli_handler = CliHandler(settings, prompts)
    cli_handler.handle_prompts_menu()


@cli.command()
@click.argument('search_term')
def search_prompts(search_term):
    """ Search for prompts by name or description. """
    prompts = PromptsManager()
    results = prompts.search_prompts(search_term)

    if results:
        click.echo(f"Found {len(results)} prompts matching {search_term}...")
        for name, description in results.items():
            click.echo(f"   {name}: {description[:100]}{'...' if len(description) else ''}")
    else:
        click.echo(f"No prompts found matching '{search_term}'")


@cli.command()
def status():
    """ Show current configuration status. """
    settings = SettingsManager()
    prompts = PromptsManager()

    click.echo("=== Configuration Status ===")
    summary = settings.get_settings_summary()
    for key, value in summary.items():
        click.echo(f"  {key}: {value}")

    click.echo(f"\nPrompts: {prompts.count_prompts()} total")