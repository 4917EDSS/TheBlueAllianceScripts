# Development
Set up gcloud sdk. Get Python App Engine SDK. In WSL, use command `/usr/lib/google-cloud-sdk/bin/dev_appserver.py --use_mtime_file_watcher=true app.yaml` to run. To deploy, `sudo gcloud app deploy app.yaml --project opr4917`

Python 2.7.9 or higher is recommended, or else you will run into strange SSL errors.
