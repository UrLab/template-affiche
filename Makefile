DESCRIPTIONS = $(wildcard */*.yaml)
AFFICHES = $(subst .yaml,.png,${DESCRIPTIONS})

.PHONY: clean all

all: ${AFFICHES}
clean:
	rm -f ${AFFICHES}

%.png: %.yaml
	python affiche.py $<
