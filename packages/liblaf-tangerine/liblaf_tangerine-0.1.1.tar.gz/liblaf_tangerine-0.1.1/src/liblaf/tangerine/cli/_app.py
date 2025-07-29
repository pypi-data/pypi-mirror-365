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
    file: Annotated[cyclopts.types.ResolvedExistingFile, cyclopts.Argument()],
    /,
    *,
    in_place: Annotated[bool, cyclopts.Parameter()] = True,
) -> None:
    env: core.Environment = core.Environment()
    segments: list[core.Segment] = env.parse_text(file.read_text())
    if in_place:
        file.write_text(env.render(segments))
    else:
        print(env.render(segments), end="")
