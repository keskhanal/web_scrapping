if chromedriver --version
then
    echo 'yes chromedriver'
else
    cd /tmp/
    wget https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip
    sudo mv chromedriver /usr/bin/chromedriver
fi