for n in $(cat re_rangos.txt)
do
for i in {1..255}
do
ip=$(echo $n | sed 's/\.[^.]*$//')
ip=$ip.$i
ping $ip -c4 | grep -i ttl | tee -a $n.txt
done
done
