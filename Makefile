.PHONY: all
all: setup
	python3 -m grader

.PHONY: setup
setup:
	mkdir -p temp

.PHONY: fmt
fmt:
	black .

.PHONY: clean
clean:
	rm -rf temp

.PHONY: test
test:
	pytest
