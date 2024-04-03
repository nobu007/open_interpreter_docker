# open_interpreter_docker

[Open Interpreter](https://github.com/KillianLucas/open-interpreter) docker environment

## Prerequisite

Install docker and docker-compose.
This is sample steps for ubuntu 22.04.

```sh
sudo apt install gnome-terminal
sudo apt install docker-ce
sudo apt install docker-compose
```

Please see.
https://docs.docker.com/desktop/install/ubuntu/

## Setup

Execute following command:

```sh
$ cd && git clone https://github.com/nobu007/open_interpreter_docker.git
```

## Run

### Docker build & run

```sh
$ cd ~/open_interpreter_docker
$ docker-compose up --build
```

### Browse app

Browse http://localhost:8000/test

Enjoy open interpreter

## RUN(with GPU)

### Docker build & run

```sh
$ cd ~/open_interpreter_docker
$ docker-compose -f docker-compose.gpu.yml up --build
```

## Errors

```bash
ERROR: for open-interpreter  'ContainerConfig'
KeyError: 'ContainerConfig'
```

Run this.

```bash
docker-compose down
docker-compose -f docker-compose.gpu.yml down
```

Or prune this.

```bash
docker system prune
```

## Special Thanks

Desktop docker. It was very helpful for me.
https://github.com/yama07/docker-ubuntu-lxde
