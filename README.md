# NYPL_Taxonomy_Application

## Introduction

This project is developed by NYPL team for Information technology project course of NYU.

We collaborate with New York Public library and come up with this project which could help their daily work.

This course is taught by Professor Jean-Claude Franchitti and this project involves NLP (Natural language Processing)
and some other technologies which is really crucial and helpful for our daily lives.

## Setting up Development Environment
To get started, download and install VirtualBox and Vagrant.
Download [VirtualBox](https://www.virtualbox.org/
Download [Vagrant](https://www.vagrantup.com/)

Clone the project to your development folder and create your Vagrant vm

```bash
    git clone git@github.com:ITP19NYPL/NYPL_Taxonomy_Application.git
    cd NYPL_Taxonomy_Application
    vagrant up
    vagrant ssh
    cd /vagrant
```

## Start Service
You can see the service running in your browser by going to
[http://localhost:5000](http://localhost:5000) after use the `honcho` command

```bash
    honcho start
```

## Testing
Run the tests suite with:
```sh
    nosetests
```

## Shutdown
When you are done, you can exit and shut down the vm with:

```bash
    exit
    vagrant halt
```

If the VM is no longer needed you can remove it with:

```bash
    vagrant destroy
```
