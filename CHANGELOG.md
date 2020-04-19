# Changelog

## v1.2
- split class instancing and real init, and created functions accordingly
- hid all process functions, only inits and "final products" (and class variables) are now accessible from outside
- cleaned the tests files

## v1.1
- created an internal class to handle IPs and masks literals: FourBytesLiteral (FBL)
- Simplified call process. Only final parameters or functions to display final values can now be called.
- The files have been cleaned, some functions were taken out and some comments have been placed (not a lot, I know)
- New tests have been written, getting coverage up to 99%.