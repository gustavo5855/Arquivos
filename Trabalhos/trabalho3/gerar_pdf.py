import sys

import os, sys

print(sys.argv[1], sys.argv[2])

# for i in range(37)
# 	os.popen("mkdir p{}").format(i)

def teste():
	v=["Lista_ADS", "Lista_de"]
	os.popen("mkdir %s" % (sys.argv[1]))

	k = 0
	for i in range(int(sys.argv[2])):
		os.popen("cp %s.pdf %s/%s%s.pdf" % (v[k],sys.argv[1], i,v[k]))

		k += 1
		print(len(v))
		if k == len(v):
			print("dsfdsf")
			k = 0

teste()