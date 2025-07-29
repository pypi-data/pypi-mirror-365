import sys
from typing import Annotated

import cyclopts

from liblaf import grapes
from liblaf.tangerine import core
from liblaf.tangerine._version import __version__

app = cyclopts.App(name="tangerine", version=__version__)


@app.meta.default
def _(
    *tokens: Annotated[str, cyclopts.Parameter(show=False, allow_leading_hyphen=True)],
) -> None:
    grapes.logging.init()
    return app(tokens)


@app.default
def _(
    file: Annotated[
        cyclopts.types.ResolvedExistingFile | None, cyclopts.Argument()
    ] = None,
    /,
    *,
    in_place: Annotated[bool, cyclopts.Parameter()] = True,
) -> None:
    env: core.Environment = core.Environment()
    text: str = sys.stdin.read() if file is None else file.read_text()
    segments: list[core.Segment] = env.parse_text(text)
    if in_place and file is not None:
        file.write_text(env.render(segments))
    else:
        print(env.render(segments), end="")
