#!/usr/bin/env bash

# workaround for a bug in debian9, i.e. starting mysql hangs
if [ "$1" = "debian11" ] || [ "$1" = "debian12" ] || [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu24.10" ] || [ "$1" = "ubuntu25.04" ]; then
    docker exec --user root ndts service mariadb restart
else
    docker exec --user root ndts service mysql stop
    if [ "$1" = "ubuntu20.04" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "ubuntu21.04" ] || [ "$1" = "ubuntu22.04" ]; then
	# docker exec --user root ndts /bin/bash -c 'mkdir -p /var/lib/mysql'
	# docker exec --user root ndts /bin/bash -c 'chown mysql:mysql /var/lib/mysql'
	docker exec --user root ndts /bin/bash -c 'usermod -d /var/lib/mysql/ mysql'
    fi
    docker exec --user root ndts service mysql start
    # docker exec  --user root ndts /bin/bash -c '$(service mysql start &) && sleep 30'
fi

docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y xvfb  libxcb1 libx11-xcb1 libxcb-keysyms1 libxcb-image0 libxcb-icccm4 libxcb-render-util0 xkb-data tango-common; sleep 10'
if [ "$?" -ne "0" ]; then exit 255; fi
if  [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu24.10" ] || [ "$1" = "ubuntu25.04" ]; then
    # docker exec  --user tango ndts /bin/bash -c '/usr/lib/tango/DataBaseds 2 -ORBendPoint giop:tcp::10000  &'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=root\npassword=rootpw" > /root/.my.cnf'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=tango\nhost=localhost\npassword=rootpw" > /var/lib/tango/.my.cnf'
    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON tango.* TO "tango"@"%" identified by "rootpw"'
    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON tango.* TO "tango"@"localhost" identified by "rootpw"'
    docker exec  --user root ndts /usr/bin/mysql -e 'FLUSH PRIVILEGES'
fi
if [ "$1" = "ubuntu20.04" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "ubuntu21.04" ] || [ "$1" = "ubuntu21.10" ] || [ "$1" = "ubuntu22.04" ]; then
    # docker exec  --user tango ndts /bin/bash -c '/usr/lib/tango/DataBaseds 2 -ORBendPoint giop:tcp::10000  &'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=root\npassword=rootpw" > /root/.my.cnf'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=tango\nhost=127.0.0.1\npassword=rootpw" > /var/lib/tango/.my.cnf'
fi
echo "install tango-db"
docker exec  --user root ndts /bin/bash -c 'apt-get -qq update; export DEBIAN_FRONTEND=noninteractive; apt-get -qq install -y tango-db; sleep 10'
if [ "$?" -ne "0" ]; then exit 255; fi
if  [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu24.10" ] || [ "$1" = "ubuntu25.04" ]; then
    docker exec  --user tango ndts /usr/bin/mysql -e 'create database tango'
    docker exec  --user tango ndts /bin/bash -c '/usr/bin/mysql tango < /usr/share/dbconfig-common/data/tango-db/install/mysql'
fi

docker exec  --user root ndts service tango-db restart

docker exec  --user root ndts mkdir -p /tmp/runtime-tango
docker exec  --user root ndts chown -R tango:tango /tmp/runtime-tango


if [ "$?" -ne "0" ]; then exit 255; fi
echo "start Xvfb :99 -screen 0 1024x768x24 &"
docker exec  --user root ndts /bin/bash -c 'export DISPLAY=":99.0"; Xvfb :99 -screen 0 1024x768x24 &'
if [ "$?" -ne "0" ]; then exit 255; fi

echo "install tango servers"
docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y  tango-starter tango-test liblog4j1.2-java git'
if [ "$?" -ne "0" ]; then exit 255; fi

docker exec  --user root ndts service tango-starter restart


if [[ "$2" = "2" ]]; then
    echo "install python-pytango"
    docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   python-pytango python-h5py  python-qtpy python-click git python-itango python-pint  nxsconfigserver-db  ; sleep 10' 
else
    echo "install python3-pytango"
    if [ "$1" = "debian9" ]; then
	docker exec  --user root ndts /bin/bash -c 'git clone https://github.com/hgrecco/pint pint-src; cd pint-src'
	docker exec  --user root ndts /bin/bash -c 'cd pint-src; git checkout tags/0.8.1 -b b0.8.1; python3 setup.py install'
	docker exec  --user root ndts /bin/bash -c 'git clone https://gitlab.com/tango-controls/itango  itango-src; cd itango-src'
	docker exec  --user root ndts /bin/bash -c 'cd itango-src; git checkout tags/v0.1.7 -b b0.1.7; python3 setup.py install'
	# docker exec  --user root ndts /bin/bash -c 'cd taurus-src; git checkout; python3 setup.py install'
    fi
    if [ "$1" = "debian10" ] || [ "$1" = "ubuntu20.04" ] || [ "$1" = "ubuntu22.04" ] || [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu24.10" ] || [ "$1" = "ubuntu25.04" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "debian11" ] || [ "$1" = "debian12" ] ; then
	docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get install -y git python3-six python3-numpy graphviz python3-sphinx g++ build-essential python3-dev pkg-config python3-all-dev  python3-setuptools libtango-dev python3-setuptools python3-tango python3-tz; apt-get -qq install -y nxsconfigserver-db; sleep 10'
    else
	docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get install -y git python3-six python3-numpy graphviz python3-sphinx g++ build-essential python3-dev pkg-config python3-all-dev  python3-setuptools libtango-dev python3-setuptools python3-pytango python3-tz; apt-get -qq install -y nxsconfigserver-db; sleep 10'
    fi
    docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get install -y libboost-python-dev libboost-dev python3-h5py python3-qtpy  python3-click python3-setuptools  python3-pint'
    if [ "$1" = "ubuntu20.04" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "ubuntu21.04" ]  || [ "$1" = "ubuntu22.04" ]|| [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu24.10" ] || [ "$1" = "ubuntu25.04" ] || [ "$1" = "debian11" ] || [ "$1" = "debian12" ] || [ "$1" = "debian10" ]; then
	echo " "
    else
	docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get install -y libtango-dev python3-dev'
	docker exec  --user root ndts /bin/bash -c 'git clone https://gitlab.com/tango-controls/pytango pytango; cd pytango; git checkout tags/v9.2.5 -b b9.2.5'
	docker exec  --user root ndts /bin/bash -c 'cd pytango; python3 setup.py install'
    fi
    if [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu24.10" ] || [ "$1" = "ubuntu25.04" ]; then
	docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON nxsconfig.* TO "tango"@"%" identified by "rootpw"'
	docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON nxsconfig.* TO "tango"@"localhost" identified by "rootpw"'
	docker exec  --user root ndts /usr/bin/mysql -e 'FLUSH PRIVILEGES'
	docker exec  --user tango ndts /usr/bin/mysql -e 'create database nxsconfig'
	docker exec  --user tango ndts /bin/bash -c '/usr/bin/mysql nxsconfig < /usr/share/dbconfig-common/data/nxsconfigserver-db/install/mysql'
    fi
fi
if [ "$?" -ne "0" ]; then exit 255; fi

echo "install qt5"
if [ "$1" = "debian12" ] ||[ "$1" = "debian11" ] || [ "$1" = "ubuntu22.04" ] || [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu24.10" ] || [ "$1" = "ubuntu25.04" ]; then
    docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y  qtbase5-dev-tools'
else
    docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y  qtbase5-dev-tools qt5-default'
fi


if [ "$?" -ne "0" ]; then exit 255; fi


if [ "$2" = "2" ]; then
    echo "install pytango and nxsconfigserver-db"
    docker exec  --user root ndts /bin/bash -c 'apt-get -qq update; apt-get install -y   python-pytango  nxsconfigserver-db ; sleep 10'
else
    if [ "$1" = "debian10" ] || [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu24.10" ] || [ "$1" = "ubuntu25.04" ] || [ "$1" = "ubuntu22.04" ] || [ "$1" = "ubuntu20.04" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "debian11" ] || [ "$1" = "debian12" ] ; then
	echo "install pytango"
	docker exec --user root ndts /bin/bash -c 'apt-get -qq update; apt-get install -y   python3-tango'
	echo "install nxsconfigserver-db"
	docker exec --user root ndts /bin/bash -c 'apt-get -qq update; apt-get  install -y   nxsconfigserver-db'
    else
	echo "install pytango and nxsconfigserver-db"
	docker exec  --user root ndts /bin/bash -c 'apt-get -qq update; apt-get -qq install -y   python3-pytango nxsconfigserver-db; sleep 10'
    fi
fi
if [ "$?" != "0" ]; then exit 255; fi


if [[ "$2" == "2" ]]; then
    echo "install sardana, taurus and nexdatas"
    docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y  nxsconfigserver-db; sleep 10; apt-get -qq install -y python-nxsconfigserver python-nxswriter python-nxstools python-nxsrecselector  python-setuptools'
    if [[ "$1" == "debian10" ]]; then
	docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y python-taurus python-sardana'
    fi
else
    echo "install sardana, taurus and nexdatas"
    if [[ "$1" == "debian10" ]]; then
	docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update;  apt-get -qq install -y python3-nxsconfigserver python3-nxswriter python3-nxstools python3-nxsrecselector python3-setuptools nxsrecselector3 nxswriter3 nxsconfigserver3 nxstools3 python3-packaging'
	docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y python3-taurus python3-sardana'
    else
	docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update;  apt-get -qq install -y python3-nxsconfigserver python3-nxswriter python3-nxstools python3-nxsrecselector python3-setuptools nxsrecselector nxswriter nxsconfigserver nxstools python3-packaging'
	docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y python3-taurus python3-sardana'
    fi
fi
if [ "$?" -ne "0" ]; then exit 255; fi

if [[ "$2" == "2" ]]; then
    echo "install nxselector"
    docker exec --user root ndts chown -R tango:tango .
    docker exec  ndts python setup.py build
    docker exec --user root ndts python setup.py  install
else
    echo "install nxselector3"
    docker exec --user root ndts chown -R tango:tango .
    docker exec  ndts python3 setup.py build
    docker exec --user root ndts python3 setup.py  install
fi
if [ "$?" -ne "0" ]; then exit 255; fi

docker exec  --user root ndts chown -R tango:tango .
