#!/bin/bash

Path="/tmp/"$(ls /tmp | grep pycore)
if [ ! -d "$Path" ]; then
  echo "Error: CORE topology directory not found. Is the simulation running?"
  exit 1
fi
echo "Path: $Path"

client_command=""
case "$1" in
  "S")
    client_command="python3 -m src.client.oClient videos/TheSimpsonsEvolution.mp4"
    ;;
  "B")
    client_command="python3 -m src.client.oClient videos/video_BrskEdu.mp4"
    ;;
  "M")
    client_command="python3 -m src.client.oClient videos/movie.Mjpeg"
    ;;
  *)
    echo "Usage: $0 {S|B|M}"
    exit 1
    ;;
esac

client_node="$2"
if [ -z "$client_node" ]; then
  echo "Error: No client node specified. Usage: $0 {S|B|M} <client_node>"
  exit 1
fi

run_command_in_xterm() {
  local node=$1
  local command=$2
  local title=$3

  echo "Opening terminal for $node and running command..."

  xterm -T "$title" -hold -e bash -i -c "
    vcmd -c '$Path/$node' -- su - core -c 'export DISPLAY=:0.0; cd /home/core/Desktop/ESR-Project/; $command; exec bash'" &
}

run_command_in_xterm "JHCLorden69" "python3 -m src.server.bootstrap.bootstrap configurations/topology.json" "Bootstrap"

sleep 1

for node in "n5" "n4" "n6" "n2"; do
  run_command_in_xterm $node "python3 -m src.oNode.oNode" "$node Node"
  sleep 0.5
done

sleep 1

run_command_in_xterm "JHCLorden69" "python3 -m src.server.Server" "Server"

sleep 1

run_command_in_xterm "$client_node" "$client_command" "Client ($client_node)"

echo "Commands executed in xterm terminals."
