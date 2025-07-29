from collections.abc import Callable, Hashable, Iterable, Sequence
from idlelib.tree import (
    ScrolledCanvas as ScrolledCanvas,
    TreeItem as TreeItem,
    TreeNode as TreeNode,
)
from reprlib import Repr
from typing import TypeAlias

myrepr: Repr

_Object: TypeAlias = object

class ObjectTreeItem(TreeItem):
    labeltext: str | None
    object: (
        int
        | float
        | str
        | tuple[_Object, ...]
        | list[_Object]
        | dict[Hashable, _Object]
        | type
    )
    setfunction: Callable[[_Object], None]
    def __init__(
        self,
        labeltext: str | None,
        object: int
        | float
        | str
        | tuple[_Object, ...]
        | list[_Object]
        | dict[Hashable, _Object]
        | type,
        setfunction: Callable[[_Object], None] | None = ...,
    ) -> None: ...

class ClassTreeItem(ObjectTreeItem):
    object: type  # type: ignore[mutable-override]
    def __init__(
        self,
        labeltext: str | None,
        object: type,
        setfunction: Callable[[_Object], None] | None = ...,
    ) -> None: ...
    def IsExpandable(self) -> bool: ...
    def GetSubList(self) -> list[TreeItem]: ...

class AtomicObjectTreeItem(ObjectTreeItem):
    object: str | int | float  # type: ignore[mutable-override]
    def __init__(
        self,
        labeltext: str | None,
        object: str | int | float,
        setfunction: Callable[[_Object], None] | None = ...,
    ) -> None: ...
    def IsExpandable(self) -> bool: ...

class SequenceTreeItem(ObjectTreeItem):
    object: Sequence[_Object]  # type: ignore[assignment]
    setfunction: Callable[[_Object], None]
    def __init__(
        self,
        labeltext: str | None,
        object: Sequence[_Object],
        setfunction: Callable[[_Object], None] | None = ...,
    ) -> None: ...
    def IsExpandable(self) -> bool: ...
    def keys(self) -> Iterable[int]: ...
    def GetSubList(self) -> list[TreeItem]: ...

class DictTreeItem(SequenceTreeItem):
    object: dict[Hashable, _Object]  # type: ignore[assignment]
    setfunction: Callable[[_Object], None]
    def __init__(
        self,
        labeltext: str | None,
        object: dict[Hashable, _Object],
        setfunction: Callable[[_Object], None] | None = ...,
    ) -> None: ...
    def keys(self) -> list[Hashable]: ...  # type: ignore[override]

dispatch: dict[type, ObjectTreeItem]

def make_objecttreeitem(
    labeltext: str,
    object: _Object,
    setfunction: Callable[[str], None] | None = ...,
) -> ObjectTreeItem: ...
