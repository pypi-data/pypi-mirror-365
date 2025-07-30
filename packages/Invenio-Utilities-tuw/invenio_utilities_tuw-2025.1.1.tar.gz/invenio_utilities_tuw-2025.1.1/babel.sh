#!/bin/bash

if [[ $# -lt 1 ]]; then
    echo >&2 "error: expected at least one argument"
fi

case "${1}" in
    init)
        pybabel init \
            --input-file "invenio_utilities_tuw/translations/messages.pot" \
            --output-dir "invenio_utilities_tuw/translations/"
        ;;
    compile)
        pybabel compile \
            --directory "invenio_utilities_tuw/translations/"
        ;;
    extract)
        pybabel extract \
            --copyright-holder "TU Wien" \
            --msgid-bugs-address "tudata@tuwien.ac.at" \
            --mapping-file "babel.ini" \
            --output-file "invenio_utilities_tuw/translations/messages.pot" \
            --add-comments "NOTE"
        ;;
    update)
        pybabel update \
            --input-file "invenio_utilities_tuw/translations/messages.pot" \
            --output-dir "invenio_utilities_tuw/translations/"
        ;;
    *)
        echo >&2 "unknown command: ${1}"
        exit 1
        ;;
esac
