all: cdirip nerorip

cdirip:
	make -C tools/cdirip-0.6.3-src

nerorip:
	make -C tools/nerorip-0.4-src


install: cdirip-i nerorip-i

cdirip-i:
	make -C tools/cdirip-0.6.3-src install

nerorip-i:
	make -C tools/nerorip-0.4-src install
