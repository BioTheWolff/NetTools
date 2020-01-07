from NetworkUtilities.core.network_basic import NetworkBasic
import netifaces
from NetworkUtilities.core.utils import Utils


class NetworkProber(NetworkBasic):

    def __init__(self):
        ip, mask = None, None
        inet = netifaces.AF_INET
        addrs_raw, addrs_clean = [], []
        for interface in netifaces.interfaces():
            addrs_raw.append(netifaces.ifaddresses(interface))
        for elem in addrs_raw:
            if inet in elem.keys():
                addrs_clean.append(elem[inet])
        for elem in addrs_clean:
            addr = elem[0]['addr'].split('.')
            for p in range(3):
                allowed = self.rfc_allowed_ranges[p]
                if (int(addr[0]) == allowed[0]) and (allowed[1][0] <= int(addr[1]) <= allowed[1][1]):
                    ip = '.'.join(addr)
                    mask = elem[0]['netmask']
                    break

        super().__init__(ip, mask)

    def determine_range_reverse(self, start_ip, machine_bits):
        def _check(idx, content):
            Utils.in_rfc_range_reverse(self.rfc_current_range, idx, content[idx])

            if content[idx] == 0:
                content[idx] = 255
                return _check(idx - 1, content)
            else:
                content[idx] = content[idx] - 1
                return content

        liste = [start_ip]

        ip = start_ip.split('.')
        addresses = 2 ** machine_bits
        for e in ip:
            ip[ip.index(e)] = int(e)

        # we take 1 from addresses because the starting ip is already one
        for _ in range(addresses - 1):
            ip = _check(3, ip)
            liste.append(".".join([str(i) for i in ip]))

        for e in ip:
            ip[ip.index(e)] = str(e)

        result = {'start': start_ip, 'end': '.'.join(ip)}

        self.network_range = result

        return liste

    def estimate_range(self):

        ip = self.ip
        machine_bits = 32 - self.mask_length
        master = []

        li = self.determine_range_reverse(start_ip=ip, machine_bits=machine_bits)
        del li[-1]
        for e in li[::-1]:
            master.append(e)

        _, li = self.determine_network_range(start_ip=ip, machine_bits=machine_bits, addresses_list=True)
        for e in li:
            master.append(e)

        return master


class NetworkProbingDisplayer(NetworkProber):

    def display_range(self, display=False):
        r = self.estimate_range()
        self.network_range = {"start": r[0], "end": r[-1]}

        if display is True:
            self._display(is_prober=True)
        else:
            print("--- ESTIMATED FROM THIS MACHINE LOCAL ADDRESS ---")
            print(self.network_range)
