# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 10:13
# @Author  : vissssa
# @Email   : 292724306@qq.com
# @File    : fabfile.py
# @Software: PyCharm
from fabric.api import *

env.user = 'root'
env.roledefs = {
    'zookeeper': ['root@192.168.1.177', 'root@192.168.1.179', 'root@192.168.1.180'],
    'zookeeper01': ['root@192.168.1.177'],
    'zookeeper02': ['root@192.168.1.179'],
    'zookeeper03': ['root@192.168.1.180'],
    'nimbus': ['root@192.168.1.176'],
    'supervisor01': ['root@192.168.1.178'],
    'supervisor02': ['root@192.168.1.181'],
    'storm': ['root@192.168.1.176', 'root@192.168.1.178', 'root@192.168.1.181'],
    'nimbus_noroot': ['123@192.168.1.176']
}

# 需要注意的是，这里的host strings必须由username@host:port三部分构成，缺一不可，否则运行时还是会要求输入密码
env.passwords = {
    'root@192.168.1.177:22': '123123',
    'root@192.168.1.179:22': '123123',
    'root@192.168.1.180:22': '123123',
    'root@192.168.1.176:22': '123123',
    'root@192.168.1.178:22': '123123',
    'root@192.168.1.181:22': '123123',
    '123@192.168.1.176:22': '123'
}


@roles('zookeeper')
def put_zookeeper():
    put('/Users/zhangyu/Downloads/zookeeper/zookeeper-3.4.9.tar.gz', '/usr/local/zookeeper-3.4.9.tar.gz')
    with cd('/usr/local'):
        run('tar -zxvf zookeeper-3.4.9.tar.gz')
        run('mv zookeeper-3.4.9 zookeeper')
    put('/Users/zhangyu/PycharmProjects/fabric_test/zoo.cfg', '/usr/local/zookeeper/conf/zoo.cfg')
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
def start_zkp():
    with cd('/usr/local/zookeeper'):
        run('bin/zkServer.sh start')


@roles('zookeeper')
def status_zkp():
    with cd('/usr/local/zookeeper'):
        run('bin/zkServer.sh status')


def task_zkp():
    execute(put_zookeeper)
    execute(myid1)
    execute(myid2)
    execute(myid3)
    execute(start_zkp)
    execute(status_zkp)


@roles('storm')
def put_storm():
    run('yum install java-1.8.0-openjdk -y')
    put('/Users/zhangyu/Downloads/apache-storm-1.1.2.tar.gz', '/home/123/Desktop/apache-storm-1.1.2.tar.gz')
    with cd('/home/123/Desktop'):
        run('tar zxvf apache-storm-1.1.2.tar.gz')
        run('mkdir -p -p storm_data')
    put('/Users/zhangyu/PycharmProjects/fabric_test/storm.yaml', '/home/123/Desktop/apache-storm-1.1.2/conf/storm.yaml')


@roles('nimbus')
def put_hostname_n():
    run('''sed -i "6i storm.local.hostname: '192.168.1.176'" /home/123/Desktop/apache-storm-1.1.2/conf/storm.yaml''')


@roles('supervisor01')
def put_hostname_s1():
    run('''sed -i "6i storm.local.hostname: '192.168.1.178'" /home/123/Desktop/apache-storm-1.1.2/conf/storm.yaml''')


@roles('supervisor02')
def put_hostname_s2():
    run('''sed -i "6i storm.local.hostname: '192.168.1.181'" /home/123/Desktop/apache-storm-1.1.2/conf/storm.yaml''')


@roles('nimbus')
def start_n():
    run("$(nohup /home/123/Desktop/apache-storm-1.1.2/bin/storm ui >/dev/null 2>&1 &) && sleep 1")
    run("$(nohup /home/123/Desktop/apache-storm-1.1.2/bin/storm nimbus >/dev/null 2>&1 &) && sleep 1")


@roles('supervisor01')
def start_s1():
    run("$(nohup /home/123/Desktop/apache-storm-1.1.2/bin/storm supervisor >/dev/null 2>&1 &) && sleep 1")
    run("$(nohup /home/123/Desktop/apache-storm-1.1.2/bin/storm logviewer >/dev/null 2>&1 &) && sleep 1")


@roles('supervisor02')
def start_s2():
    run("$(nohup /home/123/Desktop/apache-storm-1.1.2/bin/storm supervisor >/dev/null 2>&1 &) && sleep 1")
    run("$(nohup /home/123/Desktop/apache-storm-1.1.2/bin/storm logviewer >/dev/null 2>&1 &) && sleep 1")


@roles('storm')
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
    execute(put_storm)
    execute(put_hostname_n)
    execute(put_hostname_s1)
    execute(put_hostname_s2)
    execute(ip_storm)
    execute(start_n)
    execute(start_s1)
    execute(start_s2)


@roles('storm')
def put_python3():
    put('/Users/zhangyu/Downloads/Python-3.6.6.tgz', '/home/123/Desktop/Python-3.6.6.tgz')
    with cd('/home/123/Desktop'):
        run('yum install zlib-devel bzip2-devel openssl-devel ncurese-devel gcc zlib sqlite-devel -y')
        run('tar zxvf Python-3.6.6.tgz')
        with cd('Python-3.6.6'):
            run('./configure --enable-loadable-sqlite-extensions --prefix=/usr/local/python3 && make && make install')

    run('ln -s /usr/local/python3/bin/python3 /usr/bin/python3')
    run('ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3')
    with cd('~/.config'):
        run('mkdir -p pip')
        put('/Users/zhangyu/PycharmProjects/fabric_test/pip.conf', '~/.config/pip/pip.conf')
    run('pip3 install virtualenv')
    run('''echo 'export PATH="$PATH:/usr/local/python3/bin"' >> /etc/profile''')
    run('source /etc/profile')


@roles('storm')
def update_glibc():
    put('/Users/zhangyu/Downloads/glibc-2.17.tar.gz', '/home/123/Desktop/glibc-2.17.tar.gz')
    with cd('/home/123/Desktop'):
        run('tar -xvf glibc-2.17.tar.gz')
        run('mkdir -p glibc_build_2.17')
        with cd('glibc_build_2.17'):
            run('../glibc-2.17/configure  --prefix=/usr --disable-profile --enable-add-ons --with-headers=/usr/include '
                '--with-binutils=/usr/bin && make && make install')


@roles('storm')
def glibc():
    run('strings /lib64/libc.so.6 | grep GLIBC')
    run('strings /usr/lib64/libstdc++.so.6 | grep GLIBCXX')


@roles('storm')
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

    put('/Users/zhangyu/Downloads/libstdc++.so.6.0.18', '/usr/lib64/libstdc++.so.6.0.18')
    with cd('/usr/lib64'):
        run('rm -rf libstdc++.so.6')
        run('ln -s libstdc++.so.6.0.18 libstdc++.so.6')


def task_env():
    execute(put_python3)
    execute(update_glibc)
    execute(update_gcc)
    execute(glibc)
    pass


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
    put('/Users/zhangyu/Downloads/lein', '~/bin/lein')
    run('mkdir -p ~/.lein/self-installs')
    put('/Users/zhangyu/Downloads/leiningen-2.8.1-standalone.jar',
        '~/.lein/self-installs/leiningen-2.8.1-standalone.jar')
    run('chmod a+x ~/bin/lein')
    # run('lein -v')

    execute(pip)
    execute(nimbus_pip)

    put('/Users/zhangyu/Developer/web_security/dpi_detection.zip', '~/Downloads/dpi_detection.zip')
    with cd('~/Downloads'):
        run('unzip dpi_detection.zip')
        with cd('dpi_detection'):
            run('sparse submit')


@roles('storm')
def pip():
    # 安装python3所需要的包
    put('/Users/zhangyu/PycharmProjects/fabric_test/requirements.txt', '/home/123/Desktop/requirements.txt')
    run('pip3 install --upgrade pip')
    run('source /etc/profile && virtualenv /data/virtualenvs/dpi_detection')
    put('/Users/zhangyu/Downloads/torch-0.4.1-cp36-cp36m-linux_x86_64.whl',
        '/home/123/Desktop/torch-0.4.1-cp36-cp36m-linux_x86_64.whl')
    run('source /data/virtualenvs/dpi_detection/bin/activate '
        '&& pip3 install /home/123/Desktop/torch-0.4.1-cp36-cp36m-linux_x86_64.whl '
        '&& pip3 install -r /home/123/Desktop/requirements.txt')
    run('mkdir -p /var/log/storm/streamparse')


@roles('nimbus')
def nimbus_pip():
    run('pip3 install --upgrade pip')
    run('pip3 install /home/123/Desktop/torch-0.4.1-cp36-cp36m-linux_x86_64.whl')
    run('pip3 install -r /home/123/Desktop/requirements.txt')
    # run('yum install git -y')
    # run("echo '192.168.1.100 gitlab' >> /etc/hosts")


def task_project():
    execute(start_project)


def task():
    execute(task_zkp)
    execute(task_storm)
    execute(task_env)
    execute(task_project)
