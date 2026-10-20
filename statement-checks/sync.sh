#!/usr/bin/env bash
# Copy the project's own .lean sources (not the challenge copies) to the WSL build directory. Run as root.
SRC=/mnt/c/Users/Work/dev/siegel/statement-checks; DST=/home/checker/statement-checks
cp $SRC/StatementChecks.lean $DST/; cp $SRC/StatementChecks/*.lean $DST/StatementChecks/; chown -R checker:checker $DST/StatementChecks $DST/StatementChecks.lean
