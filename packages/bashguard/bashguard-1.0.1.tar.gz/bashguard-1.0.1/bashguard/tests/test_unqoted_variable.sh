#!/bin/bash

PATH=/usr/bin

[ -n "$1" ] || exit 1
[ "$1" = "flag" ] && exit 2
[ $1 = "flag" ] && cat /flag

echo "Goodbye!"