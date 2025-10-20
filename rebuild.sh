set -E
set -o pipefail
docker build -t manage-django:$1-test .
sed -i "s/APP_VERSION=.*/APP_VERSION=$1-test/" ../.env
