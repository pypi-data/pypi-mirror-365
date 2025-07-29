# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
User interaction facilities for usage inside :py:class:`krrez.api.Bit` apply methods.
"""
import abc
import asyncio
import enum
import inspect
import threading
import time
import typing as t

import hallyd


class Style(enum.Enum):
    NORMAL = enum.auto()
    CAUTION = enum.auto()
    CRITICAL = enum.auto()


_TInputResult = t.TypeVar("_TInputResult")
_TSinglePickResult = t.TypeVar("_TSinglePickResult")
_TMultiPickResult = t.TypeVar("_TMultiPickResult")


_TInputAnswer = t.Optional[str]
_TChooseAnswer = t.Optional[int]
_TMultiChooseAnswer = t.Optional[list[int]]


class Processor(t.Generic[_TInputResult, _TSinglePickResult, _TMultiPickResult], abc.ABC):
    """
    Abstract data type for a type that has a method for each kind of user interaction, with any return types.
    """

    @abc.abstractmethod
    def input(self, question: str, *, suggestion: str = "", multi_line: bool = False,
              is_valid_regexp: t.Optional[str] = None, invisible: bool = False,
              additional_text: str = "", style: Style = Style.NORMAL) -> _TInputResult:
        pass

    @abc.abstractmethod
    def choose(self, question: str, *, choices: t.Union[dict[str, t.Optional[object]], list[t.Optional[object]]],
               additional_text: str = "", style: Style = Style.NORMAL) -> _TSinglePickResult:
        pass

    @abc.abstractmethod
    def pick_single(self, question: str, choices: t.Union[dict[str, t.Optional[object]], list[t.Optional[object]]], *,
                    additional_text: str = "", style: Style = Style.NORMAL) -> _TSinglePickResult:
        pass

    @abc.abstractmethod
    def pick_multi(self, question: str, choices: t.Union[dict[str, t.Optional[object]], list[t.Optional[object]]], *,
                   additional_text: str = "", style: Style = Style.NORMAL) -> _TMultiPickResult:
        pass


class Endpoint(Processor[_TInputAnswer, _TChooseAnswer, _TMultiChooseAnswer], abc.ABC):
    """
    Abstract data type for a type that has a method for each kind of user interaction, with their usual return types.

    Subclasses of this type are typically used by client code that wants to actually show a dialog to the user and to
    get back the user's answer.
    """


class Provider(Processor[asyncio.Future[_TInputAnswer], asyncio.Future[_TChooseAnswer],
                         asyncio.Future[_TMultiChooseAnswer]], abc.ABC):
    """
    Abstract data type for a type that has a method for each kind of user interaction, with an :code:`asyncio.Future` of
    their usual return types as return types.

    Subclasses of this type typically implement the frontend side of dialogs, i.e. the actual user interface.

    Its method returns Future objects that hold a result once the user has answered the dialog, or it was cancelled.
    """


class _DialogRequest:

    def __init__(self, method_name, args, kwargs):
        self.__method_name = method_name
        self.__args = args
        self.__kwargs = kwargs

    @property
    def method_name(self):
        return self.__method_name

    @property
    def args(self):
        return self.__args

    @property
    def kwargs(self):
        return self.__kwargs


class Hub(hallyd.ipc_hub.Hub[_DialogRequest, t.Optional[t.Any]]):
    """
    Abstract base class for an IPC hub of dialog requests.
    """


class HubEndpoint(Endpoint, hallyd.lang.AllAbstractMethodsProvidedByTrick[Endpoint]):
    """
    Dialog endpoint implementation that passes interaction requests through a :py:class:`Hub`.
    """

    def __init__(self, dialog_hub: "Hub"):
        self.__dialog_hub = dialog_hub

    def __getattribute__(self, item):
        if (not item.startswith("_")) and (item in dir(Processor)):
            def method(*args, **kwargs):
                args = list(args)
                original_method_signature = inspect.getfullargspec(getattr(Processor, item))
                args += (original_method_signature.defaults or ())[len(args):]
                for kwarg_key, kwarg_default_value in (original_method_signature.kwonlydefaults or {}).items():
                    if kwarg_key not in kwargs:
                        kwargs[kwarg_key] = kwarg_default_value
                req = _DialogRequest(item, args, kwargs)
                req_id = self.__dialog_hub.put_request(req)
                return self.__dialog_hub.get_answer(req_id)

            return method

        return super().__getattribute__(item)


class _InteractionRequestFetcher(hallyd.ipc_hub.HubWorker[_DialogRequest, t.Optional[t.Any]]):

    def __init__(self, *args, provider: "Provider", **kwargs):
        super().__init__(*args, **kwargs)
        self.__open_requests = set()
        self.__provider = provider
        self.__fed = {}

    def request_arrived(self, request):
        self.__fed[request.request_id] = futs = []
        ans: asyncio.Future = getattr(self.__provider, request.payload.method_name)(*request.payload.args,
                                                                                    **request.payload.kwargs)
        futs.append(ans)
        def trd():
            while not ans.done():
                time.sleep(0.5)
            self.answer_request(request.request_id, ans.result())
        threading.Thread(target=trd, daemon=True).start()

    def request_disappeared(self, request):
        for fud in self.__fed[request.request_id]:
            fud.cancel()
