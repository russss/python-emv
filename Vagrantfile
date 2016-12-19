# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y pcscd pcsc-tools python-pyscard python-six
  SHELL

  config.vm.provider "virtualbox" do |v|
    v.customize ["modifyvm", :id, "--usb", "on"]
    v.customize ["modifyvm", :id, "--usbehci", "on"]
    v.customize ["usbfilter", "add", "0",
      "--target", :id,
      "--name", "Card Reader",
      "--manufacturer", "Gemplus",
      "--product", "USB SmartCard Reader"]
  end
end
