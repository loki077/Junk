#! /usr/bin/bash

# Install Scripts for Ubuntu 20.
# CX-Software -Lokesh install all default software and repo required for a new VM

printf 'Welcome $(whoami). This script is to install default apps for CX-Software'
printf 'Included....\nnet-tools\nVScode\nGitkraken\nGithub\n'
printf 'Begin installation.........'

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