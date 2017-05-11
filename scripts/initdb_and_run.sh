set -xe

/app/scripts/generate_version_file.sh

if [ ! -e /app/.cache/mysql/db.done ]; then
    sleep 30
    echo "Initializing DB..."
    PYTHONPATH=${PYTHONPATH}:/app/vendor/lib/python python /app/migrate_repo/manage.py version_control mysql://shipit:shipitpw@shipitdb/shipit migrate_repo
    # the sample data is for schema version 19
    PYTHONPATH=${PYTHONPATH}:/app/vendor/lib/python python /app/migrate_repo/manage.py upgrade --version=19 mysql://shipit:shipitpw@shipitdb/shipit migrate_repo
    bunzip2 -c /app/scripts/sample-data.sql.bz2 | mysql -h shipitdb -u shipit --password=shipitpw shipit
    # update to the latest schema
    PYTHONPATH=${PYTHONPATH}:/app/vendor/lib/python python /app/migrate_repo/manage.py upgrade mysql://shipit:shipitpw@shipitdb/shipit migrate_repo
    touch /app/.cache/mysql/db.done
    echo "Done"
else
    sleep 10
    echo "Upgrading DB...";
    PYTHONPATH=${PYTHONPATH}:/app/vendor/lib/python python /app/migrate_repo/manage.py upgrade mysql://shipit:shipitpw@shipitdb/shipit migrate_repo
fi

# run the command passed from docker
$@
