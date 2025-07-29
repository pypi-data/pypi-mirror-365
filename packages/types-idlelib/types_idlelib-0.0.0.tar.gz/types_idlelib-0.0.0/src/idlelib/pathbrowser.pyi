from collections.abc import Iterable
from idlelib.browser import (
    ModuleBrowser as ModuleBrowser,
    ModuleBrowserTreeItem as ModuleBrowserTreeItem,
)
from idlelib.tree import TreeItem as TreeItem
from tkinter import Tk

class PathBrowser(ModuleBrowser):
    master: Tk
    def __init__(
        self,
        master: Tk,
        *,
        _htest: bool = ...,
        _utest: bool = ...,
    ) -> None: ...
    def settitle(self) -> None: ...
    def rootnode(self) -> PathBrowserTreeItem: ...  # type: ignore[override]

class PathBrowserTreeItem(TreeItem):
    def GetText(self) -> str: ...
    def GetSubList(self) -> list[DirBrowserTreeItem]: ...  # type: ignore[override]

class DirBrowserTreeItem(TreeItem):
    dir: str
    packages: list[str]
    def __init__(self, dir: str, packages: list[str] = ...) -> None: ...
    def GetText(self) -> str: ...
    def GetSubList(self) -> list[ModuleBrowserTreeItem]: ...  # type: ignore[override]
    def ispackagedir(self, file: str) -> bool: ...
    def listmodules(
        self,
        allnames: Iterable[str],
    ) -> list[tuple[str, str]]: ...
