.PHONY: all
all: setup
	source venv/bin/activate && python3 -m grader

.PHONY: setup
setup:
	if [ ! -d venv ]; then \
		python3 -m venv venv; \
		source venv/bin/activate && \
		python3 -m pip install --upgrade pip && \
		python3 -m pip install -r requirements.txt; \
	fi
	mkdir -p temp

.PHONY: fmt
fmt:
	source venv/bin/activate && black .

.PHONY: clean
clean:
	rm -rf temp

.PHONY: test
test:
	pytest
