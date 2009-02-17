#!/bin/bash

for i in `cat index`

do curl $i -O

done
