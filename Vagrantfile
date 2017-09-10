VAGRANTFILE_API_VERSION = "2"

cluster = {
  "rsimola" => { :name => "Imola-Rancher", :rancher => true, :ip => "192.168.33.105"},
  "lugo" => { :name => "Lugo-Backup", :ip => "192.168.33.101"},
  "exe" => { :name => "ExE-Production", :ip => "192.168.33.102"}
}

rancher_node = cluster.select{|k,v| v[:rancher]}.values[0]

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  cluster.each_with_index do |(hostname, info), index|

    config.vm.define hostname do |cfg|

        cfg.vm.box = "elastic/ubuntu-16.04-x86_64"

        cfg.vm.network :private_network, ip: "#{info[:ip]}"
        cfg.vm.hostname = info[:name]

        cfg.ssh.insert_key = false

        cfg.vm.provision "file", source: "~/.vagrant.d/less_insecure_private_key", destination: ".ssh/id_rsa"

        cfg.vm.provision :docker

        if info[:rancher]
          cfg.vm.provision "rancher" do |rancher|
              rancher.hostname = info[:ip]
          end
          cfg.vm.provision :shell, path: "vagrant_scripts/consul_server_init.sh",
            args: "%{machine_address}" % {:machine_address => '192.168.33.105'},
            run: "always"
        else
          cfg.vm.provision :shell, path: "vagrant_scripts/bootstrap.sh"

          cfg.vm.provision "rancher" do |rancher|
              #rancher.hostname = rancher_node[:ip]
              rancher.hostname = "192.168.33.105"
              rancher.role = 'agent'
          end

          cfg.vm.provision :shell, path: "vagrant_scripts/consul_client_init.sh",
              args:  "%{machine_address} %{consul_server_address}" %
                  {:machine_address => info[:ip], :consul_server_address => "192.168.33.105"},
              run: "always"
        end
    end # end config
  end # end cluster
end
