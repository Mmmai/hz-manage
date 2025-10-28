set -E
set -o pipefail

if [[ $1 == "base" || $1 == "" ]];
then
  echo Received invalid image version
  exit
fi

# Update source code
echo '******************************* Building manage-django with new tag *******************************'
docker build -t manage-django:$1 .
echo

# Stop apps
echo '****************************************** Stopping apps ******************************************'
docker-compose -f ../docker-compose.yaml down
echo

# Set environment params
echo '********************************** Replacing APP_VERSION in .env **********************************'
sed -i "s/APP_VERSION=.*/APP_VERSION=$1/" ../.env
grep '^APP_VERSION' ../.env
echo

# Restart
echo '***************************************** Restarting apps *****************************************'
docker-compose -f ../docker-compose.yaml up -d
echo
