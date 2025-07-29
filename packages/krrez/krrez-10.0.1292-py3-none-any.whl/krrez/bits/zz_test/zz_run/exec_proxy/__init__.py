# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import time

import krrez.api


class Bit(krrez.api.Bit):

    __later: krrez.api.Later[krrez.api.IfPicked["krrez.bits.sys.config.Bit"],
                             "krrez.bits.zz_test.zz_run.exec_proxy.LateBit"]

    def __apply__(self):
        svc_exe = self._data_dir("krrez_testing_proxy.py").copy_to("/usr/local/bin/krrez_testing_proxy.py",
                                                                   executable=True)

        with self._services.create_service("krrez_testing_proxy", svc_exe) as _:
            _.add_dependency("network.target")

        self._internals.session.context.config.set("zz_test.exec_proxy.available_since", datetime.datetime.now())


class LateBit(krrez.api.Bit):
    # TODO implement waiting time simpler/more effective (e.g. instead wait in Bit until first command got executed?)

    __more_deps: krrez.api.Beforehand[krrez.api.IfPicked["krrez.bits.net.ssh.LateBit"]]

    def __apply__(self):
        available_since = self._internals.session.context.config.get("zz_test.exec_proxy.available_since")
        available_for = datetime.datetime.now() - available_since
        time.sleep(max(0.0, (datetime.timedelta(minutes=0.5) - available_for).total_seconds()))
