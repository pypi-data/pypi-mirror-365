# SPDX-FileCopyrightText: © 2024 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import abc
import contextlib
import copy
import dataclasses
import inspect
import logging
import subprocess
import typing as t

import hallyd

import krrez.api
import krrez.flow.bit_loader
import krrez.flow.dialog
import krrez.flow.graph.resolver
import krrez.flow.logging


class MayDeclareSecondaryBitUsages:
    """
    Subclasses of this class may declare the usage of other Bits by an annotated class attribute (like for dataclasses),
    and use them in a convenient, straight-forward way.

    This mechanism is used in :py:class:`krrez.api.Bit`, but also in a few other places.
    """

    def __init__(self, *, used_by=lambda: None):
        self.__foreign_bits_cache = {}
        self.__used_by = used_by

    @staticmethod
    def _resolve_optional(annotation_value: t.Any) -> tuple[t.Any, bool]:
        try:
            # noinspection PyUnresolvedReferences,PyProtectedMember
            if type(annotation_value) == t._UnionGenericAlias:
                argz = [x for x in t.get_args(annotation_value) if x is not type(None)]
                if len(argz) == 1:
                    annotation_value = argz[0]
                    if isinstance(annotation_value, t.ForwardRef):
                        annotation_value = annotation_value.__forward_arg__
                    return annotation_value, True
        except Exception:
            pass
        return annotation_value, False

    @classmethod
    def _all_bit_usage_declarations(cls, *, all_bits: t.Optional[t.Iterable[type["krrez.api.Bit"]]] = None
                                    ) -> dict[str, tuple[t.Optional[type["krrez.api.Bit"]], str, t.Any]]:
        if all_bits is None:
            all_bits = krrez.flow.bit_loader.all_bits(accept_cached=True)
        result = {}
        for my_type in reversed(cls.__mro__):
            for var_name, unresolved_foreign_bit_type in getattr(my_type, "__annotations__", {}).items():
                bit_type = unresolved_foreign_bit_type
                bit_type, is_optional = MayDeclareSecondaryBitUsages._resolve_optional(bit_type)
                foreign_bit_type = MayDeclareSecondaryBitUsages._try_resolve_bit_type(bit_type, all_bits=all_bits)

                foreign_bit_type_gname = None
                if isinstance(bit_type, str) and bit_type.startswith(f"{krrez.flow.BITS_NAMESPACE}."
                                                                     ) and ".SPECIAL." in bit_type:
                    foreign_bit_type_gname = bit_type[len(krrez.flow.BITS_NAMESPACE) + 1:]
                elif foreign_bit_type:
                    foreign_bit_type_gname = (f"{foreign_bit_type.__module__[len(krrez.flow.BITS_NAMESPACE) + 1:]}"
                                              f".{foreign_bit_type.__name__}")

                if foreign_bit_type_gname:
                    result[var_name] = foreign_bit_type, foreign_bit_type_gname, unresolved_foreign_bit_type
        return result

    @staticmethod
    def _try_resolve_bit_type(bit_type: t.Union[str, type["krrez.api.Bit"]], *,
                              all_bits: t.Iterable[type["krrez.api.Bit"]] = None) -> t.Optional[type["krrez.api.Bit"]]:
        """
        Translate any way of attribute-style dependency to a Bit subclass.

        :param bit_type: The Bit specification.
        """
        if isinstance(bit_type, str) and bit_type.startswith(f"{krrez.flow.BITS_NAMESPACE}."):
            bit_type = krrez.flow.bit_loader.bit_by_name(bit_type[len(krrez.flow.BITS_NAMESPACE) + 1:],
                                                         all_bits=all_bits)

        if isinstance(bit_type, type) and issubclass(bit_type, krrez.api.Bit) and bit_type.__module__.startswith(
                f"{krrez.flow.BITS_NAMESPACE}."):
            # noinspection PyTypeChecker
            return bit_type

    def _bit_for_type(self, bit_type):
        return krrez.flow.bit_loader.bit_for_secondary_usage(bit_type, used_by=self.__used_by())

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            foreign_bit_type, *_ = self._all_bit_usage_declarations().get(item, (None,))
            if foreign_bit_type:
                if foreign_bit_type not in self.__foreign_bits_cache:
                    self.__foreign_bits_cache[foreign_bit_type] = self._bit_for_type(foreign_bit_type)
                return self.__foreign_bits_cache[foreign_bit_type]

            raise


class ProfileMeta(type):
    """
    Metaclass for :py:class:`krrez.api.Profile` and subclasses. It provides some metadata and useful information as
    class properties.
    """

    @property
    def name(self) -> str:
        import krrez.seeding.profile_loader
        return krrez.seeding.profile_loader.profile_name(self)

    @property
    def open_parameters(self) -> t.Optional[list["krrez.api.Profile.Parameter"]]:
        result = []

        for param in inspect.signature(self).parameters.values():
            if param.kind in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD]:
                return None

            param_type = getattr(self.__init__, "__annotations__", {}).get(param.name, None)
            result.append(krrez.api.Profile.Parameter(param.name, param_type))

        return result

    @property
    def available_target_devices(self) -> list[tuple[hallyd.fs.Path, str]]:
        available_targets = sorted([(
            disk.path,
            f"{disk.path.name} - {hallyd.fs.byte_size_to_human_readable(disk.size_bytes)}"
            f" {self.__get_block_dev_info(disk.path.name)}".strip())
            for disk in hallyd.disk.host_disks() if disk.is_disk and disk.is_removable], key=lambda target: target[0])

        try:
            available_targets += [("/dev/loop77", "LOOPY")]; subprocess.call(
                ["losetup", "-P", "/dev/loop77", "/mnt/raid/looopy"], stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)  # TODO WEG!!!
        except:
            pass

        return available_targets

    @property
    def is_browsable(self) -> bool:
        return None not in [self.open_parameters, self.name]

    @property
    def is_hidden(self) -> bool:
        return self.__dict__.get("is_hidden", False)

    @staticmethod
    def __get_block_dev_info(name: str) -> str:
        sys_block_path = hallyd.fs.Path("/sys/class/block", name)
        result = []
        try:
            result.append(sys_block_path("device/vendor").read_text().strip())
        except IOError:
            pass
        try:
            result.append(sys_block_path("device/model").read_text().strip())
        except IOError:
            pass
        return " ".join(result)


class Dependency:
    """
    A dependency is assigned to a :py:class:`Bit` and can pull in other Bits and control the order of Bits when it gets
    applied.

    In order to assign a dependency to a Bit, instantiate a subclass and decorate your apply method with it.
    This is called the "decoration-style" syntax in the documentation.
    """

    def additional_needed_bits(self, cooling_down: bool, plan: "krrez.flow.graph.resolver.Plan") -> t.Iterable[str]:
        """
        A list of Bits that are pulled in by this dependency.

        :param cooling_down: If the process is in cooling down mode.
        :param plan: The resolution plan.
        """
        return ()

    def relative_order(self, own_bit: type["krrez.api.Bit"], other_bit: type["krrez.api.Bit"]) -> int:
        """
        The relative order between two Bits, the 'own' one, and the other one.

        :param own_bit: The own Bit.
        :param other_bit: The other Bit.
        :return: -1 if the own one has to come earlier, 1 if it has to come later, and 0 if it does not matter.
        """
        return 0

    # noinspection PyUnusedLocal
    def manipulate_resolution_plan(self, owning_bit: type["krrez.api.Bit"],
                                   plan: "krrez.flow.graph.resolver.Plan") -> bool:
        """
        Apply custom manipulations to a resolution plan. Return :code:`True` if a change was made.

        This is only used for very particular internal tricks.

        :param owning_bit: The Bit that this dependency is associated to.
        :param plan: The resolution plan.
        """
        return False


class BaseForSimpleBehaviorDependency(Dependency):
    """
    Base class for a simple (afterwards or beforehand) dependency.
    """

    def __resolve_optional(self, bit):
        try:
            if isinstance(bit, str) and bit.startswith("optional:"):
                return bit[9:], True

            if type(bit) == t._UnionGenericAlias:
                argz = [x for x in t.get_args(bit) if x is not type(None)]
                if len(argz) == 1:
                    bit = argz[0]
                    if isinstance(bit, t.ForwardRef):
                        bit = bit.__forward_arg__
                    return bit, True
        except Exception:
            pass
        return bit, False

    def __repr__(self):
        return f"Dep(afterwards={self.__afterwards}, bits={self._bits}, optional_bits={self._optional_bits})"

    def __init__(self, bits: t.Iterable[str], *, afterwards: t.Optional[bool]):
        """
        :param bits: The Bits to depend on.
        :param afterwards: Whether this is an afterwards-dependency.
        """
        self.__afterwards = afterwards
        self.__bits = tuple(bits)
        self.__dependency_bits_cache = None

    def __dependency_bits(self):
        if self.__dependency_bits_cache is None:
            non_optional_bits = []
            optional_bits = []
            for bit in self.__bits:
                bit, is_optional = self.__resolve_optional(bit)
                (optional_bits if is_optional else non_optional_bits).append(krrez.flow.bit_loader.bit_name(bit))
            self.__dependency_bits_cache = non_optional_bits, optional_bits
        return self.__dependency_bits_cache

    @property
    def _bits(self) -> list[str]:
        return self.__dependency_bits()[0]

    @property
    def _optional_bits(self) -> list[str]:
        return self.__dependency_bits()[1]

    def additional_needed_bits(self, cooling_down, plan):
        return list(self._bits)

    def relative_order(self, own_bit, other_bit):
        if self.__afterwards is None:
            return 0
        if krrez.flow.bit_loader.bit_name(other_bit) not in (*self._bits, *self._optional_bits):
            return 0
        return 1 if self.__afterwards else -1


class SimpleDependency(BaseForSimpleBehaviorDependency):
    """
    A simple dependency.
    """

    def __init__(self, bits: t.Iterable[str], *, afterwards: t.Optional[bool] = False):
        super().__init__(bits, afterwards=afterwards)
        self.__afterwards = afterwards

    @property
    def bit_names(self) -> list[str]:
        """
        The names of non-optional Bits to depend on.
        """
        return self._bits

    @property
    def optional_bit_names(self) -> list[str]:
        """
        The names of optional Bits to depend on.
        """
        return self._optional_bits

    @property
    def all_bit_names(self) -> list[str]:
        """
        The names of optional and non-optional Bits to depend on.
        """
        return [*self.bit_names, self.optional_bit_names]

    @property
    def afterwards(self) -> bool:
        return self.__afterwards


_TConfigValueType = t.TypeVar("_TConfigValueType")


class ConnectableToBit(abc.ABC):

    @abc.abstractmethod
    def _connected_to_bit(self, bit: "krrez.api.Bit", key: str) -> "t.Self":
        """
        Implement this method with logic to connect this object to the owning Bit.

        Automatically called by the infrastructure when a ConnectableToBit attribute from :py:class:`krrez.api.Bit` is
        accessed.

        :param bit: The Bit to connect to.
        :param key: The attribute key.
        """


class Lock(ConnectableToBit):
    """
    A multithreading/multiprocessing lock.

    Can be used whenever code could be executed in parallel from multiple places, in order to synchronize access.
    Works beyond process barrier and is reentrant. Define a lock in the body of your Bit class like this:

    .. code-block:: python

      _lock = krrez.api.Lock()

    You can use it inside your methods like this:

    .. code-block:: python

      with self._lock:
          ...

    Note: If you define multiple Bits in one module, and they define a lock with the same name, it will refer to the
    same lock.
    """

    def __init__(self):
        self.__context_lock = None

    def _connected_to_bit(self, bit, key):
        result = copy.copy(self)
        result.__context_lock = bit._internals.context.lock(
            f"{type(bit).__module__[len(krrez.flow.BITS_NAMESPACE)+1:]}.{type(bit).__qualname__}.{key}")
        return result

    def __enter__(self):
        return self.__context_lock.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__context_lock.__exit__(exc_type, exc_val, exc_tb)


class AdHocLogger(krrez.flow.logging.Logger):

    class _MessageMode(krrez.flow.logging.LoggerMode):

        def _log(self, message, severity, aux_name):
            import sys; print(message, file=sys.stderr); return  # TODO weg
            _logger = logging.getLogger(__name__)
            if severity == krrez.flow.logging.Severity.DEBUG:
                log = _logger.debug
            elif severity == krrez.flow.logging.Severity.INFO:
                log = _logger.info
            elif severity == krrez.flow.logging.Severity.WARNING:
                log = _logger.warning
            elif severity == krrez.flow.logging.Severity.FATAL:
                log = _logger.error
            else:
                raise ValueError(f"invalid severity: {severity}")
            log(message)

    class _BlockMode(_MessageMode):

        @contextlib.contextmanager
        def _log(self, message, severity, aux_name):
            super()._log(message, severity, aux_name)
            yield AdHocLogger()

    @property
    def block(self):
        return self._BlockMode()

    @property
    def message(self):
        return self._MessageMode()


class BareConfigValue(t.Generic[_TConfigValueType], ConnectableToBit):

    _NoConfigValueDefault = object()

    @dataclasses.dataclass(frozen=True)
    class _AskForDialog:
        method_name: str
        args: t.Iterable
        kwargs: dict

    def __init__(self, *, default: _TConfigValueType = _NoConfigValueDefault, is_confidential: bool = False,
                 type: type[_TConfigValueType] = object, short_name: t.Optional[str] = None,
                 module_name: t.Optional[str] = None, full_name: t.Optional[str] = None,
                 question: t.Optional[_AskForDialog] = None):
        self.__type = type
        self.__short_name = short_name
        self.__module_name = module_name
        self.__full_name = full_name
        self.__has_default = default is not self._NoConfigValueDefault
        self.__default_serialized = hallyd.bindle.dumps(default) if self.__has_default else None
        self.__is_confidential = is_confidential
        self.__question = question
        self.__setter = None
        self.__setter_lock = None
        self.__context = None
        self.__bit = None
        self.__key = None

    @property
    def type(self) -> type[_TConfigValueType]:
        return self.__type

    @property
    def short_name(self) -> t.Optional[str]:
        return self.__short_name

    @property
    def module_name(self) -> t.Optional[str]:
        return self.__module_name

    @property
    def full_name(self) -> t.Optional[str]:
        return self.__full_name

    @property
    def default(self) -> t.Union[_TConfigValueType, object]:
        if not self.__has_default:
            return self._NoConfigValueDefault
        return hallyd.bindle.loads(self.__default_serialized)

    @property
    def is_confidential(self) -> bool:
        return self.__is_confidential

    @property
    def question(self) -> t.Optional[_AskForDialog]:
        return self.__question

    def actual_full_name(self, bit: "krrez.api.Bit", item: str) -> str:
        return self.__full_name or (f"{self.__module_name or type(bit).__module__[len(krrez.flow.BITS_NAMESPACE) + 1:]}"
                                    f".{self.__short_name or item.strip('_')}")

    def __ctrl(self) -> "krrez.flow.config.Controller":
        return self.__context.config

    def _connected_to_bit(self, bit, key):
        result = copy.copy(self)
        result.__context = bit._internals.context
        result.__bit = bit
        result.__key = self.__full_name = result.actual_full_name(bit, key)
        return result

    class _Setter(t.Generic[_TConfigValueType]):

        def __init__(self, value: _TConfigValueType):
            self.value: _TConfigValueType = value

    @property
    def __value(self):
        return self.__ctrl().get(self.__key, self.default)

    @property
    def value(self) -> _TConfigValueType:
        v = self.__value
        if v is self._NoConfigValueDefault:
            question = self.question or self._AskForDialog("input", (f"Please specify '{self.__key}'.",), {})
            controller = krrez.flow.config.interactive_controller(
                original_controller=krrez.flow.config.config_client_for_existing_session(self.__bit._internals.session.path),
                dialog_endpoint=self.__bit._internals.dialog_endpoint)

            return getattr(controller.ask_for(self.__key, confidentially=self.is_confidential),
                           question.method_name)(*question.args, **question.kwargs)
        return v

    def __enter__(self):
        self.__setter_lock = self.__ctrl().lock(self.__key).__enter__()
        self.__setter = self._Setter[_TConfigValueType](self.__value)
        return self.__setter

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__ctrl().set(self.__key, self.__setter.value)
        lock = self.__setter_lock
        self.__setter_lock = None
        self.__setter = None
        lock.__exit__(exc_type, exc_val, exc_tb)


class _ConfigValueWithoutAskFor(BareConfigValue[_TConfigValueType], t.Generic[_TConfigValueType]):
    pass


class ConfigValueAskForPrepared(t.Generic[_TConfigValueType], BareConfigValue[_TConfigValueType]):

    class _AskFor(t.Generic[_TConfigValueType],
                  krrez.flow.dialog.Processor[_ConfigValueWithoutAskFor[_TConfigValueType], _ConfigValueWithoutAskFor[_TConfigValueType],
                  _ConfigValueWithoutAskFor[_TConfigValueType]],
                  hallyd.lang.AllAbstractMethodsProvidedByTrick[krrez.flow.dialog.Processor]):

        def __init__(self, config_value: "ConfigValueAskForPrepared"):
            self.__config_value = config_value

        def __getattribute__(self, item):
            if (not item.startswith("_")) and (item in dir(krrez.flow.dialog.Processor)):
                def method(*args, **kwargs):
                    return _ConfigValueWithoutAskFor(
                        type=self.__config_value.type,
                        short_name=self.__config_value.short_name,
                        module_name=self.__config_value.module_name,
                        full_name=self.__config_value.full_name,
                        default=self.__config_value.default,
                        is_confidential=self.__config_value.is_confidential,
                        question=BareConfigValue._AskForDialog(item, args, kwargs)
                    )

                return method

            return super().__getattribute__(item)

    def _ask_for(self) -> _AskFor[_TConfigValueType]:
        return ConfigValueAskForPrepared._AskFor(self)


class ConfigValue(ConfigValueAskForPrepared[_TConfigValueType], t.Generic[_TConfigValueType]):
    """
    A configuration value.

    Configuration values allow to make parts of your automation logic configurable. The actual value at runtime can
    either be defined in the seed profile, or if not, is entered by the user during the seed procedure. Note that all
    values must have a primitive data type (or be serializable by hallyd).

    The way to specify a configuration value is to add a line like this to the top of your Bit class body:

    .. code-block:: python

      _my_config = krrez.api.ConfigValue(default="hello", type=str)

    You can access the actual value inside your :py:meth:`Bit.__apply__` method in some ways. It is readable:

    .. code-block:: python

      my_config = self._my_config.value

    And also writable:

    .. code-block:: python

      with self._my_config as my_config:
          my_config.value = "ola"

    When you read it, at there was no value specified e.g. in the seed profile, the behavior depends on whether you have
    specified a :code:`default`. If yes, you will read this default value. If not, the user will be asked to enter it
    during installation.

    For more control about how the user is asked to enter a value at installation time, see :py:attr:`ask_for`, e.g.
    used like this:

    .. code-block:: python

      _name = krrez.api.ConfigValue(type=str).ask_for.input("Please enter the foo name.")

    In general, with usual configuration, the internal key for your configuration value will be
    ":code:`[A].[B]`" where :code:`[A]` is the short name of the Bit where it is defined, but without the last part
    (i.e. ":code:`foo`" for :code:`krrez.bits.foo.Bit`), and :code:`[B]` is the name of the attribute, but with
    underscores stripped away on the left hand side (i.e. :code:`my_config` for :code:`_my_config`).
    """

    def __init__(self, *, default: _TConfigValueType = BareConfigValue._NoConfigValueDefault,
                 is_confidential: bool = False, type: type[_TConfigValueType] = object):
        """
        :param default: The default value.
        :param is_confidential: Whether this value contains confidential information that must not be persisted.
        :param type: The value type. Mostly used for IDE guidance.
        """
        super().__init__(default=default, is_confidential=is_confidential, type=type)

    # noinspection PyProtectedMember
    ask_for = ConfigValueAskForPrepared()._ask_for()

    def __getattribute__(self, item):
        if item == "ask_for":
            return self._ask_for()
        return super().__getattribute__(item)


class GenericDependencyAnnotation:
    """
    Special objects for some ways to define dependencies.
    """

    def __init__(self, **dependency_config):
        self.__dependency_config = dependency_config

    def __getitem__(self, params) -> object:
        if not isinstance(params, tuple):
            params = (params,)
        return SimpleDependency(params, **self.__dependency_config)


def usage_does_not_imply_a_dependency(bit_type: type) -> type:
    """
    Mark a Bit type as not implying a dependency when used in an attribute-style dependency specification.

    You usually do not need it.

    :param bit_type: The Bit type to mark.
    """
    bit_type._krrez_do_not_derive_a_dependency = True
    return bit_type
