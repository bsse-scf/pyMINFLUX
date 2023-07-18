#!/bin/bash

if [ "$#" != "1" ]; then
    echo "Usage: ./build_docs.sh /path/to/docs/folder"
    exit
fi

if [ -d "$1" ]
then
    dir_name=$(basename "$1")
    parent_path=$(dirname "$1")
    current_date=$(date +%Y%m%d_%H%M%S)
    mv "$1" "$parent_path/${dir_name}_$current_date"
    echo "$1 renamed to $parent_path/${dir_name}_$current_date"
fi

# Build documentation
pdoc3 pyminflux --html --force --output-dir $1 --template-dir templates

# Wrong references are added to the code -- unclear why
find . -name *.html -exec sed -i 's/pyminflux.reader._reader.MinFluxReader/pyminflux.reader.MinFluxReader/g' {} \;
find . -name *.html -exec sed -i 's/pyminflux.processor._processor.MinFluxProcessor/pyminflux.processor.MinFluxProcessor/g' {} \;

