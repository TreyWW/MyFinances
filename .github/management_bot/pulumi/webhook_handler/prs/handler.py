import os
import re
from textwrap import dedent
import logging

logger = logging.getLogger(__name__)
if os.environ.get("AWS_EXECUTION_ENV") is not None:
    import _types
else:
    from .. import _types


def handler(context_dicts: _types.Context, context_objs: _types.Objects) -> list[str]: ...
