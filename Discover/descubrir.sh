#!/bin/bash

for n in $(cat rangos.txt)
do
fichero="${n%%/*}"
nmap -sP $n | grep "Nmap scan report for" | cut -d " " -f 5,6 | tee -a $fichero.txt
done
