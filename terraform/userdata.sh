#!/bin/bash
apt-get update -y
apt-get install -y docker.io docker-compose-plugin git

systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

mkdir -p /opt/pastebin
chown ubuntu:ubuntu /opt/pastebin
