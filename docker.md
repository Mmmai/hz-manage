PyJWT==2.8.0

mysqlclient==2.1.1

uwsgi==2.0.25.1



apk add mysql-dev nginx linux-headers gcc g++ mysql-client





```
uwsgi --chdir=/opt/teligen-ui \
    --module=vuedjango.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=vuedjango.settings \
    --master --pidfile=/tmp/project-master.pid \
    --socket=127.0.0.1:49152 
```