CC         := gcc
CFLAGS     := -I../include -O0 -g

all:       problem1 problem2

%:         %.c ../src/pluh.c
	$(CC) $^ -o $@ $(CFLAGS)

%.c:       %.pluh
	cd ../; python3 -m pluh day1/$< -o day1/$@

clean:
	rm -f problem1 problem1.c
	rm -f problem2 problem2.c

.PRECIOUS: %.c
