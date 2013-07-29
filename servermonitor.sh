until ./manage.py runserver --insecure 0.0.0.0:4200; do
    echo "Server 'myserver' crashed with exit code $?.  Respawning.." >&2
    sleep 1
done
