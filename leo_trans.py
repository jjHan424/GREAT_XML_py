#!/usr/bin/python3

import sys
import os

if len(sys.argv) < 4:
    print('Wrong input!!!!')
    print('Usage: ' + sys.argv[0] + ' LeoSiteName  mode  upplow')
    print('Default mode:   1  represents LEO short name to long name')
    print('                2  represents LEO long name to short name')
    print('Default upplow: up represents output with upper format')
    print('                lo represents output with lower format')
    sys.exit()
leo_b = sys.argv[1]
mode = eval(sys.argv[2])
uplo = sys.argv[3]
LEO_SHORT = ['swa' + x for x in 'abc']
LEO_LONG = ['swarm-' + x for x in 'abc']
LEO_SHORT.extend(['gra' + x for x in 'abcd'])
LEO_LONG.extend(['grace-' + x for x in 'abcd'])
LEO_SHORT.extend(['jas' + x for x in '23'])
LEO_LONG.extend(['jason-' + x for x in '23'] )
LEO_SHORT.extend(['fy3' + x for x in 'cd'])
LEO_LONG.extend(['fy-3' + x for x in 'cd'])
LEO_SHORT.extend(['met' + x for x in 'abc'])
LEO_LONG.extend(['metop-' + x for x in 'abc'])
LEO_SHORT.extend(['se' + x for x in ['1a', '1b', '2a', '2b', '3a', '3b']])
LEO_LONG.extend(['sentinel-' + x for x in ['1a', '1b', '2a', '2b', '3a', '3b']])
LEO_SHORT.append('tesx')
LEO_SHORT.append('tadx')
LEO_LONG.append('terrasar-x')
LEO_LONG.append('tandem-x')
LEOS = dict(zip(LEO_SHORT, LEO_LONG))
LEOL = dict(zip(LEO_LONG, LEO_SHORT))
if mode == 1:
    leo = LEOS.get(leo_b, 'WRONG!!!')
    if uplo == 'up':
        print(leo.upper())
    else:
        print(leo.lower())
elif mode == 2:
    leo = LEOL.get(leo_b, 'WRONG!!!')
    if uplo == 'up':
        print(leo.upper())
    else:
        print(leo.lower())

