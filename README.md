# splinterlands-stats

How-to use:

https://peakd.com/hive-13323/@beaker007/how-to-use-the-splinterlands-season-statistics-tool-python


## TODO
* Create manual
* Reference to PeakD post on how to use it?



## Installed python packages:
see requirement text

# Test docker
docker login ghcr.io --username your_github_username

docker pull ghcr.io/gamerbeaker007/splinterlands-stats:latest

## windows:
docker run -it -v C:\Temp\:/app/output -e "ACCOUNT_NAMES=spl_account_name,spl_name2" -e "TIME_ZONE=Europe/Amsterdam" -e "SKIP_ZEROS=True" ghcr.io/gamerbeaker007/splinterlands-stats:latest

## Linux:
docker run -it -v \tmp\:/app/output -e "ACCOUNT_NAMES=spl_account_name, spl_name2" -e "TIME_ZONE=Europe/Amsterdam" -e "SKIP_ZEROS=True" ghcr.io/gamerbeaker007/splinterlands-stats:latest