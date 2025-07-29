# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import contextlib
import importlib

import hallyd
import klovve

import krrez.flow
import krrez.ui


@contextlib.contextmanager
def app(app_name: str, context_path: hallyd.fs.TInputPath, **kwargs):  # TODO move to krrez.ui ?!
    application = importlib.import_module(f"krrez.ui.apps.{app_name}").Application(
        runtime_data=krrez.ui.RuntimeData(
            context=krrez.flow.Context(hallyd.fs.Path(context_path) if context_path else None)), **kwargs)

    application_controller = klovve.app.create(application)
    yield application, application_controller
