# ukmon_meteortools

Python tools and utilities to work with meteor data from the UK Meteor Network

To get more information about the submodules and functions use Python's built-in help capability, for example
as shown here. 

## Installation on a Raspberry Pi
To install these tools on aa Raspberry Pi you must first install GEOS and PROJ  
``` bash
sudo apt-get install -y libgeos-dev proj-bin
```
You may also need to install these on some other Linux platforms. If you see an error that geos_c.h cannot be found
or that PROJ_LIB is not defined, install the above packages. 


## Usage

``` python
from ukmon_meteortools import utils
help(utils)
help(utils.sendAnEmail)
```

```python
>>>from ukmon_meteortools.utils import date2JD, jd2LST, getActiveShowers, getShowerDets
>>> date2JD(2023,4,11,12,45,9)
2460046.0313541666
>>>import numpy as np
>>> jd2LST(2460046.0313541666, lon=np.radians(-1.31))
(30.741774823384617, 30.76463863658577)
>>> import datetime
>>> getActiveShowers(datetime.datetime.now())
LYR
ETA
>>> from ukmon_meteortools.utils import getShowerDets
>>> getShowerDets('LYR')
(6, 'April Lyrids', 32.0, '04-22')
>>>
```