import logging

from ida_dbg import DBG_Hooks
from ida_hexrays import Hexrays_Hooks
from ida_idp import IDB_Hooks, IDP_Hooks
from ida_kernwin import UI_Hooks, View_Hooks
from typing_extensions import TypeAlias, Union

from .base import DatabaseEntity

logger = logging.getLogger(__name__)


class _BaseHooks(DatabaseEntity):
    def __init__(self) -> None:
        super().__init__(None)
        self._is_hooked: bool = False

    @property
    def is_hooked(self) -> bool:
        return self._is_hooked

    def log(self, msg: str = '') -> None:
        """
        Utility method to optionally log called hooks and their parameters.
        """
        import inspect

        if msg:
            logger.debug('>>> %s: %s' % self.__class__.__name__ % msg)
        else:
            stack = inspect.stack()
            frame, _, _, _, _, _ = stack[1]
            args, _, _, values = inspect.getargvalues(frame)
            method_name = inspect.getframeinfo(frame)[2]
            argstrs = []
            for arg in args[1:]:
                argstrs.append('%s=%s' % (arg, str(values[arg])))
            logger.debug(
                '>>> %s.%s: %s' % (self.__class__.__name__, method_name, ', '.join(argstrs))
            )


class ProcessorHooks(_BaseHooks, IDP_Hooks):
    """
    Convenience class for IDP (processor) events handling.
    """

    def __init__(self) -> None:
        _BaseHooks.__init__(self)
        IDP_Hooks.__init__(self)

    def hook(self) -> None:
        """
        Hook (activate) the event handlers.
        """
        if not self.is_hooked:
            if IDP_Hooks.hook(self):
                self._is_hooked = True

    def unhook(self) -> None:
        """
        Un-hook (de-activate) the event handlers.
        """
        if self.is_hooked:
            if IDP_Hooks.unhook(self):
                self._is_hooked = False


class DatabaseHooks(_BaseHooks, IDB_Hooks):
    """
    Convenience class for IDB (database) events handling.
    """

    def __init__(self) -> None:
        _BaseHooks.__init__(self)
        IDB_Hooks.__init__(self)

    def hook(self) -> None:
        """
        Hook (activate) the event handlers.
        """
        if not self.is_hooked:
            if IDB_Hooks.hook(self):
                self._is_hooked = True

    def unhook(self) -> None:
        """
        Un-hook (de-activate) the event handlers.
        """
        if self.is_hooked:
            if IDB_Hooks.unhook(self):
                self._is_hooked = False


class DebuggerHooks(_BaseHooks, DBG_Hooks):
    """
    Convenience class for IDB (database) events handling.
    """

    def __init__(self) -> None:
        _BaseHooks.__init__(self)
        DBG_Hooks.__init__(self)

    def hook(self) -> None:
        """
        Hook (activate) the event handlers.
        """
        if not self.is_hooked:
            if DBG_Hooks.hook(self):
                self._is_hooked = True

    def unhook(self) -> None:
        """
        Un-hook (de-activate) the event handlers.
        """
        if self.is_hooked:
            if DBG_Hooks.unhook(self):
                self._is_hooked = False


class UIHooks(_BaseHooks, UI_Hooks):
    """
    Convenience class for UI events handling.
    """

    def __init__(self) -> None:
        _BaseHooks.__init__(self)
        UI_Hooks.__init__(self)

    def hook(self) -> None:
        """
        Hook (activate) the event handlers.
        """
        if not self.is_hooked:
            if UI_Hooks.hook(self):
                self._is_hooked = True

    def unhook(self) -> None:
        """
        Un-hook (de-activate) the event handlers.
        """
        if self.is_hooked:
            if UI_Hooks.unhook(self):
                self._is_hooked = False


class ViewHooks(_BaseHooks, View_Hooks):
    """
    Convenience class for IDA View events handling.
    """

    def __init__(self) -> None:
        _BaseHooks.__init__(self)
        View_Hooks.__init__(self)

    def hook(self) -> None:
        """
        Hook (activate) the event handlers.
        """
        if not self.is_hooked:
            if View_Hooks.hook(self):
                self._is_hooked = True

    def unhook(self) -> None:
        """
        Un-hook (de-activate) the event handlers.
        """
        if self.is_hooked:
            if View_Hooks.unhook(self):
                self._is_hooked = False


class DecompilerHooks(_BaseHooks, Hexrays_Hooks):
    """
    Convenience class for decompiler events handling.
    """

    def __init__(self) -> None:
        _BaseHooks.__init__(self)
        Hexrays_Hooks.__init__(self)

    def hook(self) -> None:
        """
        Hook (activate) the event handlers.
        """
        if not self.is_hooked:
            if Hexrays_Hooks.hook(self):
                self._is_hooked = True

    def unhook(self) -> None:
        """
        Un-hook (de-activate) the event handlers.
        """
        if self.is_hooked:
            # returns False, assume it succeeded
            Hexrays_Hooks.unhook(self)
            self._is_hooked = False


# Type alias to be used as a shorthand for a list of zero or more hook instances
HooksList: TypeAlias = list[
    Union[ProcessorHooks, DatabaseHooks, DebuggerHooks, DecompilerHooks, UIHooks, ViewHooks]
]
