mkdir -p access
echo Don\'t forget to put Google Sheets credentials to /access folder!
wget https://nb3.me/public/aging-slayers-data.tar.gz
tar -xf aging-slayers-data.tar.gz
docker rm -f aging_slay_streamlit
docker image prune -a
docker compose up -d
docker exec --user root -it aging_slay_streamlit chown -R appuser access
docker logs aging_slay_streamlit  -f
