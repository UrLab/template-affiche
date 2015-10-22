DESCRIPTIONS = $(wildcard */*.yaml)
AFFICHES = $(subst .yaml,.png,${DESCRIPTIONS})
BANNERS = $(subst .png,-fb.png,${AFFICHES})

.PHONY: clean all

all: ${AFFICHES}
clean:
	rm -f ${AFFICHES} ${BANNERS}

%.png: %.yaml
	python affiche.py $<
