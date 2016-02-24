set -xe
if [ ! -e /app/.cache/mysql/db.done ]; then
    sleep 30
    echo "Initializing DB..."
    # No DB import yet, but we still stamp for the initializing
    # of MySQL's DB to be done, so we don't always have to sleep
    touch /app/.cache/mysql/db.done
    echo "Done"
fi

# run the command passed from docker
$@