# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import abc
import string
import typing as t

import hallyd

import krrez.flow.dialog


def _config_dir_path_for_context_path(context_path: hallyd.fs.Path) -> hallyd.fs.Path:
    # TODO race condition ?
    return context_path("config").make_dir(exist_ok=True, preserve_perms=True, readable_by_all=True)


class Controller(abc.ABC):
    """
    Read and modify configuration values.

    This is a low-level mechanism and not what a Bit would use (see :py:class:`krrez.api.ConfigValue`). It does not
    include user dialogs.
    """

    @property
    @abc.abstractmethod
    def context(self) -> "krrez.flow.Context":
        pass

    @abc.abstractmethod
    def get(self, key: str, default: t.Optional[t.Any] = None) -> t.Optional[t.Any]:
        """
        Get the configuration value for a key.

        :param key: The key.
        :param default: The default value, if the key does not exist.
        """

    @abc.abstractmethod
    def set(self, key: str, value: t.Optional[t.Any], *, confidentially: bool = False) -> None:
        """
        Set the configuration value for a key.

        :param key: The key.
        :param value: The new value.
        """

    @abc.abstractmethod
    def lock(self, key: str) -> t.Generator[None, None, None]:
        """
        Return a context manager that locks a particular key.

        :param key: The key.
        """

    @abc.abstractmethod
    def available_keys(self, *, with_confidential: bool = False) -> list[str]:
        """
        All keys that are stored.
        """

    @staticmethod
    def key_is_valid(key: str) -> bool:
        for char in key:
            if not ((char in string.ascii_letters) or (char in string.digits) or (char in "-_.+")):
                return False
        return True

    @staticmethod
    def _verify_key_is_valid(key: str) -> None:
        if not Controller.key_is_valid(key):
            raise ValueError(f"invalid key name: {key}")


class _Controller(Controller):

    def __init__(self, context: "krrez.flow.Context"):
        super().__init__()
        self.__context = context
        self.__confidential_values = {}

    @property
    def context(self):
        return self.__context

    def lock(self, key):
        return self.__context.lock(f"value.{key}", ns=_Controller)

    def get(self, key, default=None):
        self._verify_key_is_valid(key)
        with self.lock(key):
            if key in self.__confidential_values:
                return self.__confidential_values[key]
            result = self
            value_file_path = _config_dir_path_for_context_path(self.__context.path)(key)

            if value_file_path.exists():
                result = hallyd.bindle.loads(value_file_path.read_text())
            if result is self:
                result = default
            return result

    def set(self, key, value, *, confidentially=False):
        self._verify_key_is_valid(key)
        with self.lock(key):
            if confidentially:
                self.__confidential_values[key] = value
            else:
                with open(_config_dir_path_for_context_path(self.__context.path)(key), "w") as f:
                    f.write(hallyd.bindle.dumps(value))

    def available_keys(self, *, with_confidential=False):
        return list(sorted({
            *[key.name for key in _config_dir_path_for_context_path(self.__context.path).iterdir()
              if self.key_is_valid(key.name)],
            *(self.__confidential_values.keys() if with_confidential else [])
        }))


class _InteractiveController(Controller):

    class _AskFor(krrez.flow.dialog.Endpoint, hallyd.lang.AllAbstractMethodsProvidedByTrick):

        class _None:
            pass

        def __init__(self, controller: "_InteractiveController", dialog_endpoint: "krrez.flow.dialog.Endpoint",
                     key: str, confidentially):
            super().__init__()
            self.__key = self._key = key
            self.__controller = controller
            self.__confidentially = confidentially
            self.__dialog_endpoint = dialog_endpoint

        def __getattribute__(self, item):
            if (not item.startswith("_")) and (item in dir(krrez.flow.dialog.Endpoint)):

                def method(*args, **kwargs):
                    value = self.__controller.get(self.__key, default=_InteractiveController._AskFor._None())
                    if isinstance(value, _InteractiveController._AskFor._None):
                        value = getattr(self.__dialog_endpoint, item)(*args, **kwargs)
                        self.__controller.set(self._key, value, confidentially=self.__confidentially)
                    return value

                return method

            return super().__getattribute__(item)

    def __init__(self, original_controller: Controller, dialog_endpoint: "krrez.flow.dialog.Endpoint"):
        self.__original_controller = original_controller
        super().__init__()
        self.__dialog_endpoint = dialog_endpoint

    def ask_for(self, key: str, *, confidentially: bool = False) -> "krrez.flow.dialog.Endpoint":
        return self._AskFor(self, self.__dialog_endpoint, key, confidentially)

    @property
    def context(self):
        return self.__original_controller.context

    def lock(self, key, default=None):
        return self.__original_controller.lock(key)

    def get(self, key, default=None):
        return self.__original_controller.get(key, default=default)

    def set(self, key, value, *, confidentially=False):
        return self.__original_controller.set(key, value, confidentially=confidentially)

    def available_keys(self, *, with_confidential=False):
        return self.__original_controller.available_keys(with_confidential=with_confidential)


def controller(*, context: "krrez.flow.Context") -> Controller:
    """
    A (non-interactive) config controller for a context.

    :param context: The context to access.
    """
    return _Controller(context)


def interactive_controller(*, original_controller: Controller,
                           dialog_endpoint: "krrez.flow.dialog.Endpoint") -> _InteractiveController:
    """
    An interactive config controller, wrapping a non-interactive one with a dialog endpoint.

    :param original_controller: The original controller to wrap.
    :param dialog_endpoint: The dialog endpoint.
    """
    return _InteractiveController(original_controller, dialog_endpoint)


def new_config_server_for_session(fresh_session_path: hallyd.fs.Path) -> hallyd.ipc.Server:
    """
    An IPC object-ref to a config controller for a fresh session.

    :param fresh_session_path: The session path.
    """
    context_path = fresh_session_path.parent.parent  # TODO odd
    context = krrez.flow.Context(context_path)
    return hallyd.ipc.threaded_server(context.config, path=_ipc_config_object_path(fresh_session_path))


def config_client_for_existing_session(session_path: hallyd.fs.Path) -> Controller:
    """
    An IPC object-ref to a config controller for an existing session.

    :param session_path: The session path.
    """
    return hallyd.ipc.client(_ipc_config_object_path(session_path))


def _ipc_config_object_path(session_path: hallyd.fs.Path) -> hallyd.fs.Path:
    return session_path("ipc_config")
