SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)

echo $SCRIPT_DIR/contrib/bot.service


MAINDB="superapp"


mysql -uroot <<MYSQL_SCRIPT
CREATE DATABASE $MAINDB;
MYSQL_SCRIPT

echo "MySQL db created."
echo "DB name:   $MAINDB"

apt-get install libmysqlclient-dev
apt install mysql-server mysql-client


api_service_path="/etc/systemd/system/api.service"
bot_service_path="/etc/systemd/system/bot.service"


pip install -r requirements.txt

yes | cp -if $SCRIPT_DIR/contrib/api.service $api_service_path
yes | cp -if $SCRIPT_DIR/contrib/bot.service $bot_service_path

systemctl daemon-reload

systemctl restart api
systemctl restart bot