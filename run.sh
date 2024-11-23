#!/bin/bash

Path="/tmp/"$(ls /tmp | grep pycore)
if [ ! -d "$Path" ]; then
  echo "Error: CORE topology directory not found. Is the simulation running?"
  exit 1
fi
echo "Path: $Path"

run_command_in_xterm() {
  local node=$1
  local command=$2
  local title=$3

  echo "Opening terminal for $node and running command..."

  xterm -T "$title" -hold -e bash -c "
    vcmd -c '$Path/$node' -- su - core -c 'export DISPLAY=:0.0; cd /home/core/Desktop/ESR-Project/; $command; exec bash'" &
}

run_command_in_xterm "JHCLorden69" "python3 -m src.server.bootstrap.bootstrap configurations/topology.json" "Bootstrap"

sleep 2

for node in "n5" "n4" "n6" "n2"; do
  run_command_in_xterm $node "python3 -m src.oNode.oNode" "$node Node"
  sleep 1
done

sleep 2

run_command_in_xterm "JHCLorden69" "python3 -m src.server.Server" "Server"

echo "Commands executed in xterm terminals."
