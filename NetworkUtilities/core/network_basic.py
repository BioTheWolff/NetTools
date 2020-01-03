from NetworkUtilities.core.errors import *


class NetworkBasic:
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

            'utils': "{} sous-réseau{}",
            'sub_addr': "{} - {} ({} adresses)",
            'sub_addr_advanced': "{} - {} ({} adresses disponibles, {} demandées)",
            'net_usage': "Occupation du réseau :"
        },
        'en': {
            'network': "NetworkBasic:",
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

            'utils': "{} sub-network{}",
            'sub_addr': "{} - {} ({} addresses)",
            'sub_addr_advanced': "{} - {} ({} available addresses, {} requested)",
            'net_usage': "NetworkBasic usage:"
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
    def __dec_to_bin(x):
        return int(bin(x)[:2])

    @staticmethod
    def _switch_length(mask_length):
        lengths = [0, 128, 192, 224, 240, 248, 252, 254, 255]
        return lengths[mask_length]

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
            raise MaskLengthOffBoundsException(self.lang, mask_length)
        return result

    def _display(self, is_prober=False):
        print(self.lang_dict[self.lang]['network'])
        print(self.lang_dict[self.lang]['cidr'].format(self.ip, self.mask_length))
        if is_prober:
            print("Estimated range from probing : {} - {}".format(self.network_range['start'],
                                                                  self.network_range['end']))
        else:
            print("{} - {}".format(self.network_range['start'], self.network_range['end']))
        print(self.lang_dict[self.lang]['addr_avail'].format(self.addresses))

        if self.address_type is not None:
            print('')

            if self.address_type in [0, 1, 2]:
                types = ['net', 'mac', 'bct']
                machine_type = self.lang_dict[self.lang]['addr_types'][types[self.address_type]]
            else:
                raise Exception("Given address type other than expected address types")

            print(self.lang_dict[self.lang]['addr_type'].format(self.ip, machine_type))

    def _verify_provided_types(self):
        temp = self.ip.split('.')
        if len(temp) != 4:
            raise IPBytesLengthException(self.lang, len(temp))
        for i in range(len(temp)):
            if not (0 <= int(temp[i]) <= 255):
                raise IPByteNumberOffLimitsException(self.lang, temp[i], i)

        try:
            temp = self.mask.split('.')
            if len(temp) == 1:
                raise AttributeError()
            if len(temp) != 4:
                raise MaskBytesLengthException(self.lang, len(temp))
            for i in range(len(temp)):
                if not (0 <= int(temp[i]) <= 255):
                    raise MaskByteNumberOffLimitsException(self.lang, temp[i], i)
        except (AttributeError, ValueError):
            if 0 <= int(self.mask) <= 32:
                return
            else:
                raise MaskLengthOffBoundsException(self.lang, self.mask)

    def _verify_rfc_rules(self):
        # For more information on RFC 1918 standards, check https://tools.ietf.org/html/rfc1918
        def _check(content):
            ip_test = False
            for I in range(3):
                if (int(content[0]) == self.rfc_allowed_ranges[I][0]) and \
                        (self.rfc_allowed_ranges[I][1][0] <= int(content[1]) <= self.rfc_allowed_ranges[I][1][1]):
                    ip_test = True
                    self.rfc_current_range = I

            if ip_test is False:
                raise RFCRulesIPWrongRangeException(self.lang, ip[0], ip[1])

        ip = self.ip.split('.')
        mask = self.mask_length

        # We check that ip respects RFC standards
        _check(ip)

        # We then check that provided mask corresponds to RFC standards
        for i in range(3):
            allowed = self.rfc_allowed_ranges[i][0]
            allowed_mask = self.rfc_masks[i]
            if (int(ip[0]) == allowed) and (mask < allowed_mask):
                raise RFCRulesWrongCoupleException(self.lang, ip[0], ip[1], allowed_mask, mask)

    def calculate_mask(self):
        try:
            temp = self.mask.split('.')
            if len(temp) == 1:
                raise AttributeError()
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
                    raise IncorrectMaskException(self.lang)
            self.mask_length = length
        except AttributeError:
            self.mask_length = int(self.mask)
            self.mask = self.mask_length_to_readable(self.mask_length)
        finally:
            self.addresses = 2 ** (32 - self.mask_length) - 2

    def __init__(self, ip, mask=None, lang=None):
        if mask is None:
            try:
                ip, mask = ip.split('/')
                self.ip = ip
                self.mask = mask
            except ValueError:
                raise MaskNotProvided(ip)
        else:
            self.ip = ip
            self.mask = mask
        self.lang = lang if lang else 'fr'

        self._verify_provided_types()
        self.calculate_mask()
        self._verify_rfc_rules()

    def determine_network_range(self, start_ip=None, machine_bits=None, returning=True, addresses_list=None):
        start = self.ip if start_ip is None else start_ip
        machine_bits = 32 - self.mask_length if machine_bits is None else machine_bits

        # gives the range of the network depending on the mask
        def _check(idx, content):
            if idx == 0 and content[idx] == 255:
                raise NetworkLimitException(self.lang)

            if content[idx] == 255:
                content[idx] = 0
                return _check(idx - 1, content)
            else:
                content[idx] = content[idx] + 1
                return content

        liste = []

        if (start_ip is None and returning is None) and (self.mask_length == self.rfc_masks[self.rfc_current_range]) \
                and addresses_list is None:

            if self.rfc_current_range == 0:
                result = {'start': "192.168.0.0", 'end': "192.168.255.255"}
            elif self.rfc_current_range == 1:
                result = {'start': "172.16.0.0", 'end': "172.31.255.255"}
            elif self.rfc_current_range == 2:
                result = {'start': "10.0.0.0", 'end': "10.255.255.255"}
            else:
                raise Exception("Something wrong happened when nothing should. Try contacting the author to solve this")

        else:
            if addresses_list:
                liste.append(start)
            ip = start.split('.')
            addresses = 2 ** machine_bits
            for i in range(len(ip)):
                ip[i] = int(ip[i])

            # we take 1 from addresses because the starting ip is already one
            for i in range(addresses - 1):
                ip = _check(3, ip)
                if addresses_list:
                    liste.append(".".join([str(i) for i in ip]))

            for i in range(len(ip)):
                ip[i] = str(ip[i])

            result = {'start': start, 'end': '.'.join(ip)}

        self.network_range = result
        if addresses_list:
            del liste[-1]

        if returning and not addresses_list:
            return result
        elif returning and addresses_list:
            return result, liste
        elif addresses_list and not returning:
            return liste

    def determine_type(self, machine_ip, display=None):
        def _check_end(machine_ip_, idx=3):
            if self.network_range['end'].split('.')[idx] >= machine_ip_.split('.')[idx]:
                if idx == 0:
                    return None
                else:
                    return _check_end(machine_ip_, idx - 1)
            else:
                return True

        def _check_start(machine_ip_, idx=3):
            if self.network_range['start'].split('.')[idx] <= machine_ip_.split('.')[idx]:
                if idx == 0:
                    return None
                else:
                    return _check_start(machine_ip_, idx - 1)
            else:
                return True

        if self.network_range == {}:
            self.determine_network_range()

        if _check_end(machine_ip) or _check_start(machine_ip):
            raise IPOffNetworkRangeException(self.lang)

        if self.network_range['start'] == machine_ip:
            self.address_type = 0
        elif self.network_range['end'] == machine_ip:
            self.address_type = 2
        else:
            self.address_type = 1

        if display is True:
            self._display()
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

        return self.address_type


class NetworkBasicDisplayer(NetworkBasic):

    def display_range(self, display=False):
        self.determine_network_range()

        if display is True:
            self._display()
        else:
            print(self.network_range)
