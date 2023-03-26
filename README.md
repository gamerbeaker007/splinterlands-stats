# splinterlands-stats

# How-to use:
detail description on how to use on window with anaconda is given in post:

https://peakd.com/hive-13323/@beaker007/how-to-use-the-splinterlands-season-statistics-tool-python

## Installed python packages:
<code>pip install -r requirements.txt</code>

## Execute
Modify config.properties with you desired information

<code>python main.py</code>

# How to it use docker
<code>docker login ghcr.io --username your_github_username

docker pull ghcr.io/gamerbeaker007/splinterlands-stats:latest</code>

## Windows:
<code>docker run -it -v C:\Temp\:/app/output -e "ACCOUNT_NAMES=spl_account_name,spl_name2" -e "SKIP_ZEROS=True" ghcr.io/gamerbeaker007/splinterlands-stats:latest</code>

## Linux:
<code>docker run -it -v \tmp\:/app/output -e "ACCOUNT_NAMES=spl_account_name,spl_name2" -e "SKIP_ZEROS=True" ghcr.io/gamerbeaker007/splinterlands-stats:latest</code>