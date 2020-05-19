#!/bin/bash

downloadLink="https://github.com/wqhot/zntk_core.git"
branchName="sgimu"
nowDir=`pwd`
sshServer="10.42.0.1"
sshUserName="shipei"
echo "ssh设置中..."
ssh-keygen -t rsa -f ~/.ssh/id_zntkrsa -N "" -C ""
ssh-copy-id -i ~/.ssh/id_zntkrsa ${sshUserName}@${sshServer}
echo "下载中..."
mkdir -p ~/zntk_tmp
cd ~/zntk_tmp
git clone -b ${branchName} ${downloadLink} --depth=1
scp -r zntk_core ${sshUserName}@${sshServer}:/home/${sshUserName}/zntk_tmp
echo "编译中..."
ssh ${sshUserName}@${sshServer}  > /dev/null 2>&1 << eeooff
cd /home/${sshUserName}/zntk_tmp
mkdir build
cd build
cmake ..
make -j4
mkdir -p /home/${sshUserName}/zntk/zntk_core_1
cd /home/${sshUserName}/zntk/zntk_core_1
mkdir -p bin
mkdir -p config
cp -af /home/${sshUserName}/zntk_tmp/build/zntk_core bin/zntk_core
cp -af /home/${sshUserName}/zntk_tmp/build/imu_init bin/imu_init
cp -rf /home/${sshUserName}/zntk_tmp/config .
mkdir -p /home/${sshUserName}/output
# rm -rf /home/${sshUserName}/zntk_tmp
exit
eeooff
# rm -rf ~/zntk_tmp
cd ${nowDir}
