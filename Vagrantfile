$script = <<SCRIPT
sudo apt-get update
sudo apt-get install -y python-pip libmysqlclient-dev python-dev sqlite3
sudo pip install -U pip
cd /vagrant
sudo pip install -r requirements/compiled.txt
sudo pip install -r requirements/dev.txt
sudo pip install -r requirements/prod.txt
python kickoff-web.py -d sqlite:///update.db --username=admin --password=password --host=0.0.0.0 --port=5000 &
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "hashicorp/precise64" # Just a basic box
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.provision "shell", inline: $script
end
