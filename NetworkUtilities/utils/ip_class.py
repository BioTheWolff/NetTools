from typing import Any, Union
from .errors import ByteNumberOffLimitsException, BytesLengthException


class LimitedList:

    __limit = None
    __list = None

    # PROPERTIES
    @property
    def limit(self):
        return self.__limit

    @property
    def length(self) -> int:
        return len(self.__list)

    @property
    def content(self) -> list:
        return self.__list

    # DUNDERS
    def __init__(self, size: int) -> None:
        super().__init__()
        self.__limit = size
        self.__list = []

    def __getitem__(self, item) -> Any:
        return self.__list[item]

    def __setitem__(self, key, value) -> None:
        self.__list[key] = value

    def __len__(self) -> int:
        return len(self.__list)

    def __copy__(self):
        return LimitedList(self.limit).append_all(self.__list)

    def __index__(self, obj: Any):
        return self.__list.index(obj)

    # NORMAL
    def append(self, obj: Any):
        if len(self.__list) == self.__limit:
            raise OverflowError("LimitedList limit reached")
        self.__list.append(obj)

        return self

    def append_all(self, list_: list):
        if len(list_) > self.limit:
            raise OverflowError("LimitedList limit reached")

        self.__list = list_

        return self


class FourBytesLiteral:

    __bytes: LimitedList = None

    # Dunders
    def __getitem__(self, item) -> Any:
        return self.__bytes[item] if self.__bytes else None

    def __setitem__(self, key, value) -> None:
        self.__bytes[key] = value

    def __len__(self) -> int:
        return len(self.__bytes)

    def __str__(self):
        return ".".join([str(i) for i in self.__bytes]) if self.bytes else "No literal"

    def __copy__(self):
        return FourBytesLiteral().set_eval(self.bytes) if self.__bytes else FourBytesLiteral()

    # Properties & getters
    @property
    def bytes(self) -> LimitedList:
        return self.__bytes

    @property
    def bytes_list(self) -> list:
        return self.__bytes.content if self.__bytes else None

    def index(self, i: Any) -> int:
        return self.__bytes.__index__(i) if self.__bytes else None

    def append(self, obj: Any) -> None:
        if self.__bytes is None:
            self.__bytes = LimitedList(4)
        self.__bytes.append(obj)

    # Setters (possibility of chaining)
    def set_eval(self, value: Union[str, LimitedList, list]):
        if isinstance(value, str):
            self.set_from_string_literal(value)
        elif isinstance(value, LimitedList):
            self.set_from_limited_list(value)
        elif isinstance(value, list):
            self.set_from_builtin_list(value)
        else:
            raise Exception("Formats can only be string literals, builtin lists or LimitedList instances")

        return self

    def set_from_string_literal(self, value: str):
        check_fbl(value)
        self.__bytes = LimitedList(4).append_all([int(i) for i in value.split('.')])

        return self

    def set_from_limited_list(self, value: LimitedList):
        if value.limit != 4:
            raise Exception("IPv4 LimitedList must be capped at 4")

        to_set = value.__copy__()
        # Allow partial filling
        if to_set.length < 4:
            for i in range(4 - to_set.length):
                to_set.append(0)

        self.__bytes = to_set

        return self

    def set_from_builtin_list(self, value: list):
        if len(value) > 4:
            raise Exception("IPv4 bytes must be capped at 4")

        # Allow partial filling
        if len(value) < 4:
            for i in range(4 - len(value)):
                value.append(0)

        self.__bytes = LimitedList(4).append_all(value)

        return self


def check_fbl(literal: str):
    # FBL stands for FourBytesLiteral
    split = [int(i) for i in literal.split('.')]

    if len(split) != 4:
        raise BytesLengthException("literal", len(split))

    for i in split:
        if not (0 <= i <= 255):
            raise ByteNumberOffLimitsException("literal", i, split.index(i))
