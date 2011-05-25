all: cdirip nerorip

cdirip:
	make -C tools/cdirip-0.6.3-src

nerorip:
	make -C tools/nerorip_src


install: cdirip-i nerorip-i

cdirip-i:
	make -C tools/cdirip-0.6.3-src install

nerorip-i:
	make -C tools/nerorip_src install

clean: cdirip-c nerorip-c

cdirip-c:
	make -C tools/cdirip-0.6.3-src clean

nerorip-c:
	make -C tools/nerorip_src clean
