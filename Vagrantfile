# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "generic/ubuntu1804"
    config.vm.box_check_update = false
    # config.vm.network "private_network", ip: "192.168.10.50"
    config.vm.network "forwarded_port", guest: 8888, host: 8888

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder "./ddset", "/home/vagrant/ddset"

  config.vm.provider "virtualbox" do |v|
      v.memory = 8048
      v.cpus = 2
  end

  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get -y install openjdk-11-jre-headless
    apt-get -y install make
    apt-get -y install docker.io
    apt-get -y install graphviz
    apt-get -y install python3-venv
    apt-get -y install python3-pip
    pip3 install wheel
    pip3 install graphviz
    pip3 install jupyter
    pip3 install pudb

    pip3 install jupyter_contrib_nbextensions
    pip3 install jupyter_nbextensions_configurator
    jupyter contrib nbextension install --sys-prefix
    jupyter nbextension enable toc2/main --sys-prefix
  SHELL
end
