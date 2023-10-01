#! /usr/bin/bash

# Install Scripts for Ubuntu 20.
# CX-Software -Lokesh install all default software and repo required for a new VM

printf 'Welcome $(whoami). This script is to install default apps for CX-Software'
printf 'Included....\nnet-tools\nVScode\nGitkraken\nGithub\n'
printf 'Begin installation.........'

# Get the currently logged-in username using the `whoami` command
username=$(whoami)

cd ~
sudo apt update
sudo apt install -yy net-tools git && snap install code gitkraken
sudo apt install -yy gitk git-gui



#Install Chrome, Sublime 
cd ~/Downloads

#Install Lokesh Dev Repo
cd ~
cd ~/Desktop
mkdir -p dev
cd dev

if [ ! -d "Junk/.git" ]
then
    git clone https://github.com/Lokesh-Carbonix/Junk.git
else
    cd Junk
    git pull
    cd ..
fi

if [ ! -d "gui_tool/.git" ]
then
    git clone https://github.com/Lokesh-Carbonix/gui_tool.git
else
    cd gui_tool
    git pull
    cd ..
fi

if [ ! -d "examples/.git" ]
then
    git clone https://github.com/Lokesh-Carbonix/examples.git
else
    cd examples
    git pull
    cd ..
fi

#Intsall Carbonix Repo
cd ~
cd ~/Desktop
mkdir -p cx_dev
cd cx_dev

if [ ! -d "ardupilot/.git" ]
then
    git clone https://github.com/CarbonixUAV/ardupilot.git
    git submodule update --init --recursive
    Tools/environment_install/install-prereqs-ubuntu.sh -y
    . ~/.profile
    ./waf configure
else
    cd ardupilot
    git pull
    cd ..
fi

if [ ! -d "carbopilot_V2/.git" ] 
then
    git clone https://github.com/CarbonixUAV/carbopilot_V2.git
    git submodule update --init --recursive
    Tools/environment_install/install-prereqs-ubuntu.sh -y
    . ~/.profile
    ./waf configure
    # git clone https://username:password@github.com/CarbonixUAV/carbopilot_V2.git
else
    cd carbopilot_V2
    git pull
    cd ..
fi

#instal drone can GUI
sudo apt install -y python3-pip python3-setuptools python3-wheel
sudo apt install -y python3-numpy python3-pyqt5 python3-pyqt5.qtsvg git-core
sudo pip3 install numpy --upgrade


sudo pip3 install git+https://github.com/DroneCAN/gui_tool@master

#show branch name on terminal
# git_branch() {
#   git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
# }
# export PS1="\e[1m\e[32m\u@\h\e[0m\e[0m:\e[1m\e[34m\w\e[0m\e[1;33m\$(git_branch)\e[0m\$ "
source ~/.bashrc


sudo apt install mlocate

# Add Google Chrome repository
echo "Adding Google Chrome repository..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list > /dev/null

# Update package list
echo "Updating package list..."
sudo apt update

# Install Google Chrome
echo "Installing Google Chrome..."
sudo apt install google-chrome-stable

echo "Google Chrome installation complete."

#install ACT for local CI
# Function to print step headers
print_step() {
  echo "--------------------------------------------------"
  echo "Step $1: $2"
  echo "--------------------------------------------------"
}

# Prerequisites

print_step 1 "Install Docker on Ubuntu"

# Step 1: Install Docker on Ubuntu
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu focal stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
sudo docker --version
sudo usermod -aG docker $username

print_step 2 "Install Brew in Ubuntu"

# Step 2: Install Brew in Ubuntu
sudo apt update
sudo apt install build-essential curl file git
sh -c "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/install/master/install.sh)"
(echo; echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"') >> ~/.profile
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
sudo apt-get install build-essential
brew install gcc

print_step 3 "Install act"

# Step 3: Install act
brew --version
brew install act
act --version

echo "Congratulations! You have successfully set up and run GitHub Action CI locally on your Ubuntu machine using the act tool."


# create Git alias
# Alias for 'status'
git config --global alias.st status

# Alias for 'log' with a pretty format
git config --global alias.lg "log --oneline --graph --decorate --all"

# Alias for 'commit' with a helpful message
git config --global alias.ci "commit -m"

# Alias for 'branch' to list branches
git config --global alias.br branch

# Alias for 'diff' with color highlighting
git config --global alias.dif "diff --color"

git config --global alias.co checkout

git config --global alias.cob "checkout -b"

git config --global alias.su "submodule update --init --recursive"


#install cmake
sudo apt install cmake
