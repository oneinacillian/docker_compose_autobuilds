DATADIR="/apps/wax"
NODEOSBINDIR="/usr/opt/wax-leap/404wax01/bin"
$DATADIR/stop.sh
echo -e "Starting Nodeos \n";


$NODEOSBINDIR/nodeos --disable-replay-opts --genesis-json $DATADIR/genesis.json --data-dir $DATADIR --config-dir $DATADIR "$@" > $DATADIR/stdout.txt 2> $DATADIR/stderr.txt &  echo $! > $DATADIR/nodeos.pid
#$NODEOSBINDIR/nodeos --disable-replay-opts --data-dir $DATADIR --config-dir $DATADIR --snapshot /data/snapshots/snapshot-0de0cd8ba13c824ff17c4403e92492b1090ba393dbcf3144690caf16e205b85e.bin "$@" > $DATADIR/stdout.txt 2> $DATADIR/stderr.txt &  echo $! > $DATADIR/nodeos.pid
