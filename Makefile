.PHONY: all
all: HCA
lib:
	$(MAKE) -C $@
HCA: lib
	$(MAKE) -C $@
.PHONY: all lib HCA
