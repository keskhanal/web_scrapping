if chromedriver --version
then
    echo 'yes chromedriver'
else
    sudo yum install -y chromium libmng libXScrnSaver libXv
    cd /tmp/
    wget https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip
    sudo mv chromedriver /usr/bin/chromedriver

    curl https://intoli.com/install-google-chrome.sh | bash
    sudo mv /usr/bin/google-chrome-stable /usr/bin/google-chrome
    google-chrome --version && which google-chrome
fi