#!/bin/bash

EXTRACTION_FOLDER="extracted_layers"
mkdir "$EXTRACTION_FOLDER"

let ind=0

for i in {1..403}
    do if  ((i % 2))
        then tshark -r "Capture.pcapng" -Y usb -z follow,tcp,hex,$i > hexdata
        cat hexdata | tr --delete "\t" |  tail -n +2  | sed '1,5d' | head -n -1 | cut -d " " -f3-19 | tr --delete '\n'  | tr --delete ' ' | xxd -r -p> "${EXTRACTION_FOLDER}/layer${ind}.pkl"
        rm hexdata
        let ind++
    fi
done


python3 solve.py
