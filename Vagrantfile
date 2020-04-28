# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "generic/ubuntu1804"
  config.vm.box_check_update = false
  # config.vm.network "private_network", ip: "192.168.10.50"
  config.vm.network "forwarded_port", guest: 8888, host: 8888

  # we do not want a synced folder other than the default.
  # we will be extracting the tarred up ddset to home.
  config.vm.synced_folder "./ddset", "/vagrant/ddset"

  config.vm.provider "virtualbox" do |v|
    v.memory = 8048
    v.cpus = 2
  end

  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get -y install openjdk-11-jre-headless make docker.io graphviz python3-venv python3-pip
    pip3 install wheel
    pip3 install graphviz
    pip3 install jupyter
    pip3 install pudb

    pip3 install jupyter_contrib_nbextensions
    pip3 install jupyter_nbextensions_configurator
    jupyter contrib nbextension install --sys-prefix
    jupyter nbextension enable toc2/main --sys-prefix
    echo cd /home/vagrant/ddset >  /home/vagrant/startjupyter.sh
    echo jupyter notebook --ip 0.0.0.0 --port 8888 >> /home/vagrant/startjupyter.sh
    chmod +x /home/vagrant/startjupyter.sh

    echo cd /home/vagrant/ddset >  /home/vagrant/table1.sh
    echo python3 src/table1.py >>  /home/vagrant/table1.sh
    chmod +x /home/vagrant/table1.sh

    echo cd /home/vagrant/ddset >  /home/vagrant/table2.sh
    echo python3 src/table2.py >>  /home/vagrant/table2.sh
    chmod +x /home/vagrant/table2.sh
  SHELL
end
