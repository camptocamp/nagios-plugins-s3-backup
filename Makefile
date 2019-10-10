all: prune run

run:
	. ./run.sh

prune:
	docker container prune -f