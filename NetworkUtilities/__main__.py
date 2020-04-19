import argparse
from NetworkUtilities.core.network_basic import NetworkBasicDisplayer
from NetworkUtilities.core.subnetworkbuilder import SubnetworkBuilder


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser", help="Sub-modules")

    # network parser
    network_parser = subparsers.add_parser("network", help="Module to determine a network range and type of an IP",
                                           aliases="net")
    network_parser.add_argument("ip", help="One IP in the network")
    network_parser.add_argument("mask", help="The network mask. You can provide either the mask or its length")

    network_parser.add_argument("-R", "--raw", help="Returns the array of utils instad of displaying a smooth recap",
                                action="store_false")

    # subnetbuilder parser
    subnetbuilder = subparsers.add_parser("subnet", help="Module to determine subnetworks ranges")
    subnetbuilder.add_argument("ip", help="One IP in the network")
    subnetbuilder.add_argument("mask", help="The network mask. You can provide either the mask or its length")
    subnetbuilder.add_argument("subnets_sizes", help="Subnetworks sizes. Give the number of addresses you want to see "
                                                     "in each subnetwork", nargs='+', type=int)

    group = subnetbuilder.add_mutually_exclusive_group()
    group.add_argument("-R", "--raw", help="Returns the array of utils instad of displaying a smooth recap",
                       action="store_true")
    group.add_argument("-A", "--advanced", help="Displays more informations about how the utils are composed, and "
                                                "also some advices on the masks that can be used", action="store_true")

    args = parser.parse_args()

    if args.subparser == "network":
        net = NetworkBasicDisplayer().init_from_couple(args.ip, args.mask)
        net.display_type(display=args.raw)

    elif args.subparser == "subnet":
        net = SubnetworkBuilder(args.subnets_sizes).init_from_couple(args.ip, args.mask)
        if not args.raw:
            net.print_subnetworks_fancy(advanced=args.advanced)
        else:
            net.print_subnetworks()


if __name__ == '__main__':
    main()
