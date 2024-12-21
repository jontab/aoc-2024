CC     := gcc
CFLAGS := -I../include -O0 -g

problem1: problem1.c ../src/pluh.c
	$(CC) $^ -o $@ $(CFLAGS)

problem1.c: problem1.pluh
	cd ../; python3 -m pluh problem1/$< -o problem1/$@

clean:
	rm -f problem1.c
	rm -f problem1
