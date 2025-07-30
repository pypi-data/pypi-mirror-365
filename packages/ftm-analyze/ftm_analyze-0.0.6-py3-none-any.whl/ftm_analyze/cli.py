from typing import Optional

import typer
from anystore.cli import ErrorHandler
from anystore.logging import configure_logging, get_logger
from ftmq.io import smart_read_proxies, smart_write_proxies
from rich.console import Console
from spacy.cli.download import download
from typing_extensions import Annotated

from ftm_analyze import __version__, logic
from ftm_analyze.settings import Settings

settings = Settings()
cli = typer.Typer(
    no_args_is_help=True,
    pretty_exceptions_enable=True,
    pretty_exceptions_short=not settings.debug,
)
console = Console(stderr=True)

log = get_logger(__name__)

IN = Annotated[
    str, typer.Option(..., "-i", help="Input entities uri (file, http, s3...)")
]
OUT = Annotated[
    str, typer.Option(..., "-o", help="Output entities uri (file, http, s3...)")
]


@cli.callback(invoke_without_command=True)
def cli_base(
    version: Annotated[Optional[bool], typer.Option(..., help="Show version")] = False,
    settings: Annotated[
        Optional[bool], typer.Option(..., help="Show current settings")
    ] = False,
):
    if version:
        print(__version__)
        raise typer.Exit()
    if settings:
        print(Settings())
        raise typer.Exit()
    configure_logging()


@cli.command("download-spacy")
def cli_download():
    """
    Download required spacy models based on current settings
    """
    console.print(settings.ner_models)
    models = settings.ner_models.model_dump()
    for model in models.values():
        download(model)


@cli.command("analyze")
def cli_analyze(
    in_uri: IN = "-",
    out_uri: OUT = "-",
    resolve_mentions: Annotated[
        bool, typer.Option(help="Resolve known mentions via `juditha`")
    ] = True,
    annotate: Annotated[
        bool, typer.Option(help="Annotate extracted patterns, names and mentions")
    ] = True,
):
    """
    Analyze a stream of entities.
    """
    with ErrorHandler(log):
        entities = smart_read_proxies(in_uri)
        results = logic.analyze_entities(entities, resolve_mentions, annotate)
        smart_write_proxies(out_uri, results)
