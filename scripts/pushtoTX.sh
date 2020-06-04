#!/bin/bash
nowDir=`pwd`
sshServer="10.42.0.1"
sshUserName="shipei"
cd ~/zntk/
scp -r zntk_core ${sshUserName}@${sshServer}:/home/${sshUserName}/zntk/zntk_core
echo "编译中..."
ssh ${sshUserName}@${sshServer}  > /dev/null 2>&1 << eeooff
cd /home/${sshUserName}/zntk/zntk_core
mkdir build
cd build
cmake ..
make -j4
exit
eeooff
cd ${nowDir}
