# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import random
import syslog
import traceback
import typing as t
import xml.etree.ElementTree
import xml.sax.saxutils

import hallyd

import krrez.bits.zz_test.zz_run._libvirt
import krrez.bits.zz_test.zz_run._machine


class Network:

    # noinspection PyProtectedMember
    def __init__(self, run: "krrez.bits.zz_test.zz_run.Bit"):
        import libvirt
        self.__run = run
        self.__name = f"krrez-test-{run.test_id}"
        with run._internals.session.context.lock("networks", ns=Network):
            for network in krrez.bits.zz_test.zz_run._libvirt.all_networks():
                if network.name() == self.__name:
                    self.__libvirt_network = network
                    break
            else:
                for ip4network, ip4netmask in self.__private_ip4_networks():
                    ip4_host = ".".join([str(i) for i in ip4network[:3]]) + ".1"
                    ip4_netmask = ".".join([str(i) for i in ip4netmask])
                    ip4_dhcp_range_start = ".".join([str(i) for i in ip4network[:3]]) + ".2"
                    ip4_dhcp_range_end = ".".join([str(i) for i in ip4network[:3]]) + ".254"
                    network_xml = f"""
                        <network>
                            <name>{self.__name}</name>
                            <forward mode='nat'>
                                <nat>
                                    <port start='1' end='65535'/>
                                </nat>
                            </forward>
                            <bridge stp='on' delay='0'/>
                            <ip address='{ip4_host}' netmask='{ip4_netmask}'>
                                <dhcp>
                                    <range start='{ip4_dhcp_range_start}' end='{ip4_dhcp_range_end}'/>
                                </dhcp>
                            </ip>
                            <dns forwardPlainNames="no"/>
                        </network>
                    """
                    self.__libvirt_network = krrez.bits.zz_test.zz_run._libvirt.define_network(network_xml)
                    try:
                        hallyd.cleanup.add_cleanup_task(krrez.bits.zz_test.zz_run._libvirt.remove_network, self.__name)
                        self.__libvirt_network.create()
                        self.__libvirt_network.setAutostart(True)
                        break
                    except libvirt.libvirtError:
                        syslog.syslog(syslog.LOG_DEBUG, f"Unable to create network.\n{traceback.format_exc()}")
                        self.__libvirt_network.undefine()
                        self.__libvirt_network = None
                else:
                    raise RuntimeError("could not find any free network")

                self._add_dns(self.host_ip4_address, self.host_hostnames)

    @property
    def host_ip4_address(self) -> str:
        return xml.etree.ElementTree.fromstring(self.__libvirt_network.XMLDesc()).find("ip").attrib["address"]

    @property
    def host_hostnames(self) -> t.Iterable[str]:
        return ["x--host.krz"]

    @property
    def name(self) -> str:
        return self.__name

    def add_machine(self, machine: "krrez.bits.zz_test.zz_run.Machine") -> None:
        import libvirt

        try:
            self.__libvirt_network.update(libvirt.VIR_NETWORK_UPDATE_COMMAND_DELETE,
                                          libvirt.VIR_NETWORK_SECTION_IP_DHCP_HOST,
                                          -1, f"<host mac='{machine.mac_address}'/>")
        except:
            self.__run._log.message.debug(traceback.format_exc())

        try:
            self.__libvirt_network.update(libvirt.VIR_NETWORK_UPDATE_COMMAND_DELETE,
                                          libvirt.VIR_NETWORK_SECTION_IP_DHCP_HOST,
                                          -1, f"<host ip='{machine.ip4_address}'/>")
        except:
            self.__run._log.message.debug(traceback.format_exc())

        self.__libvirt_network.update(libvirt.VIR_NETWORK_UPDATE_COMMAND_ADD_LAST,
                                      libvirt.VIR_NETWORK_SECTION_IP_DHCP_HOST,
                                      -1, f"<host mac='{machine.mac_address}' ip='{machine.ip4_address}'/>")

        xhostnames = ""
        for hostname in machine.hostnames:
            xhostnames += f"<hostname>{xml.sax.saxutils.escape(hostname)}</hostname>"

        self._add_dns(machine.ip4_address, machine.hostnames)

    def mac_address_for_machine(self, machine: "krrez.bits.zz_test.zz_run.Machine") -> str: # TODO !!!!!!!!!!!!!!!!!!!
        with self.__run._internals.session.context.lock("mac_addresses", ns=Network):
            mac_addresses = self.__run.run_data("mac_addresses") or {}
            result = mac_addresses.get(machine.short_name)
            if not result:
                while (not result) or (result in mac_addresses.values()):
                    a, b, c = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                    result = ":".join([f"{x:02x}" for x in [0x52, 0x54, 0x00, a, b, c]])
                mac_addresses[machine.short_name] = result
                self.__run.set_run_data("mac_addresses", {machine.short_name: result, **mac_addresses})
        return result
    
    def ip4_address_for_machine(self, machine: "krrez.bits.zz_test.zz_run.Machine") -> str:
        with self.__run._internals.session.context.lock("ip4_addresses", ns=Network):
            ip4_addresses = self.__run.run_data("ip4_addresses") or {}
            result = ip4_addresses.get(machine.short_name)
            if not result:
                network_part = self.host_ip4_address.split(".")[:3]
                while (not result) or (result in ip4_addresses.values()):
                    result = ".".join([*network_part, str(random.randint(3, 254))])
                ip4_addresses[machine.short_name] = result
                self.__run.set_run_data("ip4_addresses", ip4_addresses)
        return result

    def _add_dns(self, ip4_address: str, hostnames: t.Iterable[str]) -> None:
        import libvirt

        xhostnames = ""
        for hostname in hostnames:
            xhostnames += f"<hostname>{xml.sax.saxutils.escape(hostname)}</hostname>"

        try:
            self.__libvirt_network.update(libvirt.VIR_NETWORK_UPDATE_COMMAND_DELETE,
                                          libvirt.VIR_NETWORK_SECTION_DNS_HOST,
                                          -1, f"<host>{xhostnames}</host>")
        except:
            self.__run._log.message.debug(traceback.format_exc())

        self.__libvirt_network.update(libvirt.VIR_NETWORK_UPDATE_COMMAND_ADD_LAST,
                                      libvirt.VIR_NETWORK_SECTION_DNS_HOST,
                                      -1, f"<host ip='{ip4_address}'>{xhostnames}</host>")

    def __private_ip4_networks(self):
        for part2 in range(256):
            yield (10, 250, part2, 0), (255, 255, 255, 0)
