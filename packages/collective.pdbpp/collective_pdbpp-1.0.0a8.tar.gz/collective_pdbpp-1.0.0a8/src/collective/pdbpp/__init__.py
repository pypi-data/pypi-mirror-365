"""Init and utils."""

from AccessControl import Unauthorized
from BTrees.IOBTree import IOBTree
from pdb import Pdb  # type: ignore
from plone import api
from plone.browserlayer.utils import registered_layers
from Products.Five import BrowserView
from rich import pretty
from ZPublisher.HTTPRequest import HTTPRequest
from OFS.SimpleItem import PathReprProvider

import logging
import rich
import rich.pretty

try:
    from pdbpp import DefaultConfig

    DefaultConfig.sticky_by_default = True
except ImportError:
    # This works on recent versions of pdbpp
    pass


def initialize(context):
    pretty.install()


def rich_pprint(obj):
    """Print using rich."""
    rich.pretty.pprint(obj, expand_all=True)


def _do_pp(self, arg):
    """Override the pp (pretty-print) command to use rich."""
    try:
        # Evaluate the argument in the current debugging context
        obj = self._getval(arg)
        # Use rich's pprint to display the object
        if isinstance(obj, BrowserView):
            rich_pprint(obj.__class__.mro())
            rich.inspect(obj)
        elif isinstance(obj, HTTPRequest):
            rich.inspect(obj)
        elif isinstance(obj, IOBTree):
            rich_pprint(dict(obj))
        elif obj.__class__.__repr__ in (
            object.__repr__, PathReprProvider.__repr__,
        ):
            # Default repr is too boring
            rich_pprint(obj)
        else:
            rich_pprint(obj)

    except Exception:
        self._original_do_pp(arg)


def _do_ii(self: Pdb, arg):
    """Provide a rich inspect command."""
    # Evaluate the argument in the current debugging context
    obj = self._getval(arg)
    # Use rich's inspect to display the object
    rich.inspect(obj)


Pdb._original_do_pp = Pdb.do_pp
Pdb.do_pp = _do_pp

Pdb.do_ii = _do_ii


class RegisteredLAyers:

    def __repr__(self):
        return ""


class PdbView(BrowserView):

    @property
    def layers(self):
        rich.pretty.pprint(
            [layer.__identifier__ for layer in registered_layers()], expand_all=True
        )

    def __call__(self):
        if not api.env.debug_mode():
            raise Unauthorized

        locals().update(
            {
                "api": api,
                "context": self.context,
                "request": self.request,
                "rich": rich,
            }
        )

        rich.print(locals())
        breakpoint()
        logging.info("Exiting the interactive session")
        return self.request.response.redirect(self.context.absolute_url())
