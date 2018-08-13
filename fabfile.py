# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 10:13
# @Author  : vissssa
# @Email   : 292724306@qq.com
# @File    : fabfile.py
# @Software: PyCharm
from fabric.api import *
from datetime import datetime

env.user = 'root'
# env.roledefs = {
#     'zookeeper': ['root@192.168.1.177', 'root@192.168.1.179', 'root@192.168.1.180'],
#     'zookeeper01': ['root@192.168.1.177'],
#     'zookeeper02': ['root@192.168.1.179'],
#     'zookeeper03': ['root@192.168.1.180'],
#     'nimbus': ['root@192.168.1.176'],
#     'supervisor01': ['root@192.168.1.178'],
#     'supervisor02': ['root@192.168.1.181'],
#     'storm': ['root@192.168.1.176', 'root@192.168.1.178', 'root@192.168.1.181'],
#     'nimbus_noroot': ['123@192.168.1.176']
# }
#
# # 需要注意的是，这里的host strings必须由username@host:port三部分构成，缺一不可，否则运行时还是会要求输入密码
# env.passwords = {
#     'root@192.168.1.177:22': '123123',
#     'root@192.168.1.179:22': '123123',
#     'root@192.168.1.180:22': '123123',
#     'root@192.168.1.176:22': '123123',
#     'root@192.168.1.178:22': '123123',
#     'root@192.168.1.181:22': '123123',
#     '123@192.168.1.176:22': '123'
# }

zookeeper01 = 'root@192.168.1.168'
zookeeper02 = 'root@192.168.1.167'
zookeeper03 = 'root@192.168.1.166'
nimbus = 'root@192.168.1.164'
nimbus_noroot = '123@192.168.1.164'
supervisor01 = 'root@192.168.1.165'
supervisor02 = 'root@192.168.1.163'

local_dir = '/Users/zhangyu/PycharmProjects/fabric_test/local_dir'
remote_dir = '/home/123/project_dpi'

env.roledefs = {
    'zookeeper': [zookeeper01, zookeeper02, zookeeper03],
    'zookeeper01': [zookeeper01],
    'zookeeper02': [zookeeper02],
    'zookeeper03': [zookeeper03],
    'nimbus': [nimbus],
    'supervisor01': [supervisor01],
    'supervisor02': [supervisor02],
    'storm': [nimbus, supervisor01, supervisor02],
    'nimbus_noroot': [nimbus_noroot]
}

# 需要注意的是，这里的host strings必须由username@host:port三部分构成，缺一不可，否则运行时还是会要求输入密码
env.passwords = {
    '{}:22'.format(zookeeper01): '123123',
    '{}:22'.format(zookeeper02): '123123',
    '{}:22'.format(zookeeper03): '123123',
    '{}:22'.format(nimbus): '123123',
    '{}:22'.format(supervisor01): '123123',
    '{}:22'.format(supervisor02): '123123',
    '{}:22'.format(nimbus_noroot): '123'
}


@roles('zookeeper')
@parallel
def put_zookeeper():
    put('{}/zookeeper-3.4.9.tar.gz'.format(local_dir), '/usr/local/zookeeper-3.4.9.tar.gz')
    with cd('/usr/local'):
        run('tar -zxvf zookeeper-3.4.9.tar.gz')
        run('mv zookeeper-3.4.9 zookeeper')
    put('{}/zoo.cfg'.format(local_dir), '/usr/local/zookeeper/conf/zoo.cfg')
    run('iptables -I INPUT -m state --state NEW -p tcp --dport 2181 -j ACCEPT')
    run('iptables -I INPUT -m state --state NEW -p tcp --dport 2888 -j ACCEPT')
    run('iptables -I INPUT -m state --state NEW -p tcp --dport 3888 -j ACCEPT')
    # 讲开放端口保存到配置中
    run('service iptables save')
    run('service iptables restart')


# 三种不同的myid
@roles('zookeeper01')
def myid1():
    with cd('/usr/local/zookeeper'):
        run('mkdir -p -p data')
        run('echo 0 >> data/myid')


@roles('zookeeper02')
def myid2():
    with cd('/usr/local/zookeeper'):
        run('mkdir -p -p data')
        run('echo 1 >> data/myid')


@roles('zookeeper03')
def myid3():
    with cd('/usr/local/zookeeper'):
        run('mkdir -p -p data')
        run('echo 2 >> data/myid')


@roles('zookeeper')
@parallel
def start_zkp():
    with cd('/usr/local/zookeeper'):
        run('bin/zkServer.sh start')


@roles('zookeeper')
def status_zkp():
    with cd('/usr/local/zookeeper'):
        run('bin/zkServer.sh status')


def task_zkp():
    with open('time.txt', 'a') as f:
        f.write('zkp start: {} \n'.format(str(datetime.now())))
    execute(put_zookeeper)
    execute(myid1)
    execute(myid2)
    execute(myid3)
    execute(start_zkp)
    # execute(status_zkp)
    with open('time.txt', 'a') as f:
        f.write('zkp end: {} \n'.format(str(datetime.now())))


@roles('storm')
@parallel
def put_storm():
    run('mkdir -p {} && chmod 777 {}'.format(remote_dir, remote_dir))
    run('rm -rf /var/run/yum.pid')
    run('yum install java-1.8.0-openjdk -y')
    put('{}/apache-storm-1.1.2.tar.gz'.format(local_dir), '{}/apache-storm-1.1.2.tar.gz'.format(remote_dir))
    with cd(remote_dir):
        run('tar zxvf apache-storm-1.1.2.tar.gz')
        run('mkdir -p storm_data')
    put('{}/storm.yaml'.format(local_dir), '{}/apache-storm-1.1.2/conf/storm.yaml'.format(remote_dir))


@roles('nimbus')
def put_hostname_n():
    run('''sed -i "6i storm.local.hostname: '{}'" {}/apache-storm-1.1.2/conf/storm.yaml'''.format(
        nimbus.replace('root@', ''), remote_dir))


@roles('supervisor01')
def put_hostname_s1():
    run('''sed -i "6i storm.local.hostname: '{}'" {}/apache-storm-1.1.2/conf/storm.yaml'''.format(
        supervisor01.replace('root@', ''), remote_dir))


@roles('supervisor02')
def put_hostname_s2():
    run('''sed -i "6i storm.local.hostname: '{}'" {}/apache-storm-1.1.2/conf/storm.yaml'''.format(
        supervisor02.replace('root@', ''), remote_dir))


@roles('nimbus')
def start_n():
    run("$(nohup {}/apache-storm-1.1.2/bin/storm ui >/dev/null 2>&1 &) && sleep 1 "
        "&& $(nohup {}/apache-storm-1.1.2/bin/storm nimbus >/dev/null 2>&1 &) && sleep 1"
        "&& $(nohup {}/apache-storm-1.1.2/bin/storm logviewer >/dev/null 2>&1 &) && sleep 1".format(remote_dir,
                                                                                                    remote_dir,
                                                                                                    remote_dir))
    # run("$(nohup /home/123/Desktop/apache-storm-1.1.2/bin/storm nimbus >/dev/null 2>&1 &) && sleep 1")


@roles('supervisor01')
def start_s1():
    run("$(nohup {}/apache-storm-1.1.2/bin/storm supervisor >/dev/null 2>&1 &) && sleep 1 "
        "&& $(nohup {}/apache-storm-1.1.2/bin/storm logviewer >/dev/null 2>&1 &) && sleep 1".format(remote_dir,
                                                                                                    remote_dir))
    # run("$(nohup /home/123/Desktop/apache-storm-1.1.2/bin/storm logviewer >/dev/null 2>&1 &) && sleep 1")


@roles('supervisor02')
def start_s2():
    run("$(nohup {}/apache-storm-1.1.2/bin/storm supervisor >/dev/null 2>&1 &) && sleep 1 "
        "&& $(nohup {}/apache-storm-1.1.2/bin/storm logviewer >/dev/null 2>&1 &) && sleep 1".format(remote_dir,
                                                                                                    remote_dir))
    # run("$(nohup /home/123/Desktop/apache-storm-1.1.2/bin/storm logviewer >/dev/null 2>&1 &) && sleep 1")


@roles('storm')
@parallel
def ip_storm():
    run('iptables -I INPUT -m state --state NEW -p tcp --dport 8000 -j ACCEPT')
    run('iptables -I INPUT -m state --state NEW -p tcp --dport 8080 -j ACCEPT')
    run('iptables -I INPUT -m state --state NEW -p tcp --dport 6627 -j ACCEPT')
    run('iptables -I INPUT -m state --state NEW -p tcp --dport 6700 -j ACCEPT')
    run('iptables -I INPUT -m state --state NEW -p tcp --dport 6701 -j ACCEPT')
    run('iptables -I INPUT -m state --state NEW -p tcp --dport 6702 -j ACCEPT')
    run('iptables -I INPUT -m state --state NEW -p tcp --dport 6703 -j ACCEPT')
    run('service iptables save')
    run('service iptables restart')


@roles('supervisor02')
def stop_storm():
    # run("kill `ps aux | egrep '(daemon\.nimbus)|(storm\.ui\.core)' | fgrep -v egrep | awk '{print $2}'`")
    run("kill `ps aux | fgrep storm | fgrep -v 'fgrep' | awk '{print $2}'`")


def task_storm():
    with open('time.txt', 'a') as f:
        f.write('storm start: {} \n'.format(str(datetime.now())))
    execute(put_storm)
    execute(put_hostname_n)
    execute(put_hostname_s1)
    execute(put_hostname_s2)
    execute(ip_storm)
    execute(start_n)
    execute(start_s1)
    execute(start_s2)
    with open('time.txt', 'a') as f:
        f.write('storm end: {} \n'.format(str(datetime.now())))


@roles('storm')
@parallel
def put_python3():
    put('{}/Python-3.6.6.tgz'.format(local_dir), '{}/Python-3.6.6.tgz'.format(remote_dir))
    with cd(remote_dir):
        run('rm -rf /var/run/yum.pid')
        run('yum install zlib-devel bzip2-devel openssl-devel ncurese-devel gcc zlib sqlite-devel -y')
        run('tar zxvf Python-3.6.6.tgz')
        with cd('Python-3.6.6'):
            run('./configure --enable-loadable-sqlite-extensions --prefix=/usr/local/python3 && make && make install')

    run('ln -s /usr/local/python3/bin/python3 /usr/bin/python3')
    run('ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3')
    with cd('~/.config'):
        run('mkdir -p pip')
        put('{}/pip.conf'.format(local_dir), '~/.config/pip/pip.conf')
    run('pip3 install virtualenv')
    run('''echo 'export PATH="$PATH:/usr/local/python3/bin"' >> /etc/profile''')
    run('source /etc/profile')


@roles('storm')
@parallel
def update_glibc():
    # 找到新的快速升级方法

    # put('/Users/zhangyu/Downloads/glibc-2.17.tar.gz', '/home/123/Desktop/glibc-2.17.tar.gz')
    # with cd('/home/123/Desktop'):
    #     run('tar -xvf glibc-2.17.tar.gz')
    #     run('mkdir -p glibc_build_2.17')
    #     with cd('glibc_build_2.17'):
    #         run('../glibc-2.17/configure  --prefix=/usr --disable-profile --enable-add-ons --with-headers=/usr/include '
    #             '--with-binutils=/usr/bin && make -j4 && make install')

    put('{}/glibc-2.17-55.el6.x86_64.rpm'.format(local_dir),
        '{}/glibc-2.17-55.el6.x86_64.rpm'.format(remote_dir))
    put('{}/glibc-common-2.17-55.el6.x86_64.rpm'.format(local_dir),
        '{}/glibc-common-2.17-55.el6.x86_64.rpm'.format(remote_dir))
    put('{}/glibc-devel-2.17-55.el6.x86_64.rpm'.format(local_dir),
        '{}/glibc-devel-2.17-55.el6.x86_64.rpm'.format(remote_dir))
    put('{}/glibc-headers-2.17-55.el6.x86_64.rpm'.format(local_dir),
        '{}/glibc-headers-2.17-55.el6.x86_64.rpm'.format(remote_dir))
    put('{}/update_glibc.sh'.format(local_dir), '{}/update_glibc.sh'.format(remote_dir))
    run('yum install kernel-headers -y')
    with cd(remote_dir):
        run('bash update_glibc.sh')
    run('strings /lib64/libc.so.6 | grep GLIBC')


@roles('storm')
@parallel
def update_gcc():
    # 直接安装gcc-4.8.1会出现make error的情况， 所以我直接拿生成好的libstdc++so.6.18来替换

    # put('/Users/zhangyu/Downloads/gcc-4.8.1.tar.gz', '/home/123/Desktop/gcc-4.8.1.tar.gz')
    # with cd('/home/123/Desktop'):
    #     run('tar -xvzf gcc-4.8.1.tar.gz')
    #     with cd('gcc-4.8.1'):
    #         run('./contrib/download_prerequisites')
    #     run('mkdir -p build_gcc_4.8.1')
    #     with cd('build_gcc_4.8.1'):
    #         run('../gcc-4.8.1/configure --enable-checking=release --enable-languages=c,c++ --disable-multilib '
    #             '&& make -j4 && make install')
    # run('/usr/sbin/update-alternatives --install  '
    #     '/usr/bin/gcc gcc /usr/local/bin/x86_64-unknown-linux-gnu-gcc-4.8.1 40')
    # run('/usr/sbin/update-alternatives --install /usr/bin/g++ g++ /usr/local/bin/g++ 40')

    put('{}/libstdc++.so.6.0.18'.format(local_dir), '/usr/lib64/libstdc++.so.6.0.18')
    with cd('/usr/lib64'):
        run('rm -rf libstdc++.so.6')
        run('ln -s libstdc++.so.6.0.18 libstdc++.so.6')


def task_env():
    with open('time.txt', 'a') as f:
        f.write('env start: {} \n'.format(str(datetime.now())))
    execute(put_python3)
    with open('time.txt', 'a') as f:
        f.write('glibc start: {} \n'.format(str(datetime.now())))
    execute(update_glibc)
    with open('time.txt', 'a') as f:
        f.write('glibc end: {} \n'.format(str(datetime.now())))
    execute(update_gcc)
    with open('time.txt', 'a') as f:
        f.write('env end: {} \n'.format(str(datetime.now())))


@roles('nimbus_noroot')
def start_project():
    # 下载容易出问题

    # with cd('~'):
    #     run('mkdir -p bin')
    # with cd('~/bin'):
    #     run('wget https://raw.githubusercontent.com/technomancy/leiningen/stable/bin/lein --no-check-certificate')
    # run('chmod a+x ~/bin/lein')
    # run('lein')

    run('mkdir -p ~/bin')
    put('{}/lein'.format(local_dir), '~/bin/lein')
    run('mkdir -p ~/.lein/self-installs')
    put('{}/leiningen-2.8.1-standalone.jar'.format(local_dir),
        '~/.lein/self-installs/leiningen-2.8.1-standalone.jar')
    run('chmod a+x ~/bin/lein')

    execute(pip)
    execute(nimbus_pip)

    put('{}/dpi_detection.zip'.format(local_dir), '{}/dpi_detection.zip'.format(remote_dir))
    with cd(remote_dir):
        run('unzip dpi_detection.zip')
        with cd('dpi_detection'):
            run('sparse submit')


@roles('storm')
@parallel
def pip():
    # 安装python3所需要的包
    put('{}/requirements.txt'.format(local_dir), '{}/requirements.txt'.format(remote_dir))
    # run('pip3 install --upgrade pip')
    run('source /etc/profile && virtualenv /data/virtualenvs/dpi_detection')
    put('{}/torch-0.4.1-cp36-cp36m-linux_x86_64.whl'.format(local_dir),
        '{}/torch-0.4.1-cp36-cp36m-linux_x86_64.whl'.format(remote_dir))
    for i in range(0, 3):
        try:
            run('source /data/virtualenvs/dpi_detection/bin/activate '
                '&& pip3 install {}/torch-0.4.1-cp36-cp36m-linux_x86_64.whl '
                '&& pip3 install -r {}/requirements.txt'.format(remote_dir, remote_dir))
        except:
            pass
        else:
            break
    run('mkdir -p /var/log/storm/streamparse')


@roles('nimbus')
def nimbus_pip():
    for i in range(0, 3):
        try:
            run('pip3 install --upgrade pip')
            run('pip3 install {}/torch-0.4.1-cp36-cp36m-linux_x86_64.whl'.format(remote_dir))
            run('pip3 install -r {}/requirements.txt'.format(remote_dir))
        except:
            pass
        else:
            break
    # run('yum install git -y')
    # run("echo '192.168.1.100 gitlab' >> /etc/hosts")


def task_project():
    with open('time.txt', 'a') as f:
        f.write('project start: {} \n'.format(str(datetime.now())))
    execute(start_project)
    with open('time.txt', 'a') as f:
        f.write('project end: {} \n'.format(str(datetime.now())))


def task():
    execute(task_zkp)
    execute(task_storm)
    execute(task_env)
    execute(task_project)


def glibc():
    run('strings /lib64/libc.so.6 | grep GLIBC')
    run('strings /usr/lib64/libstdc++.so.6 | grep GLIBCXX')
