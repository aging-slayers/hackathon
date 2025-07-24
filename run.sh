#!/bin bash
mkdir -p access
mkdir -d data
echo Don\'t forget to put Google Sheets credentials to /access folder!
wget -nc https://nb3.me/public/aging-slayers-data.tar.gz
[ "$(ls -A data)" ] && echo "Data seems to be downloaded, skipping" || tar -xf aging-slayers-data.tar.gz
docker rm -f aging_slay_streamlit
docker image prune -af
docker compose up -d
docker exec --user root -it aging_slay_streamlit chown -R appuser access
docker logs aging_slay_streamlit  -f
