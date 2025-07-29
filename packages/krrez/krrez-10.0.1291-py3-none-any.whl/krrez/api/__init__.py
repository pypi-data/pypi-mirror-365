# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Main programming interface for the implementation of bits, i.e. your custom automation logic to be executed by Krrez
when it seeds a system.
"""
import dataclasses
import typing as t

import hallyd

import krrez.api.internal as _internal
import krrez.flow.bit_loader
import krrez.flow.dialog
import krrez.flow.logging

if t.TYPE_CHECKING:
    import krrez.bits.seed.common
    import krrez.bits.seed.steps.disks
    import krrez.bits.seed.steps.keyboard
    import krrez.bits.seed.steps.networking
    import krrez.bits.seed.steps.seed_user
    import krrez.bits.sys.helpers
    import krrez.bits.sys.fs
    import krrez.bits.sys.packages
    import krrez.bits.sys.scheduled_tasks
    import krrez.bits.sys.services
    import krrez.bits.sys.system_users
    import krrez.flow.graph.resolver
    import krrez.flow.writer
    import krrez.seeding


@hallyd.lang.with_friendly_repr_implementation()
class Bit(_internal.MayDeclareSecondaryBitUsages):
    """
    Base class for bits.

    Put your automation code (i.e. what is to be executed on a Krrez target machine) in a new subclass.
    This subclass must either be named `Bit` (the common case), or at least have a name that ends with `Bit` (you should
    not do that without a particular reason). It must override :py:meth:`__apply__` with your actual automation code and
    be put into a Python submodule somewhere inside `krrez.bits.`.

    In order to define dependencies, there are some options. The most common one is to add a line like this to the top
    of your Bit class body:

    .. code-block:: python

      _foo: krrez.bits.foo.Bit  # by convention, the name is the last part of the module with an underscore appended

    This line specifies a dependency, i.e. whenever your Bit is going to be applied, the infrastructure will apply
    `krrez.bits.foo.Bit` before. You either have to :code:`import krrez.bits.foo` for that (recommended at least if you
    use a real IDE), or put quotes around the type name.

    Beyond the specification of a dependency, this line has another effect: Your :py:meth:`__apply__` method can use
    this other Bit, e.g. in order to call some of its service methods, like here:

    .. code-block:: python

      def __apply__(self):
          my_thingy = ...
          self._foo.add_bar_handler(my_thingy)

    For optional dependencies, see :py:data:`IfPicked`. For some other advanced ways, see :py:data:`Beforehand`,
    :py:data:`Later` and :py:data:`Eventually`.

    In order to define a configuration value, see :py:class:`ConfigValue`.

    In order to define a lock (you only need them in some advanced cases), see :py:class:`Lock`.

    Read more in the Krrez documentation.
    """

    _helpers: "krrez.bits.sys.helpers.Bit"
    _fs: "krrez.bits.sys.fs.Bit"
    _packages: "krrez.bits.sys.packages.Bit"
    _services: "krrez.bits.sys.services.Bit"
    _system_users: "krrez.bits.sys.system_users.Bit"

    def __init__(self):
        """
        Do not construct Bits directly.
        """
        super().__init__(used_by=lambda: self._internals.origin_bit or self)
        self.__internals = self._Internals(self)

    def __apply__(self) -> None:
        """
        The automation code that realizes the intent of this Bit.

        It is directly executed on the target machine during the seed procedure, by the Krrez infrastructure, in a
        proper order with the other Bits, if it was selected for installation.
        """

    def __getattribute__(self, item):
        result = super().__getattribute__(item)
        if isinstance(result, _internal.ConnectableToBit):
            return result._connected_to_bit(self, item)
        return result

    def __setattr__(self, item, value):
        try:
            super_result = self.__dict__.get(item)
        except AttributeError:
            super_result = None
        if isinstance(super_result, _internal.BareConfigValue):
            raise AttributeError(f"you need to use the .setter in order to set config values")

        return super().__setattr__(item, value)

    def __eq__(self, o):
        return isinstance(o, Bit) and (self.name == o.name)

    def __hash__(self):
        return hash(self.name)

    @property
    def name(self) -> str:
        """
        The Bit name.

        You usually do not need it.
        """
        return krrez.flow.bit_loader.bit_name(self)

    @property
    def _data_dir(self) -> hallyd.fs.Path:
        """
        The path of this Bit's data directory.

        This is the "`-data`" subdirectory of the directory that contains your Bit module file.
        """
        return krrez.flow.bit_loader.bit_module_path(self).parent("-data")

    @property
    def _log(self) -> krrez.flow.logging.Logger:
        """
        The logger.
        """
        return self._internals.log_block or krrez.api.internal.AdHocLogger()

    @property
    def _internals(self) -> "_Internals":
        """
        Internal features that are usually not needed to be used.
        """
        return self.__internals

    def _bit_for_type(self, bit_type):
        try:
            if not self._internals.context.is_bit_installed(bit_type) and not getattr(bit_type, "_krrez_do_not_derive_a_dependency", False):
                return None
        except PermissionError:
            pass  # this happens in very special situations (bits are used by non-root users) and is fine to ignore

        return super()._bit_for_type(bit_type)

    class _Internals:

        def __init__(self, bit: "Bit"):
            self.__bit = bit
            self.__origin_bit = None
            self.__session = None
            self.__my_log_block = None
            self.__dialog_endpoint = None

        @property
        def origin_bit(self) -> t.Optional["Bit"]:
            return self.__origin_bit or (self.__bit if self.__dialog_endpoint else None)

        @property
        def context(self) -> krrez.flow.Context:
            return self.session.context if self.session else krrez.flow.Context()

        @property
        def session(self) -> t.Optional[krrez.flow.Session]:
            return (self.__origin_bit or self.__bit)._internals.__session

        @property
        def dialog_endpoint(self) -> t.Optional["krrez.flow.dialog.Endpoint"]:
            return (self.__origin_bit or self.__bit)._internals.__dialog_endpoint

        @property
        def log_block(self) -> t.Optional["krrez.flow.writer.Writer.LogBlock"]:
            return (self.__origin_bit or self.__bit)._internals.__my_log_block

        def initialize_as_secondary(self, origin_bit: "Bit") -> None:
            self.__origin_bit = origin_bit

        def prepare_apply(self, session: "krrez.flow.Session", log_block: "krrez.flow.writer.Writer.LogBlock",
                          dialog_endpoint: "krrez.flow.dialog.Endpoint") -> None:
            self.__session = session
            self.__my_log_block = log_block
            self.__dialog_endpoint = dialog_endpoint


@hallyd.lang.with_friendly_repr_implementation()
class Profile(metaclass=_internal.ProfileMeta):
    """
    Base class for Profiles.

    A profile collects all kinds of setup, including system settings like disk partitioning, and a list of Krrez Bits
    to install. Whenever to install a new Krrez system, the seeding procedure, and so the target system, is defined by
    the Profile you choose.
    """

    def __init__(self, *, hostname: str, disks: list["krrez.bits.seed.steps.disks.Disk"],
                 raid_partitions: list["krrez.bits.seed.steps.disks.RaidPartition"],
                 network_interfaces: list["krrez.bits.seed.steps.networking.NetworkInterface"], krrez_bits: list[str],
                 arch: str, operating_system: "krrez.bits.seed.common.OperatingSystem",
                 seed_strategy: "krrez.seeding.SeedStrategy", keyboard: "krrez.bits.seed.steps.keyboard.Keyboard",
                 locale: str, timezone: str, seed_user: t.Optional["krrez.bits.seed.steps.seed_user.SeedUser"],
                 config: dict[str, t.Any], drivers: list[str]):
        self.hostname = hostname
        self.disks = disks
        self.raid_partitions = raid_partitions
        self.network_interfaces = network_interfaces
        self.krrez_bits = krrez_bits
        self.arch = arch
        self.operating_system = operating_system
        self.seed_strategy = seed_strategy
        self.keyboard = keyboard
        self.locale = locale
        self.timezone = timezone
        self.seed_user = seed_user
        self.config = dict(config or ())
        self.drivers = drivers
        self.first_boot_actions = []

    def __to_json_dict__(self):
        return dict(self.__dict__)

    @classmethod
    def get(cls, data) -> "Profile":
        profile = cls(**data)
        profile.config["profile_created_as"] = (cls, data)
        return profile

    @classmethod
    def __from_json_dict__(cls, json_dict):
        result = Profile.__new__(Profile)
        result.__dict__.update(json_dict)
        return result

    def to_flow_config_dict(self) -> dict[str, t.Any]:
        return {f"seed.{key}": getattr(self, key) for key in self.__dict__}

    is_hidden = False

    @dataclasses.dataclass(frozen=True)
    class Parameter:
        name: str
        type: type[t.Any]


#: Specifies a list of Bits as no-order dependencies, i.e. enforcing the specified Bits to be applied when this is one
#: will, no matter if afterward or beforehand, like this:
#: :code:`__eventually: krrez.api.Eventually["krrez.bits.foo.Bit", "krrez.bits.bar.Bit", ...]`.
Eventually = _internal.GenericDependencyAnnotation(afterwards=None)


#: Specifies a list of Bits as reverse-order dependencies, i.e. similar to usual dependencies, but applying the
#: specified Bits *after* the own Bit was applied, like this:
#: :code:`__later: krrez.api.Later["krrez.bits.foo.Bit", "krrez.bits.bar.Bit", ...]`.
Later = _internal.GenericDependencyAnnotation(afterwards=True)


#: A simpler way to specify multiple dependencies if you do not need them as dedicated property in
#: :py:meth:`Bit.__apply__`. You can annotate one property with it and specify multiple Bit types like this:
#: :code:`__more_deps: krrez.api.Beforehand["krrez.bits.foo.Bit", "krrez.bits.bar.Bit", ...]`.
Beforehand = _internal.GenericDependencyAnnotation(afterwards=False)


#: Modifier for a dependency specification.
#:
#: A dependency specification can be marked as optional by putting :code:`krrez.api.IfPicked[...]` around the type.
#: Such a dependency specification will influence the order, but it will not enforce the other Bit to be applied. If
#: it is not at all in the list of Bits to be applied, this dependency specification will not make it part of the list.
#:
#: Inside your :py:meth:`Bit.__apply__` code, this property is :code:`None` if that Bit was optional and not applied.
#:
#: It may also be used in :py:data:`Beforehand` and :py:data:`Later` specifications.
IfPicked = t.Optional


ConfigValue = _internal.ConfigValue
Lock = _internal.Lock
Path = hallyd.fs.Path
