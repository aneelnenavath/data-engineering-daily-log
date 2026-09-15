#!/bin/bash
# Home-grown replacement for Sqoop's saved-job feature, which turned out to
# have a real bug in this version: `sqoop job --create` silently drops
# --table/--connect/--check-column/--last-value when storing the job
# (confirmed via `sqoop job --show`, which never listed them at all).
# This does the same thing manually: remember the last imported
# customer_id in a local file, and pass it back in as --last-value.
set -e
export MSYS_NO_PATHCONV=1

STATE_FILE="./last_value.txt"
if [ ! -f "$STATE_FILE" ]; then
  echo "ERROR: $STATE_FILE not found."
  echo "Refusing to default to 0 -- that silently re-imports the WHOLE table"
  echo "as a duplicate batch (this exact bug happened once already)."
  echo "If this is genuinely the first run, create it explicitly yourself:"
  echo "    echo 0 > $STATE_FILE"
  exit 1
fi
LAST_VALUE=$(cat "$STATE_FILE")
echo "Running incremental import for customer_id > $LAST_VALUE ..."

docker exec namenode bash -c "
source /opt/sqoop-env.sh &&
export HADOOP_CLASSPATH=/opt/sqoop_gen:\$HADOOP_CLASSPATH &&
sqoop import --connect jdbc:mysql://ecommerce-mysql:3306/ecommerce --username root --password 'devpassword' --table customers --target-dir /data/sqoop/customers --outdir /opt/sqoop_gen --bindir /opt/sqoop_gen -m 1 --incremental append --check-column customer_id --last-value $LAST_VALUE
"

NEW_LAST=$(docker exec ecommerce-mysql mysql -uroot -p"devpassword" ecommerce -N -e "SELECT MAX(customer_id) FROM customers;" | tr -d '\r')
echo "$NEW_LAST" > "$STATE_FILE"
echo "Done. Bookmark updated: $LAST_VALUE -> $NEW_LAST"
