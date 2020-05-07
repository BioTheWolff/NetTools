# Changelog

## v2.0
- Renamed NetworkBasic class to IPv4Network and secured class variables.
The vars are now gettable by properties of the same name
- Simplified the insides of the IPv4Network class, using Utils as a support for all static things
not required in the class
- The SubnetworkBuilder class became IPv4NetworkCompound. Both its objective and the way it works have been
changed

## v1.2
- Split class instancing and real init, and created functions accordingly
- Hid all process functions, only inits and "final products" (and class variables) are now accessible from outside
- Cleaned the tests files

## v1.1
- Created an internal class to handle IPs and masks literals: FourBytesLiteral (FBL)
- Simplified call process. Only final parameters or functions to display final values can now be called.
- The files have been cleaned, some functions were taken out and some comments have been placed (not a lot, I know)
- New tests have been written, getting coverage up to 99%.