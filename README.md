# aoc-2024
Advent of Code, 2024, anyone?

## What is this?

Pluh is a simple functional language I created, inspired by ML. I developed a Python compiler/transpiler for Pluh that translates Pluh source code into C. This C code can then be compiled with the Pluh standard library to produce a functional executable. I embarked on this project due to my interest in the fundamentals of compiling functional languages, and Advent of Code provided the perfect opportunity to apply it. For examples of the syntax, please refer to the `data/examples` directory. The grammar can be found in `pluh/syntax.py`.

## Progress
- [x] Add parsing for custom functional language.
- [x] Add alpha-renaming.
- [x] Add Hindley-Milner type inference, opaque recursive types, let-polymorphism.
- [x] Add administrative normal form (ANF) conversion.
- [x] Add closure creation.
- [x] Add compilation.
  - Added standard library functions.
  - Delegate constructing variant types to `pluh_rt_make_variant` runtime function.
- [x] Solve day1.

## Stretch-goals

- [ ] Garbage collection via reachability analysis.
- [ ] "Generic" variant types (i.e., `'a list`).
- [ ] Tuple-literals beyond length 2.
- [ ] Curried functions (`fun x -> fun y ->` becomes `fun x y ->`).
- [ ] "define" or "def" statements.
