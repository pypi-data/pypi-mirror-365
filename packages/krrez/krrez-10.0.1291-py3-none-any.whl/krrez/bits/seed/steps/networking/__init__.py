# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import json
import os
import socket
import subprocess
import time
import typing as t

import hallyd

import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):

    network_interfaces = krrez.seeding.api.ConfigValue(default=[], type=list["NetworkInterface"])


class InTargetBit(Bit):

    def __apply__(self):
        for i, interface in enumerate(self.network_interfaces.value):
            systemd_match = f"[Match]\nName={interface.name}"
            systemd_network = "[Network]\n"
            systemd_network_post = ""
            systemd_network_name = f"00-psbnet{i}"

            if isinstance(interface, WirelessNetworkInterface):
                self._packages.install("wpasupplicant")

                interfaceconfigpath = f"/etc/wpa_supplicant/wpa_supplicant-{interface.name}.conf"
                with open(interfaceconfigpath, "w") as f:
                    f.write(f"ctrl_interface=/var/run/wpa_supplicant\n"
                            f"ctrl_interface_group=root\n"
                            f"ap_scan=1\n"
                            f"network={{\n"
                            f" ssid=\"{interface.ssid}\"\n"
                            f" scan_ssid=1\n"
                            f" psk=\"{interface.passphrase}\"\n"
                            f"}}\n")
                os.chmod(interfaceconfigpath, 0o600)
                subprocess.check_call(["systemctl", "enable", f"wpa_supplicant@{interface.name}"])

            for connection in interface.connections:
                if isinstance(connection, ConnectIp4ByDHCP):
                    systemd_network += "DHCP=ipv4\n"
                elif isinstance(connection, ConnectIPv4ByStaticAddress):
                    for addr in connection.own_addresses:
                        systemd_network += f"Address={addr}\n"
                    systemd_network_post += f"[Route]\nGateway={connection.gateway}\nMetric=2000\n\n"
                    for dns in connection.dns_servers:
                        systemd_network += f"DNS={dns}\n"
                    if connection.allow_dhcp_fallback_initially:
                        self.__allow_dhcp_fallback_initially_for_connection(systemd_network_name)
                elif isinstance(connection, ConnectIPv6ByStaticAddress):
                    for addr in connection.own_addresses:
                        systemd_network += f"Address={addr}\n"
                    systemd_network_post += f"[Route]\nGateway={connection.gateway}\nMetric=2000\n\n"
                    for dns in connection.dns_servers:
                        systemd_network += f"DNS={dns}\n"
                else:
                    raise ValueError(f"connection type unsupported: {type(connection).__name__}")

            self._fs(f"/etc/systemd/network/{systemd_network_name}.network").write_text(
                f"{systemd_match}\n\n{systemd_network}\n\n{systemd_network_post}[DHCPv4]\nUseHostname=false\n")

        run_resolve_path = self._fs("/run/systemd/resolve").make_dir(until="/",
                                                                     exist_ok=True, readable_by_all=True)
        self._fs("/etc/resolv.conf").copy_to(run_resolve_path("stub-resolv.conf"), readable_by_all=True)
        self._packages.install("systemd-resolved", "networkd-dispatcher")
        for svc in ["systemd-networkd", "systemd-resolved", "networkd-dispatcher"]:
            subprocess.check_call(["systemctl", "enable", svc])

    def __allow_dhcp_fallback_initially_for_connection(self, systemd_network_name: str) -> None:
        drop_in_dir = self._fs(f"/etc/systemd/network/{systemd_network_name}.network.d").make_dir(readable_by_all=True)
        drop_in_dir("allow_dhcp_fallback_initially.conf").write_text(
            "[Network]\n"
            "DHCP=ipv4\n")
        service_name = f"dhcp_fallback_{systemd_network_name}"
        with hallyd.services.create_service(
                service_name,
                self._AllowDhcpFallbackInitiallyControllerActionTask(service_name, systemd_network_name)) as _:
            _.do_not_start_instantly()

    class _AllowDhcpFallbackInitiallyControllerActionTask(hallyd.services.Runnable):

        def __init__(self, service_name, systemd_network_name):
            self.service_name = service_name
            self.systemd_network_name = systemd_network_name

        def run(self):
            while True:
                time.sleep(300)
                if self.__dhcp_is_unneeded():
                    self.__remove()
                    break

        def __dhcp_is_unneeded(self):
            if not self.__is_ipv4_online():
                return None

            network_interfaces = self.__network_interfaces()
            for ip_route_line in subprocess.check_output(["ip", "route"]).decode().split("\n"):
                if " proto dhcp " in ip_route_line:
                    for network_interface in network_interfaces:
                        if f" dev {network_interface} " in ip_route_line:
                            return False

            if not self.__is_ipv4_online():
                return None

            return True

        def __network_interfaces(self):
            network_interfaces = []
            network_info = json.loads(subprocess.check_output(["networkctl", "list", "--json=short"]))
            for interface_info in network_info["Interfaces"]:
                interface_name = interface_info.get("Name")
                network_file = interface_info.get("NetworkFile")
                if network_file == f"/etc/systemd/network/{self.systemd_network_name}.network":
                    network_interfaces.append(interface_name)
            return network_interfaces

        def __is_ipv4_online(self):
            for external_host_name in ["kernel.org", "debian.org", "wikipedia.org", "koeln.de"]:
                try:
                    for addr_tuple in socket.getaddrinfo(external_host_name, 0):
                        if addr_tuple[0] == socket.AddressFamily.AF_INET:
                            try:
                                socket.setdefaulttimeout(4)
                                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                s.connect((addr_tuple[4][0], 443))
                            except IOError:
                                continue
                            else:
                                s.close()
                                return True
                except Exception:
                    continue
            return False

        def __remove(self):
            drop_in_dir = hallyd.fs.Path(f"/etc/systemd/network/{self.systemd_network_name}.network.d")
            drop_in_dir("allow_dhcp_fallback_initially.conf").unlink()
            subprocess.check_call(["networkctl", "reload"])
            subprocess.check_call(["systemctl", "disable", self.service_name])
            hallyd.fs.Path(f"/etc/systemd/system/{self.service_name}.service").unlink()
            subprocess.check_call(["systemctl", "daemon-reload"])


@hallyd.lang.with_friendly_repr_implementation()
class _Connection:
    """
    Networking settings for one connection. This is an abstract class, look for subclasses.
    """
    pass


class ConnectIp4ByDHCP(_Connection):
    """
    An IPv4 connection using dhcp.
    """
    pass


class _ConnectIpByStaticAddress(_Connection):

    def __init__(self, *, own_addresses: list[str], gateway: t.Optional[str] = None,
                 dns_servers: t.Optional[list[str]] = None):
        """
        :param own_addresses: List of own addresses (all ending with `"/<prefixlength>"`).
        :param gateway: Address of the default gateway.
        :param dns_servers: List of addresses to dns servers.
        """
        super().__init__()
        self.own_addresses = [own_addresses] if isinstance(own_addresses, str) else own_addresses
        self.gateway = gateway
        self.dns_servers = [dns_servers] if isinstance(dns_servers, str) else dns_servers

    @property
    def own_addresses(self) -> list[str]:
        return self.__own_addresses

    @own_addresses.setter
    def own_addresses(self, v):
        for ipaddr in v:
            if "/" not in ipaddr:
                raise ValueError("own_addresses must contain '/' specifying the network part")
        self.__own_addresses = v


class ConnectIPv4ByStaticAddress(_ConnectIpByStaticAddress):
    """
    An IPv4 connection using static addresses.
    """

    def __init__(self, *, own_addresses: list[str], gateway: t.Optional[str] = None,
                 dns_servers: t.Optional[list[str]] = None, allow_dhcp_fallback_initially: bool = False):
        """
        :param own_addresses: List of own addresses (all ending with `"/<prefixlength>"`).
        :param gateway: Address of the default gateway.
        :param dns_servers: List of addresses to dns servers.
        :param allow_dhcp_fallback_initially: Whether to use DHCP as long as it is available and only switch to static
                                              addresses once DHCP is not available anymore.
        """
        super().__init__(own_addresses=own_addresses, gateway=gateway, dns_servers=dns_servers)
        self.allow_dhcp_fallback_initially = allow_dhcp_fallback_initially


class ConnectIPv6ByStaticAddress(_ConnectIpByStaticAddress):
    """
    An IPv6 connection using static addresses.
    """


@hallyd.lang.with_friendly_repr_implementation()
class NetworkInterface:
    """
    Networking settings for one network interface.
    """

    def __init__(self, name: str, *connections: _Connection):
        """
        :param name: The interface name.
        """
        self.name = name
        self.connections = list(connections)


class WirelessNetworkInterface(NetworkInterface):
    """
    Networking settings for one Wi-Fi network interface, connected to a specified Wi-Fi network.
    """

    def __init__(self, name: str, *connections: _Connection, ssid: str, passphrase: str):
        """
        :param ssid: The Wi-Fi SSID to connect to.
        :param passphrase: The passphrase for this Wi-Fi network.
        """
        super().__init__(name, *connections)
        self.ssid = ssid
        self.passphrase = passphrase
