from typing import Any


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

    # DUNDERS
    def __init__(self, size: int) -> None:
        super().__init__()
        self.__limit = size
        self.__list = []

    def __getitem__(self, item) -> Any:
        return self.__list[item]

    def __setitem__(self, key, value) -> None:
        self.__list[key] = value

    def __copy__(self) -> Any:
        return LimitedList(self.limit).append_all(self.__list)

    # NORMAL
    def append(self, obj: Any) -> None:
        if len(self.__list) == self.__limit:
            raise OverflowError("LimitedList limit reached")
        self.__list.append(obj)

    def append_all(self, list_: list):
        if len(list_) > self.limit:
            raise OverflowError("LimitedList limit reached")

        self.__list = list_


class FourBytesLiteral:

    __bytes: LimitedList = None

    def __init__(self) -> None:
        self.__bytes = LimitedList(4)

    def __getitem__(self, item) -> Any:
        return self.__bytes[item]

    def __setitem__(self, key, value):
        self.__bytes[key] = value

    @property
    def bytes(self) -> LimitedList:
        return self.__bytes

    @bytes.setter
    def bytes(self, value: LimitedList):
        if value.limit != 4:
            raise Exception("IPv4 LimitedList must be capped at 4")

        to_set = value.__copy__()
        # Allow partial filling
        if to_set.length < 4:
            for i in range(4 - to_set.length):
                to_set[4-i] = 0

        self.__bytes = to_set
