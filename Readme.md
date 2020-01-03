# SubNetwork constructor

[![Build Status](https://travis-ci.com/BioTheWolff/NetworkUtilities.svg?branch=master)](https://travis-ci.com/BioTheWolff/NetworkUtilities)

This project was at first made to help me determining 
network ranges and subnetworks. Then I thought it could 
be useful to expand it and share it.
Be aware, I adapted my program to follow 
[RFC 1918 standards](https://tools.ietf.org/html/rfc1918). 
As to say, any provided CIDR (IP/mask_length) must be `192.168.[0-255].[0-255]/>=16`, 
`172.[16-31].[0-255].[0-255]/>=12` or `10.[0-255].[0-255].[0-255]/>=8`

This project has two classes who allows differents things
described below.

This can also be ran in CLI (command line) or in a file.

Topics:\
I. Network Class\
II. SubnetworkBuilder Class\
III. Arguments and ways of calling

## Network Class

The network class allows to get the network range by providing an IP
and either the network mask or its length.

Assuming `instance` as our defined instance, 
you can then call either `instance.determine_network_range()`, which will give
the network range, or `instance.determine_type()`, which will give the network 
range followed by the type of the provided IP (network, computer or broadcast address)

Examples :
```
# giving mask and calling determine_network_range()
test1 = Network("192.168.1.0", "255.255.240.0", english=True)
test1.determine_network_range(display=True)

# giving mask length
test2 = Network("172.16.1.0", 13)
test2.determine_type(display=False)
```

## SubnetworkBuilder Class

The subnetwork builder class allows you to determine subnetworks
from an IP address, a mask, and the array containing the number of addresses 
you would like in each subnetwork. You can then call `build_subnets()` to get output.
SubnetworkBuilder is a subclass of Network, so you will also get the "smooth display"
of the network like displayed above.

Example:
We want 3 subnetworks, one of 1500 addresses, one of 5000 and one of 3860
```
test = SubnetworkBuilder("192.168.1.0", 18, [1500, 5000, 3860])
test.build_subnets(display=True)
```

This will output
```
Network:
CIDR : 192.168.1.0/18
192.168.0.0 - 192.168.63.255
16382 available addresses

3 sub-networks
192.168.0.0 - 192.168.31.255 (8190 addresses)
192.168.32.0 - 192.168.47.255 (4094 addresses)
192.168.48.0 - 192.168.55.255 (2046 addresses)

Network usage:
[██████████████████░░] 87 %
```

## Arguments and ways of calling

### Arguments
Arguments in these classes are important if you want it to execute properly.

When instanciating either `Network` or `SubnetworkBuilder`, you can pass the 
parameter `english=True` to get any "smooth display" in English. Else, 
you will get it in French by default.

When calling a function referenced below, you can pass `display=True` to get a display in your language
 ```
Network:
CIDR : 192.168.1.0/16
192.168.0.0 - 192.168.255.255
65534 available addresses

The address 192.168.1.0 is a computer address
```
 
 or `display=False` to get a raw output (always in english)
 ```
{'start': '192.168.0.0', 'end': '192.168.255.255', 'address_type': 'computer'}
```

You can also pass `returning=True` to tell the program to return raw output. 
By default, nothing will be returned and you will have to get the variable by yourself

### Different ways of executing
You can execute it from a file, like shown above, or in command line.

Patterns :\
(`{}` is the class you are calling, you can only call one. `<>` means required and `[]` means optional.
An optional argument will be display like \[-SHORT/--long_version])\
`py -m SubNetworkConstructor [-E/--english] {network} <ip> <mask> [-R/--raw]`\
`py -m SubNetworkConstructor [-E/--english {subnet} <ip> <mask> <subnets_sizes>+ ([-A/--advanced] OR [-R/--raw])`

This instruction is nearly the same as the `{network}` module one. The only difference is you don't need to 
pass any arguments, as the prober will automatically detect your current IP address and your mask, 
and use it as a base to provide a range\
`py -m SubnetworkConstructor [-E/--english] {prober}`

Examples :
```
# python
test = SubnetworkBuilder("192.168.1.0", 18, [1500, 5000, 3860])
test.build_subnets(display=True, advanced=True)

# command line
py -m SubNetworkConstructor subnet 192.168.1.0 18 1500 5000 3860 --advanced
```

```
# python
test1 = Network("192.168.1.0", "255.255.240.0", english=True)
test1.determine_network_range(display=False)

# command line
py -m SubNetworkConstructor -E network 192.168.1.0 255.255.240.0 -R
```