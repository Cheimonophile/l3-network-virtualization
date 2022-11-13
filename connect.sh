#!/bin/bash -xe
ssh -F secrets/ssh/config -i secrets/ssh/fabric-sliver "ubuntu@$1"