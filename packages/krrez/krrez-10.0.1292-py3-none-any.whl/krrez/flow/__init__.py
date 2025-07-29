# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
The entire mechanism involved in applying bits (like :code:"krrez bits apply ..." commands) are implemented in this
module and its submodules.

This module contains some foundation parts, but not the engine itself.
"""
import abc
import datetime
import string
import typing as t

import hallyd

if t.TYPE_CHECKING:
    import krrez.api
    import krrez.flow.config


#: The Python module namespace that contains :py:class:`krrez.api.Bit` implementations.
BITS_NAMESPACE = "krrez.bits"

PROFILES_NAMESPACE = "krrez.profiles"

#: The base directory for Krrez etc data (system configuration files).
KRREZ_ETC_DIR = hallyd.fs.Path("/etc/krrez")
#: The base directory for Krrez usr data (binary data, system resources).
KRREZ_USR_DIR = hallyd.fs.Path("/usr/local/krrez")
#: The base directory for Krrez var data (variable data files).
KRREZ_VAR_DIR = hallyd.fs.Path("/var/lib/krrez")

#: The flag file that indicates whether a system is a Krrez machine (i.e. was seeded and installed by Krrez).
_IS_KRREZ_MACHINE_FLAG_PATH = KRREZ_ETC_DIR("is_krrez_machine")

#: The root directory of Krrez sources, i.e. the 'krrez' Python package. Its name is :samp:`krrez`.
KRREZ_SRC_ROOT_DIR = hallyd.fs.Path(__file__).resolve().parent.parent


@hallyd.lang.with_friendly_repr_implementation()
class Context:
    """
    A context is the place where configuration data, logs, and some other things are stored that will be used by Krrez
    (associated with a context is a path, where all that data is stored).

    For usual cases, like usual :code:`krrez bits apply` runs, there is no choice for the end user, but it will always
    use its default location. However, internally, there will be contexts with other paths involved for some operations
    (like seeding and testing).
    """

    #: The default context path.
    DEFAULT_ROOT_PATH = KRREZ_VAR_DIR("ctx")

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.path == other.path

    def __hash__(self):
        return hash(self.path)

    def __init__(self, path: t.Optional[hallyd.fs.TInputPath] = None):
        import krrez.flow.config as fconfig
        self.__path = hallyd.fs.Path(path or Context.DEFAULT_ROOT_PATH)
        self.path.mkdir(exist_ok=True, parents=True, mode=0o750)

        try:
            Context.__context_path_to_magic_file_path(self.path).mkdir(exist_ok=True)  # TODO odd
        except IOError:
            pass

        try:
            KRREZ_ETC_DIR.make_dir(exist_ok=True, readable_by_all=True)  # TODO odd
        except IOError:
            pass
        try:
            KRREZ_VAR_DIR.make_dir(exist_ok=True, readable_by_all=True)  # TODO odd
        except IOError:
            pass

        self.__config = fconfig.controller(context=self)
        self.__installed_bits_file = self.__path("installed_bits")

    def _mark_bit_installed(self, bit: type["krrez.api.Bit"]) -> None:
        import krrez.flow.bit_loader

        with self.config.lock("krrez.installed_bits"):
            self.__installed_bits_file.write_text(hallyd.bindle.dumps(
                [*self.installed_bits(), krrez.flow.bit_loader.bit_name(bit)]))

    def is_bit_installed(self, bit: type["krrez.api.Bit"]) -> bool:
        import krrez.flow.bit_loader
        return krrez.flow.bit_loader.bit_name(bit) in self.installed_bits()

    def installed_bits(self) -> list[str]:
        with self.config.lock("krrez.installed_bits"):
            if not self.__installed_bits_file.exists():
                return []
            return hallyd.bindle.loads(self.__installed_bits_file.read_text())

    @property
    def path(self) -> hallyd.fs.Path:
        return self.__path

    @property
    def config(self) -> "krrez.flow.config.Controller":
        return self.__config

    @property
    def parent_context(self) -> t.Optional["Context"]:
        result = self.path.parent.parent
        if result.name and Context.__context_path_to_magic_file_path(result).exists():
            return Context(result)

    def _blank_contexts_path(self) -> hallyd.fs.Path:
        result = self.path("sub")
        result.make_dir(exist_ok=True, readable_by_all=True, owner=None, group=None)
        return result

    def _locals_path(self) -> hallyd.fs.Path:
        result = self.path("locals")
        result.make_dir(exist_ok=True, readable_by_all=True, owner=None, group=None)
        return result

    @staticmethod
    def __context_path_to_magic_file_path(context_path: hallyd.fs.Path) -> hallyd.fs.Path:
        return context_path(".is_krrez_context")

    def get_sessions(self) -> list["Session"]:
        return [Session.by_name(session_path.name, context=self) for session_path
                in sorted(Session._sessions_path(self).iterdir())]

    def get_blank_contexts(self) -> list["Context"]:
        return [Context(context_path) for context_path in self._blank_contexts_path().iterdir()]

    def lock(self, lock_name: str, *,
             ns: t.Optional[hallyd.typing.SupportsQualifiedName] = None) -> hallyd.lang.Lock:
        if ns is not None:
            lock_name = f"{ns.__module__}.{ns.__qualname__}.{lock_name}"

        for forbidden_char in "/\\":
            if forbidden_char in lock_name:
                raise ValueError(f"invalid lock name '{lock_name}': '{forbidden_char}' is not allowed")

        locks_dir = self._locals_path()("locks")
        if not locks_dir.exists():
            locks_dir.make_dir(mode=0o777)  # TODO nobody (but root) should have access to locks?! but how?
        return hallyd.lang.lock(locks_dir(lock_name), is_reentrant=True)

    def _interaction_request_fetcher_for_session(self, session, provider):
        import krrez.flow.dialog as _dialog
        import krrez.flow.writer as _writer
        return _dialog._InteractionRequestFetcher.plug_into_hub(_writer._ipc_dialog_hub_path(session.path),
                                                                provider=provider)


def context_local_unique_id(context: Context) -> int:
    """
    Return a number that is unique for the given context on this machine.

    :param context: The context.
    """
    default_context = Context()

    with default_context.config.lock("krrez.context_id_map"):
        context_id_map = default_context.config.get("krrez.context_id_map", {})
        context_key = str(context.path.resolve())

        unique_id = context_id_map.get(context_key)
        if unique_id is None:
            unique_id = default_context.config.get("krrez.next_unique_id", 0)
            default_context.config.set("krrez.next_unique_id", unique_id+1)
            default_context.config.set("krrez.context_id_map", {**context_id_map, context_key: unique_id})

    return unique_id


def create_blank_context(in_context: t.Optional[Context] = None, *, inherit_config_values: bool = False,
                         blank_context_path: t.Optional[hallyd.fs.Path] = None) -> Context:
    in_context = in_context or Context()

    with in_context.config.lock("krrez.session_id_counter"):
        session_id = in_context.config.get("krrez.session_id_counter", 0) + 1
        in_context.config.set("krrez.session_id_counter", session_id)

    if not blank_context_path:
        while True:
            blank_context_path = in_context._blank_contexts_path()(str(session_id))
            try:
                blank_context_path.make_dir(exist_ok=False, readable_by_all=True)
                break
            except FileExistsError:
                pass
    result = Context(blank_context_path)
    if inherit_config_values:
        for config_key in in_context.config.available_keys(with_confidential=False):
            result.config.set(config_key, in_context.config.get(config_key))
    return result


class Session(abc.ABC):
    """
    Each bit apply run, either trigger by usual ":code:`krrez bits apply ...`" or internally by some other procedure,
    is associated to one separate session.

    A session itself is associated to a context, where it retrieves configuration values from, stores logging, and more.
    """

    def __eq__(self, other):
        return isinstance(other, type(self)) and (self.context, self.name) == (other.context, other.name)

    def __hash__(self):
        return hash((self.context, self.name))

    @staticmethod
    def create(*, context: Context) -> "Session":
        with context.lock("next_session_number", ns=Session):
            session_number = context.config.get("krrez.next_session_number", 0) + 1
            context.config.set("krrez.next_session_number", session_number)
        now_str = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M")
        return _Session(context=context, name=f"{now_str}N{session_number}")

    @staticmethod
    def by_name(name: str, *, context: Context) -> "Session":
        return _Session(context=context, name=name)

    @property
    @abc.abstractmethod
    def context(self) -> Context:
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def path(self) -> hallyd.fs.Path:
        pass

    @property
    def exists(self) -> bool:
        return self.path.exists()

    @staticmethod
    def name_is_valid(name: str) -> bool:
        for char in name:
            if not ((char in string.ascii_letters) or (char in string.digits) or (char in "-")):
                return False
        return True

    @staticmethod
    def _sessions_path(context: Context) -> hallyd.fs.Path:
        return context.path("runs").make_dir(exist_ok=True, readable_by_all=True, owner=None, group=None)

    @staticmethod
    def _all_sessions_path(context: Context) -> hallyd.fs.Path:
        return context.path("runs~").make_dir(exist_ok=True, readable_by_all=True, owner=None, group=None)


@hallyd.lang.with_friendly_repr_implementation()
class _Session(Session):
    """
    Session implementation.
    """

    def __init__(self, context: Context, name: str):
        self.__context = context
        if not self.name_is_valid(name):
            raise ValueError(f"invalid session name: {name}")
        self.__name = name

    @property
    def context(self):
        return self.__context

    @property
    def name(self):
        return self.__name

    @property
    def path(self):
        return Session._sessions_path(self.context)(self.name)

    @property
    def path2(self):
        return Session._all_sessions_path(self.context)(self.name)


def is_krrez_machine() -> bool:
    """
    Whether this machine is enabled to be a Krrez machine.

    This is a safety feature which helps preventing unintended execution of bits.

    See also :py:func:`mark_as_krrez_machine`.
    """
    return _IS_KRREZ_MACHINE_FLAG_PATH.exists()


def mark_as_krrez_machine(system_root_path: hallyd.fs.Path) -> None:
    """
    Enables a system to be a Krrez machine, allowing things like applying bits.

    See also :py:func:`is_krrez_machine`.

    :param system_root_path: The root path of the system to enable (assuming that it is mounted for preparation
                             somewhere inside the host filesystem).
    """
    flag_path = system_root_path(_IS_KRREZ_MACHINE_FLAG_PATH)
    flag_path.parent.make_dir(exist_ok=True, until=system_root_path, readable_by_all=True)
    flag_path.make_file(readable_by_all=True)
