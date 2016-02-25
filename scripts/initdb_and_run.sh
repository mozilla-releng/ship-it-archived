set -xe
if [ ! -e /app/.cache/mysql/db.done ]; then
    sleep 30
    echo "Initializing DB..."
    PYTHONPATH=$(PYTHONPATH):/app/vendor/lib/python python /app/migrate_repo/manage.py version_control mysql://shipit:shipitpw@shipitdb/shipit migrate_repo
    PYTHONPATH=$(PYTHONPATH):/app/vendor/lib/python python /app/migrate_repo/manage.py upgrade mysql://shipit:shipitpw@shipitdb/shipit migrate_repo
    touch /app/.cache/mysql/db.done
    echo "Done"
else:
    sleep 10
    echo "Upgrading DB..."
    PYTHONPATH=$(PYTHONPATH):/app/vendor/lib/python python /app/migrate_repo/manage.py upgrade mysql://shipit:shipitpw@shipitdb/shipit migrate_repo
fi

# run the command passed from docker
$@