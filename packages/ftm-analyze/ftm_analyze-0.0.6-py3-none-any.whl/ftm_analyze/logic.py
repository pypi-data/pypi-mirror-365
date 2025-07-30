from typing import Generator, Iterable

from anystore.decorators import error_handler
from anystore.io import logged_items
from anystore.logging import get_logger
from followthemoney.proxy import EntityProxy

from ftm_analyze.analysis.analyzer import Analyzer
from ftm_analyze.settings import Settings

log = get_logger(__name__)
settings = Settings()


@error_handler(logger=log)
def analyze_entity(
    entity: EntityProxy,
    resolve_mentions: bool | None = settings.resolve_mentions,
    annotate: bool | None = settings.annotate,
) -> Generator[EntityProxy, None, None]:
    """
    Analyze an Entity.

    Args:
        entity: The entity proxy
        resolve_mentions: Convert known mentions into its actual entities via
            `juditha`
        annotate: Annotate extracted patterns, names and mentions in `indexText`

    Yields:
        A generator of entity fragments
    """
    analyzer = Analyzer(entity, resolve_mentions, annotate)
    analyzer.feed(entity)
    yield from analyzer.flush()


def analyze_entities(
    entities: Iterable[EntityProxy],
    resolve_mentions: bool | None = settings.resolve_mentions,
    annotate: bool | None = settings.annotate,
) -> Generator[EntityProxy, None, None]:
    for e in logged_items(entities, "Analyze", item_name="Entity", logger=log):
        yield from analyze_entity(e, resolve_mentions, annotate)
