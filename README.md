DY XS estimation
------------

Within some visiable mass region, e.g (25, 125)

Data_OST - xDY_OST - MC_None_DY_OST - QCD_OST = 0 <br />
1) x = DY_XS/6025.2 <br />
2) QCD_OST = 1.06*(Data_SST - x*DY_SST - MC_None_DY_SST) <br />

=> x = (Data_OST - MC_None_DY_OST - 1.06*(Data_SST - MC_None_DY_SST))/(DY_OST - 1.06*DY_SST) <br />
=> DY_XS = x*6025.2

Similarly, one can independently calculate DY_XS in tau iso relaxed region.


Running script
------------
Edit lines 184-195 in xs_calculator.py
```bash
python xs_calculator.py
```

The script will output the DY xs in tight and relaxed regions.
It'll also make 2 stacked plots in those regions.