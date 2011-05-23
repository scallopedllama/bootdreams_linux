all: cdirip nerorip

cdirip:
	make -C cdirip-0.6.3-src

nerorip:
	make -C nerorip-0.4-src


install: cdirip-i nerorip-i

cdirip-i:
	make -C cdirip-0.6.3-src install

nerorip-i:
	make -C nerorip-0.4-src install
