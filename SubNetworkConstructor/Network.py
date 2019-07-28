import netifaces


class Network:
    lang = 'fr'
    ip, mask, address_type = None, None, None
    mask_length, addresses = 0, 0
    rfc_current_range, rfc_masks = None, [16, 12, 8]
    rfc_allowed_ranges = [[192, [168, 168]], [172, [16, 31]], [10, [0, 255]]]
    network_range = {}
    lang_dict = {
        'fr': {
            'network': "Réseau :",
            'cidr': "CIDR : {}/{}",
            'cidr_adv': "CIDR (Classless Inter Domain Routing) : {}/{}",
            'addr_avail': "{} adresses disponibles",
            'addr_avail_advanced': "{} adresses occupées sur {} adresses disponibles",
            'addr_types': {
                'net': "réseau",
                'mac': "machine",
                'bct': "broadcast"
            },
            'addr_type': "L'adresse {} est une adresse {}",

            'subnets': "{} sous-réseau{}",
            'sub_addr': "{} - {} ({} adresses)",
            'sub_addr_advanced': "{} - {} ({} adresses disponibles, {} demandées)",
            'net_usage': "Occupation du réseau :"
        },
        'en': {
            'network': "Network:",
            'cidr': "CIDR : {}/{}",
            'cidr_adv': "CIDR (Classless Inter Domain Routing) : {}/{}",
            'addr_avail': "{} available addresses",
            'addr_avail_advanced': "{} occupied addresses out of {} available addresses",
            'addr_types': {
                'net': "network",
                'mac': "computer",
                'bct': "broadcast"
            },
            'addr_type': "The address {} is a {} address",

            'subnets': "{} sub-network{}",
            'sub_addr': "{} - {} ({} addresses)",
            'sub_addr_advanced': "{} - {} ({} available addresses, {} requested)",
            'net_usage': "Network usage:"
        }
    }
    error_dict = {
        'fr': {
            'ip_bytes_length': "L'IP doit faire 4 octets, trouvé {} octect(s)",
            'ip_number_off_limits': "Les octects de l'IP doivent être entre 0 et 255. Trouvé {} à l'octect {}",
            'ip_off_network_range': "L'adresse IP n'est pas dans la plage réseau.",

            'mask_bytes_length': "Le masque doit faire 4 octets, trouvé {} octect(s)",
            'mask_number_off_limits': "Les octects du masque doivent être entre 0 et 255. Trouvé {} à l'octect {}",
            'mask_length_off_bounds': "Longueur du masque ({}) hors limites [0-32]",
            'mask_incorrect': "Masque incorrect. Valeurs acceptées: [0,128,192,224,240,248,242,254,255]",
            'mask_too_small': "La longueur du masque donnée ({}) ne peut contenir toutes les adresses des "
                              "sous-réseaux. Longueur conseillée : {}",

            'rfc_ip_wrong_range': "L'IP doit être sous la forme 192.168.x.x , 172.16.x.x ou 10.0.x.x; "
                                  "trouvé {}.{}.x.x",
            'rfc_couple': "Selon les standards RFC, le couple doit être {}.{}.x.x/>={}, trouvé masque de longueur {}",
            'rfc_ips_diff_network': "L'IP de départ ({}) et l'IP ({}) ne sont pas sur le même réseau local",

            'network_limit': "Limite 255.255.255.255 atteinte en essayant de définir une plage (de sous-)réseau."
        },
        'en': {
            'ip_bytes_length': "IP must be 4 bytes long, found {} byte(s)",
            'ip_number_off_limits': "IP bytes must be between 0 and 255. Found {} at byte {}",
            'ip_off_network_range': "IP address not in network range.",

            'mask_bytes_length': "Mask must be 4 bytes long, found {} bytes",
            'mask_number_off_limits': "Mask bytes must be between 0 and 255. Found {} at byte {}",
            'mask_length_off_bounds': "Provided mask length ({}) out of bounds [0-32]",
            'mask_incorrect': "Incorrect mask. Allowed values: [0,128,192,224,240,248,242,254,255]",
            'mask_too_small': "Given mask length ({}) cannot handle all the addresses of the subnetworks. "
                              "Advised length : {}",

            'rfc_ip_wrong_range': "IP must be either 192.168.x.x , 172.16.x.x or 10.0.x.x; found {}.{}.x.x",
            'rfc_couple': "According to RFC standards, given couple must be {}.{}.x.x/>={}, found mask length {}",
            'rfc_ips_diff_network': "Starting IP ({}) and IP ({}) are not on the same local network",

            'network_limit': "Limit 255.255.255.255 reached while trying to determine (sub)network range."
        }
    }

    @staticmethod
    def _bin_to_dec(binary):
        forbidden = ['2', '3', '4', '5', '6', '7', '8', '9']

        binary = str(binary)[::-1]
        binary = list(binary)

        # we check there are only 0's and 1's in the number
        if any(item in forbidden for item in binary):
            raise Exception("Binary can only be formed of 0 and 1.")

        result = 0

        for i in range(len(binary)):
            if binary[i] == '1':
                result += 2 ** i

        return result

    @staticmethod
    def __dec_to_bin(decimal):
        return int(bin(decimal), base=0)

    @staticmethod
    def _switch_length(mask_length):
        nb = 0
        if mask_length == 1:
            nb = 128
        elif mask_length == 2:
            nb = 192
        elif mask_length == 3:
            nb = 224
        elif mask_length == 4:
            nb = 240
        elif mask_length == 5:
            nb = 248
        elif mask_length == 6:
            nb = 252
        elif mask_length == 7:
            nb = 254
        elif mask_length == 8:
            nb = 255
        elif mask_length == 0:
            nb = 0
        return nb

    def __display_network(self):
        print(self.lang_dict[self.lang]['network'])
        print(self.lang_dict[self.lang]['cidr'].format(self.ip, self.mask_length))
        print("{} - {}".format(self.network_range['start'], self.network_range['end']))
        print(self.lang_dict[self.lang]['addr_avail'].format(self.addresses))

        if self.address_type is not None:
            print('')

            if self.address_type == 0:
                machine_type = self.lang_dict[self.lang]['addr_types']['net']
            elif self.address_type == 1:
                machine_type = self.lang_dict[self.lang]['addr_types']['mac']
            elif self.address_type == 2:
                machine_type = self.lang_dict[self.lang]['addr_types']['bct']
            else:
                raise Exception("Given address type other than expected address types")

            print(self.lang_dict[self.lang]['addr_type'].format(self.ip, machine_type))

    def _verify_provided_types(self):
        temp = self.ip.split('.')
        if len(temp) != 4:
            raise Exception(self.error_dict[self.lang]['ip_bytes_length'].format(len(temp)))
        for i in range(len(temp)):
            if not (0 <= int(temp[i]) <= 255):
                raise Exception(self.error_dict[self.lang]['ip_number_off_limit'].format(temp[i], i))

        try:
            temp = self.mask.split('.')
            if len(temp) != 4:
                raise Exception(self.error_dict[self.lang]['mask_bytes_length'].format(len(temp)))
            for i in range(len(temp)):
                if not (0 <= int(temp[i]) <= 255):
                    raise Exception(self.error_dict[self.lang]['mask_number_off_limit'].format(temp[i], i))
        except (AttributeError, ValueError):
            if 0 <= int(self.mask) <= 32:
                return
            else:
                raise Exception(self.error_dict[self.lang]['mask_length_off_bounds'].format(self.mask))

    def _verify_rfc_rules(self):
        # For more information on RFC 1918 standards, check https://tools.ietf.org/html/rfc1918
        def _check(content):
            ip_test = False
            for i in range(3):
                if (int(content[0]) == self.rfc_allowed_ranges[i][0]) and \
                        (self.rfc_allowed_ranges[i][1][0] <= int(content[1]) <= self.rfc_allowed_ranges[i][1][1]):
                    ip_test = True
                    self.rfc_current_range = i

            if ip_test is False:
                raise Exception(self.error_dict[self.lang]['rfc_ip_wrong_range'].format(ip[0], ip[1]))

        ip = self.ip.split('.')
        mask = self.mask_length

        # We check that starting ip respects RFC standards
        _check(ip)

        # We then check that provided mask corresponds to RFC standards
        if (int(ip[0]) == 192 and int(ip[1]) == 168) and mask < 16:
            raise Exception(self.error_dict[self.lang]['rfc_couple'].format(ip[0], ip[1], 16, mask))
        elif (int(ip[0]) == 172 and int(ip[1]) == 16) and mask < 12:
            raise Exception(self.error_dict[self.lang]['rfc_couple'].format(ip[0], ip[1], 12, mask))
        elif (int(ip[0]) == 10 and int(ip[1]) == 0) and mask < 8:
            raise Exception(self.error_dict[self.lang]['rfc_couple'].format(ip[0], ip[1], 8, mask))

    def mask_length_to_readable(self, mask_length):
        if mask_length <= 8:
            result = "{}.0.0.0".format(self._switch_length(mask_length))
        elif 8 < mask_length <= 16:
            mask_length -= 8
            result = "255.{}.0.0".format(self._switch_length(mask_length))
        elif 16 < mask_length <= 24:
            mask_length -= 16
            result = "255.255.{}.0".format(self._switch_length(mask_length))
        elif 24 < mask_length <= 32:
            mask_length -= 24
            result = "255.255.255.{}".format(self._switch_length(mask_length))
        else:
            raise Exception(self.error_dict[self.lang]['mask_length_off_bounds'].format(mask_length))
        return result

    def calculate_mask(self):
        try:
            temp = self.mask.split('.')
            length = 0
            for i in range(4):
                concerned = int(temp[i])
                if concerned == 255:
                    length += 8
                elif concerned == 254:
                    length += 7
                    break
                elif concerned == 252:
                    length += 6
                    break
                elif concerned == 248:
                    length += 5
                    break
                elif concerned == 240:
                    length += 4
                    break
                elif concerned == 224:
                    length += 3
                    break
                elif concerned == 192:
                    length += 2
                    break
                elif concerned == 128:
                    length += 1
                    break
                elif concerned == 0:
                    break
                else:
                    raise Exception(self.error_dict[self.lang]['mask_incorrect'])
            self.mask_length = length
        except AttributeError:
            self.mask_length = self.mask
            self.mask = self._switch_length(self.mask)
        finally:
            self.addresses = 2 ** (32 - self.mask_length) - 2

    def __init__(self, ip, mask, english=None, probe=None):
        if ip is None and mask is None and probe is True:
            inet = netifaces.AF_INET
            addrs_raw, addrs_clean = [], []
            for interface in netifaces.interfaces():
                addrs_raw.append(netifaces.ifaddresses(interface))
            for i in range(len(addrs_raw)):
                if inet in addrs_raw[i].keys():
                    addrs_clean.append(addrs_raw[i][inet])
            for i in range(len(addrs_clean)):
                addr = addrs_clean[i][0]['addr'].split('.')
                for p in range(3):
                    allowed = self.rfc_allowed_ranges[p]
                    if (int(addr[0]) == allowed[0]) and (allowed[1][0] <= int(addr[1]) <= allowed[1][1]):
                        self.ip = '.'.join(addr)
                        self.mask = addrs_clean[i][0]['netmask']
                        break
        else:
            self.ip = ip
            self.mask = mask

        if english is True:
            self.lang = 'en'

        self._verify_provided_types()
        self.calculate_mask()
        self._verify_rfc_rules()

    def determine_network_range(self, start_ip=None, machine_bits=None, returning=None, display=None):
        if start_ip is None:
            c = self.rfc_current_range
            start = "{}.{}.0.0".format(self.rfc_allowed_ranges[c][0], self.rfc_allowed_ranges[c][1][0])
        else:
            start = start_ip
        if machine_bits is None:
            machine_bits = 32 - self.mask_length

        # gives the range of the network depending on the mask
        def _check(idx, content):
            if idx == 0 and content[idx] == 255:
                raise Exception(self.error_dict[self.lang]['network_limit'])

            if content[idx] == 255:
                content[idx] = 0
                return _check(idx - 1, content)
            else:
                content[idx] = content[idx] + 1
                return content

        if (start_ip is None and returning is None) and (self.mask_length == self.rfc_masks[self.rfc_current_range]):

            if self.rfc_current_range == 0:
                result = {'start': "192.168.0.0", 'end': "192.168.255.255"}
            elif self.rfc_current_range == 1:
                result = {'start': "172.16.0.0", 'end': "172.31.255.255"}
            elif self.rfc_current_range == 2:
                result = {'start': "10.0.0.0", 'end': "10.255.255.255"}
            else:
                raise Exception("Something wrong happened when nothing should. Try contacting the author to solve this")

        else:
            ip = start.split('.')
            addresses = 2 ** machine_bits
            for i in range(len(ip)):
                ip[i] = int(ip[i])

            # we take 1 from addresses because the starting ip is already one
            for i in range(addresses - 1):
                ip = _check(3, ip)

            for i in range(len(ip)):
                ip[i] = str(ip[i])

            result = {'start': start, 'end': '.'.join(ip)}

        # if returning is None, it means the method wasn't called by the subclass SubNetworkBuilder, no need to return
        if returning is None:
            self.network_range = result
        else:
            return result

        if display is True:
            self.__display_network()
        elif display is False:
            print(result)

    def determine_type(self, display=None):
        def _check_end(idx=0):
            if self.network_range['end'].split('.')[idx] <= self.ip.split('.')[idx]:
                return False
            else:
                if idx == 3:
                    return True
                else:
                    return _check_end(idx + 1)

        def _check_start(idx=0):
            if self.network_range['start'].split('.')[idx] >= self.ip.split('.')[idx]:
                return False
            else:
                if idx == 3:
                    return True
                else:
                    return _check_start(idx + 1)

        if self.network_range == {}:
            self.determine_network_range()

        if _check_end() or _check_start():
            raise Exception(self.error_dict[self.lang]['ip_off_network_range'])

        if self.network_range['start'] == self.ip:
            self.address_type = 0
        elif self.network_range['end'] == self.ip:
            self.address_type = 2
        else:
            self.address_type = 1

        if display is True:
            self.__display_network()
        elif display is False:
            if self.address_type == 0:
                machine_type = self.lang_dict['en']['addr_types']['net']
            elif self.address_type == 1:
                machine_type = self.lang_dict['en']['addr_types']['mac']
            elif self.address_type == 2:
                machine_type = self.lang_dict['en']['addr_types']['bct']
            else:
                raise Exception("Given address type other than expected address types")

            temp = self.network_range
            temp['address_type'] = machine_type
            print(temp)


class SubnetworkBuilder(Network):
    subnets_sizes, subnets, submasks_machine_bits = [], [], []

    def __display_subnets(self, advanced):

        # graph
        occupied = 0
        for i in range(len(self.submasks_machine_bits)):
            occupied += 2 ** self.submasks_machine_bits[i] - 2
        percentage = round((occupied / self.addresses) * 100)
        graph = '['
        current = 0
        for i in range(20):
            if current < percentage:
                graph += '█'
            else:
                graph += '░'
            current += 5
        graph += "] {} %".format(percentage)

        if self.lang == 'en':
            if len(self.subnets):
                t = 's'
            else:
                t = ''
        else:
            if len(self.subnets):
                t = 'x'
            else:
                t = ''

        print(self.lang_dict[self.lang]['network'])
        if advanced is True:
            print(self.lang_dict[self.lang]['cidr_adv'].format(self.ip, self.mask_length))
        else:
            print(self.lang_dict[self.lang]['cidr'].format(self.ip, self.mask_length))
        print("{} - {}".format(self.network_range['start'], self.network_range['end']))
        if advanced is True:
            print(self.lang_dict[self.lang]['addr_avail_advanced'].format(occupied, self.addresses))
        else:
            print(self.lang_dict[self.lang]['addr_avail'].format(self.addresses))
        print('')
        print(self.lang_dict[self.lang]['subnets'].format(len(self.subnets), t))

        for i in range(len(self.subnets)):
            if advanced is True:
                print(self.lang_dict[self.lang]['sub_addr_advanced'].format(self.subnets[i]['start'],
                                                                            self.subnets[i]['end'],
                                                                            2 ** self.submasks_machine_bits[i] - 2,
                                                                            self.subnets_sizes[i]))
            else:
                print(self.lang_dict[self.lang]['sub_addr'].format(self.subnets[i]['start'], self.subnets[i]['end'],
                                                                   2 ** self.submasks_machine_bits[i] - 2))

        print('')
        print(self.lang_dict[self.lang]['net_usage'])
        print(graph)

    def _find_start_of_next_subnet_range(self, end):
        def _check(idx, content):
            if idx == 0 and content[idx] == '255':
                raise Exception(self.error_dict[self.lang]['network_limit'])

            if content[idx] == '255':
                content[idx] = '0'
                return _check(idx - 1, content)
            else:
                content[idx] = str(int(content[idx]) + 1)
                return '.'.join(content)

        data = end.split('.')
        return _check(3, data)

    def __determine_required_submasks_sizes(self):

        submasks = []

        for i in range(len(self.subnets_sizes)):
            power = 1
            while 2 ** power - 2 < self.subnets_sizes[i]:
                power = power + 1
            submasks.append(power)

        self.submasks_machine_bits = submasks

    def __init__(self, starting_ip, mask, subnets_sizes, english=None):
        super().__init__(starting_ip, mask, english=english)
        self.subnets_sizes = sorted(subnets_sizes, reverse=True)

        # first, let's check if the provided mask can handle all the addresses requested
        self.determine_network_range()
        self.__determine_required_submasks_sizes()

        total = 0

        for i in range(len(self.submasks_machine_bits)):
            total += 2**self.submasks_machine_bits[i]

        if self.addresses < total:
            power = 1
            while total > 2**power:
                power += 1
            raise Exception(self.error_dict[self.lang]['mask_too_small'].format(self.mask_length, 32-power))

    def build_subnets(self, returning=None, display=None, advanced=None):

        start_ip = self.network_range['start']

        for i in range(len(self.subnets_sizes)):
            machine_bits = self.submasks_machine_bits[i]
            result = self.determine_network_range(returning=True, start_ip=start_ip, machine_bits=machine_bits)
            self.subnets.append(result)
            start_ip = self._find_start_of_next_subnet_range(result['end'])

        if display is True:
            self.__display_subnets(advanced)
        elif display is False:
            print(self.subnets)

        if returning is True:
            return self.subnets
