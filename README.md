<!-- vim: set ft=markdown : -->


# Sudoku solver

## Summary

The script `sudoku-solver.py` solves Sudoku puzzles.

## Prerequisites

* [mise](https://mise.jdx.dev/)

``` shell
mise run install
mise exec -- pixi shell
```

## Usage

``` shell
./sudoku-solver.py --help
```

``` text
usage: sudoku-solver.py [-h] [--output-dir OUTPUT_DIR] [--sep SEP] [--solution-limit SOLUTION_LIMIT] INPUT_FILE

positional arguments:
  INPUT_FILE            Sudoku puzzle will be read from this file

options:
  -h, --help            show this help message and exit
  --output-dir OUTPUT_DIR
                        Sudoku puzzle solutions will be written to this directory (default: /Users/manselmi/repos/sudoku-solver/output)
  --sep SEP             separator delimiting values within a row (input and output) (default: ,)
  --solution-limit SOLUTION_LIMIT
                        limit the number of solutions to this value (0 for no limit) (default: 1)
```

## Examples

### Feasible

``` shell
cat -- feasible.csv
```

``` text
5,3,,,7,,,,
6,,,1,9,5,,,
,9,8,,,,,6,
8,,,,6,,,,3
4,,,8,,3,,,1
7,,,,2,,,,6
,6,,,,,2,8,
,,,4,1,9,,,5
,,,,8,,,7,9
```

``` shell
./sudoku-solver.py -- feasible.csv
```

``` text
Status:          OPTIMAL
Solutions found: 1
Wall time:       0.001425
Branches:        0
Conflicts:       0
```

``` shell
column -t -s , -- output/0
```

``` text
5  3  4  6  7  8  9  1  2
6  7  2  1  9  5  3  4  8
1  9  8  3  4  2  5  6  7
8  5  9  7  6  1  4  2  3
4  2  6  8  5  3  7  9  1
7  1  3  9  2  4  8  5  6
9  6  1  5  3  7  2  8  4
2  8  7  4  1  9  6  3  5
3  4  5  2  8  6  1  7  9
```

### Infeasible

``` shell
cat -- infeasible.csv
```

``` text
8,3,,,7,,,,
6,,,1,9,5,,,
,9,8,,,,,6,
8,,,,6,,,,3
4,,,8,,3,,,1
7,,,,2,,,,6
,6,,,,,2,8,
,,,4,1,9,,,5
,,,,8,,,7,9
```

``` shell
./sudoku-solver.py -- infeasible.csv
```

``` text
Status:          INFEASIBLE
Solutions found: 0
Wall time:       0.000146
Branches:        0
Conflicts:       0
```

### Blank 4x4

``` shell
cat -- blank-4x4.csv
```

``` text
,,,
,,,
,,,
,,,
```

``` shell
./sudoku-solver.py --solution-limit 0 -- blank-4x4.csv
```

``` text
Status:          OPTIMAL
Solutions found: 288
Wall time:       0.034108
Branches:        3571
Conflicts:       35
```

``` shell
find -- output -maxdepth 1 -type f -name '*[0-9]*' -print0 | grep -z -c -- '.*'
# 288
```
