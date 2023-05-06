build_packages: 
	make build -C packages
	cp packages/dist/pyyaap-1.0.0.tar.gz engines/crawler/pyyaap.tar.gz
	cp packages/dist/pyyaap-1.0.0.tar.gz engines/search/pyyaap.tar.gz
	
clean_packages:
	make clean -C packages
	rm engines/crawler/pyyaap.tar.gz
	rm engines/search/pyyaap.tar.gz
