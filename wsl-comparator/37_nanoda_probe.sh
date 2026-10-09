#!/bin/bash
grep -m3 '"rectangle"\|"interpolation"' /home/checker/l3k/export.ndjson | cut -c1-200; head -3 /home/checker/l3k/export.ndjson | cut -c1-200
