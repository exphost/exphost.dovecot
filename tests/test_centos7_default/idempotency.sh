#!/bin/bash
tmp=$(mktemp)
echo "Temp to $tmp"
fabsible-play|tee $tmp
echo "Return to: $?"
echo "Temp to $tmp"
CHANGED=0
grep -s "changed=[1-9][0-9]*" $tmp && CHANGED=1
rm $tmp
exit $CHANGED
