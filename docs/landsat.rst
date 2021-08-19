Scene classification and cloudmasking is included in landsat datafiles as .TIF-files
that have QA_PIXEL in their name.
Each pixel has a 16-bit integer value, and each bit of this value is a flag for a certain condition
or confidence level of a certain condition. 
Meaning of each bit in Landsat Collection 2 data can be viewed here:
https://prd-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/atoms/files/LSDS-1328_Landsat8-9-OLI-TIRS-C2-L2-DFCB-v6.pdf#PAGE=14

config_ls8.yml has value bitmask set to 1, which tells mask.py to interpret the tobemaskedlist
as bit indices and not values. For example if bit 3 is set the pixel could have value 8, or other
value depending on the other bits, so if we want to mask out a pixel when bit 3 is set, we cannot 
check for any individual value (like 3 or even 8). This is why mask.py then uses a seperate function
to create the cloudmask. The method checkbits takes an individual number (data) and compares it to the tobemaskedlist.
Now tobemaskedlist is interpreted as bit indices and the method loops through all the indices in said list.
Bitshifting 1 to the left by the amount of the bit index (1 << bit) creates a binary number where the bit
in the desired index is set as 1 and rest are 0, e.g., 1 << 3 = 0b1000. Now comparing this with bitwise
and (&) with the pixel value, we get zero if the pixel value doesn't have a one in the same place as
1 << bit (such as 0b1000) and nonzero if there is. Now converting this into boolean, we get True if
the pixel value has bit on the chosen index set as 1 and False if not. Testing this for each bit index we want
to mask, and setting the pixel's "mask value" as 1 if any of them is True and 0 if all of them are False.
In createbitmask we have vectorized checkbits so it maps through numpy arrays, thus creating a mask array
with same 2D shape as the array received from the Quality Assessment .TIF.