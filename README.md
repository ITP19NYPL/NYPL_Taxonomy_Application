# NYPL_Taxonomy_Application

## Introduction

This project is developed by NYPL team [@Proneet27](https://github.com/Proneet27), [@DerrickBu](https://github.com/DerrickBu), [@xchen20](https://github.com/xchen20), [@joanne3634](https://github.com/joanne3634) for Information technology project course of NYU.

We collaborate with New York Public library and come up with this project which could help their daily work.

This course is taught by Professor Jean-Claude Franchitti and this project involves NLP (Natural language Processing)
and some other technologies which is really crucial and helpful for our daily lives.

All the deliverables can be found in the [sharing folder](https://drive.google.com/open?id=1F2129MiDaLzAa-kERRjKDVpU8Iph7SuT) including Business Model Canvas, Showcase Videos, Technical & Business Poster, Kickoff and Showcase decks, Flyer and Report.

## Set up
To get started, download and install [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/). Then clone the project to your development folder and invoke vagrant.

```bash
    git clone git@github.com:ITP19NYPL/NYPL_Taxonomy_Application.git
    cd NYPL_Taxonomy_Application
    vagrant up
    vagrant ssh
    cd /vagrant
```

## pre-train model
Download the GoogleNew, and run train.py.

```bash
    cd /vagrant/service/train
    wget -c "https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz"
    gunzip -f GoogleNews-vectors-negative300.bin.gz
    cd /vagrant
    python3 service/train.py
```

## Start Service

```bash
    honcho start
```

## View App with UI
You can see the service running in your browser by going to
[http://localhost:5000](http://localhost:5000) after use the `honcho` command

## Swagger Restful API Doc

[http://localhost:5000/apidocs/index.html](http://localhost:5000/apidocs/index.html)

## API Endpoint

##### Query top n similarity words of target_word

- By target_word and number:  GET `/category?target_word={string:target_word}&number={int:number}`

##### Create a new category

- PATH: POST `/category`

##### Get a category by a category id

- PATH: GET `/category/{string:id} `

##### List all categories

- PATH: GET `/category`

##### Delete a category

- PATH: DELETE `/category/{string:id} `


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
