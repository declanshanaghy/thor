#!/usr/bin/env bash

FILE=pipeline-transform-event-to-metrics-thor
#FILE=pipeline-transform-event-to-metrics-example

${FILE}.dsl
scloud -v 2 -logtostderr streams compile-dsl -dsl-file ${FILE}.dsl > ${FILE}.json
