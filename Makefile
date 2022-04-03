WITH_VENV=source venv/bin/activate && 


.PHONY: all
all: setup
	$(WITH_VENV) python3 -m grader

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
	$(WITH_VENV) black .

.PHONY: clean
clean:
	rm -rf temp

.PHONY: test
test:
	$(WITH_VENV) pytest
