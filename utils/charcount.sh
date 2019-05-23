#wc -c < $1
cat $1 && echo "," && wc -c < $1 && echo "$f"