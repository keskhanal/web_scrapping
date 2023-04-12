if chromedriver --version
then
    echo 'yes chromedriver'
else
    sudo yum install libxi6 libgconf-2-4
    cd /tmp/
    wget https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip
    sudo mv chromedriver /usr/bin/chromedriver
fi