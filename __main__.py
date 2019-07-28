import argparse
from .Network import *


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser", help="Sub-modules")

    # network parser
    network_parser = subparsers.add_parser("network", help="Module to determine a network range or the type of an IP")
    network_parser.add_argument("ip", help="One IP in the network")
    network_parser.add_argument("mask", help="The network mask. You can provide either the mask or its length")

    network_parser.add_argument("-T", "--type", help="Display the type of the provided IP", action="store_true")
    network_parser.add_argument("-R", "--raw", help="Returns the array of subnets instad of displaying a smooth recap",
                                action="store_false")

    # subnetbuilder parser
    subnetbuilder = subparsers.add_parser("subnet", help="Module to determine subnetworks ranges")
    subnetbuilder.add_argument("ip", help="One IP in the network")
    subnetbuilder.add_argument("mask", help="The network mask. You can provide either the mask or its length")
    subnetbuilder.add_argument("subnets_sizes", help="Subnetworks sizes. Give the number of addresses you want to see "
                                                     "in each subnetwork", nargs='+', type=int)

    group = subnetbuilder.add_mutually_exclusive_group()
    group.add_argument("-R", "--raw", help="Returns the array of subnets instad of displaying a smooth recap",
                       action="store_false")
    group.add_argument("-A", "--advanced", help="Displays more informations about how the subnets are composed, and "
                                                "also some advices on the masks that can be used", action="store_true")

    # lang
    lang = parser.add_mutually_exclusive_group()
    lang.add_argument("-E", "--english", help="Sets the display language to English",
                      action="store_true")
    lang.add_argument("-F", "--french", help="Affiche le récapitulatif en français", action="store_true")

    args = parser.parse_args()

    if args.english is True:
        lang = True
    else:
        lang = False

    if args.subparser == "network":
        if args.type is True:
            net = Network(args.ip, args.mask, english=lang)
            net.determine_type(display=args.raw)
        else:
            net = Network(args.ip, args.mask, english=lang)
            net.determine_network_range(display=args.raw)

    elif args.subparser == "subnet":
        net = SubnetworkBuilder(args.ip, args.mask, args.subnets_sizes, english=lang)
        net.build_subnets(display=args.raw, advanced=args.advanced)


if __name__ == '__main__':
    main()
