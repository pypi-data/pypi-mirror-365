import itertools
from pathlib import Path

import attrs
import cytoolz as toolz
import git
import jinja2
import platformdirs
from loguru import logger

from liblaf import grapes
from liblaf.tangerine import utils

from .constants import TANGERINE_END, TANGERINE_START
from .template import Template

type Segment = str | Template


def load_copier_answers() -> dict[str, str]:
    try:
        repo = git.Repo(search_parent_directories=True)
        cwd = Path(repo.working_dir)
    except git.InvalidGitRepositoryError:
        cwd = Path()
    answers: dict[str, str] = {}
    for file in itertools.chain(
        cwd.rglob(".copier-answers.*.yaml"),
        cwd.rglob(".copier-answers.*.yml"),
        cwd.rglob(".copier-answers.yaml"),
        cwd.rglob(".copier-answers.yml"),
    ):
        answers.update(grapes.load(file))
    answers = toolz.keyfilter(lambda k: not k.startswith("_"), answers)
    return answers


def _default_environment() -> jinja2.Environment:
    loaders: list[jinja2.BaseLoader] = []
    dirs: platformdirs.AppDirs = utils.app_dirs()
    for config_dir in dirs.iter_config_paths():
        templates_dir: Path = config_dir / "templates"
        if not templates_dir.exists():
            continue
        loaders.append(jinja2.FileSystemLoader(templates_dir))
    return jinja2.Environment(
        undefined=jinja2.StrictUndefined,
        autoescape=jinja2.select_autoescape(),
        loader=jinja2.ChoiceLoader(
            [*loaders, jinja2.PackageLoader("liblaf.tangerine")]
        ),
    )


@attrs.define
class Environment:
    context: dict[str, str] = attrs.field(factory=load_copier_answers)
    jinja: jinja2.Environment = attrs.field(factory=_default_environment)

    def parse_text(self, text: str) -> list[Segment]:
        lines: list[str] = text.splitlines()
        segments: list[Segment] = []
        in_template: bool = False
        template_lines: list[str] = []
        for line in lines:
            if in_template:
                template_lines.append(line)
                if TANGERINE_END in line:
                    segments.append(Template.from_lines(template_lines))
                    in_template = False
            elif TANGERINE_START in line:
                in_template = True
                template_lines.append(line)
            else:
                segments.append(line)
        return segments

    def render(self, segments: list[Segment], **kwargs: str) -> str:
        lines: list[str] = []
        for segment in segments:
            if isinstance(segment, Template):
                lines.append(self.render_template(segment, **kwargs))
            else:
                lines.append(segment)
        text: str = "\n".join(lines)
        if not text.endswith("\n"):
            text += "\n"
        return text

    def render_template(self, template: Template, **kwargs: str) -> str:
        try:
            template_jinja: jinja2.Template = self.jinja.get_template(template.name)
        except jinja2.TemplateNotFound as err:
            for template_name in err.templates:
                logger.warning("Template not found: {}", template_name)
            return "\n".join(template.lines)
        kwargs = toolz.merge(self.context, template.context, kwargs)
        rendered: str = template_jinja.render(kwargs).strip()
        lines: list[str] = rendered.splitlines()
        if "-*-" in lines[0]:
            lines = lines[1:]
        rendered = "\n".join(lines).strip()
        rendered = template.lines[0] + "\n" + rendered + "\n" + template.lines[-1]
        return rendered
