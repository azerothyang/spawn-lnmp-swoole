#!/usr/bin/python
# coding:utf-8

import os
import sys

mongodbVersion = "mongodb-1.4.4"
phpRedisVersion = "redis-4.0.2"
phpVersion = "php-7.3.4"
phpSubVersion = "php-5.6.30"
swooleVersion = "swoole-4.3.2"
swooleSubVersion = "swoole-1.10.1"
freetypeVersion = "freetype-2.9"
inotifyVersion = "inotify-2.0.0"

#目前phpmemcache 没有加Simple Authentication and Security Layer
phpMemcached = "memcached-3.0.4.tgz"
libMemcached = "libmemcached-1.0.18"


# 先判断是否为root用户
if os.getuid() == 0:
    pass
else:
    print('当前用户不是root用户, 请以root用户执行脚本')
    sys.exit(1)

# yum源初始化
cmd = "wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && rpm -ivh epel-release-latest-7.noarch.rpm && yum clean all && yum -y update"
os.system(cmd)

# 先安装php需要的依赖
cmd = "yum -y install gcc gcc-c++ libmcrypt libmcrypt-devel autoconf freetype gd jpegsrc libmcrypt libpng libpng-devel libjpeg libxml2 libxml2-devel zlib curl curl-devel openssl* libxml2 libxml2-devel openssl openssl-devel bzip2 bzip2-devel libcurl libcurl-devel libjpeg libjpeg-devel libpng libpng-devel freetype freetype-devel gmp gmp-devel libmcrypt libmcrypt-devel readline readline-devel libxslt libxslt-devel"
res = os.system(cmd)
if res != 0:
    print('yum命令缺失, 请检查')
    sys.exit(1)

# 确定php版本
version = raw_input('请输入您想安装的php版本(' + phpVersion + '/' + phpSubVersion + ') \n')
if version != phpSubVersion:
    version = phpVersion
    url = 'http://cn2.php.net/distributions/' + phpVersion + '.tar.gz'
else:
    url = 'http://cn2.php.net/distributions/' + phpSubVersion + '.tar.gz'

# 下载源码包, 先删除所有python先关的文件
os.system('rm -rf php*')

cmd = 'wget ' + url
res = os.system(cmd)
# 下载失败
if res != 0:
    print('下载失败, 请检查当前网络, 或者重新运行脚本')
    sys.exit(1)

# 解压源码包
packageName = version + '.tar.gz'
cmd = 'tar -zxvf ' + packageName
res = os.system(cmd)
if res != 0:
    print('php源码包, 解压失败, 请重新运行此脚本下载源码包')
    sys.exit(1)

# 编译安装php
cmd = 'cd ' + version + \
      ' && ./configure --prefix=/usr/local/' + version + ' --with-mysql-sock=/var/run/mysql/mysql.sock --with-mhash --with-openssl --with-mysqli=mysqlnd --with-pdo-mysql=mysqlnd --with-iconv --with-zlib --enable-zip --enable-inline-optimization --disable-fileinfo --enable-shared --enable-bcmath --enable-shmop --enable-sysvsem --enable-mbregex --enable-mbstring --enable-ftp --enable-pcntl --enable-sockets --with-xmlrpc --enable-soap --with-gettext --enable-session --with-curl --enable-opcache --enable-fpm --with-config-file-path=/usr/local/' + version + '/etc/ && make && make install'
res = os.system(cmd)

if res != 0:
    print('编译安装php源码失败, 请检查是否缺少依赖库')
    sys.exit(1)
# 生成php配置文件
question = raw_input('请选择您想要生成的php初始化配置文件, 默认为生成环境。 请填写 prod 或者 dev \n')
if question == 'dev':
    cmd = 'cd ' + version + '&& cp php.ini-development /usr/local/' + version + '/etc/php.ini'
else:
    cmd = 'cd ' + version + '&& cp php.ini-production /usr/local/' + version + '/etc/php.ini'
os.system(cmd)

#复制php命令到主命令

res = raw_input('php命令是否设置为全局?y/n \n')
if res != 'n':
    os.system("ln -s /usr/local/" + version + "/bin/php /usr/local/bin")
    os.system("ln -s /usr/local/" + version + "/bin/php-config /usr/local/bin")
    os.system("ln -s /usr/local/" + version + "/bin/phpize /usr/local/bin")

question = raw_input('是否需要为您启动php-fpm, 默认启动? 请填写 y/n \n')
if question == 'n':
    pass
else:
    os.system('cp /usr/local/' + version + '/etc/php-fpm.conf.default /usr/local/' + version + '/etc/php-fpm.conf')
    res = os.system(
        'cp /usr/local/' + version + '/etc/php-fpm.d/www.conf.default /usr/local/' + version + '/etc/php-fpm.d/www.conf && /usr/local/' + version + '/sbin/php-fpm -D')
    if res != 0:
        print('php-fpm启动失败')
    else:
        print('php-fpm启动成功')
        
# 安装php各项扩展

# gd
question = raw_input('是否需要为您安装gd扩展? 请填写 y/n \n')
if question == 'n':
    cmd = 0
    pass
else:
    #首先下载安装freetype
    cmd = 'wget https://download.savannah.gnu.org/releases/freetype/' + freetypeVersion + '.tar.gz && tar -zxvf ' + freetypeVersion + '.tar.gz'
    os.system(cmd)
    cmd = 'cd ' + freetypeVersion + ' && ./configure --prefix=/usr/local/freetype/ ' + freetypeVersion + ' && make && make install'
    os.system(cmd)
    #安装gd 支持freetype
    cmd = 'cd ' + version + '/ext/gd && /usr/local/' + version + '/bin/phpize && ./configure --with-php-config=/usr/local/' + version + '/bin/php-config --with-freetype-dir=/usr/local/freetype/' + freetypeVersion + ' && make && make install'
    res = os.system(cmd)
    # 安装php的gd扩展
    if res == 0:
        document = open('/usr/local/' + version + '/etc/php.ini', 'a')
        document.write('extension=gd.so\n')
        document.close()
        print('gd扩展安装成功')
    else:
        print('gd扩展安装失败')

# redis
question = raw_input('是否需要为您安装php-redis扩展? 请填写 y/n \n')
if question == 'n':
    cmd = 0
    pass
else:
    cmd = 'wget http://pecl.php.net/get/' + phpRedisVersion + '.tgz'
if cmd != 0:
    os.system(cmd)
    os.system('tar -zxvf ' + phpRedisVersion + '.tgz')
    os.system('cd ' + phpRedisVersion + ' && /usr/local/' + version + '/bin/phpize')
    res = os.system('cd ' + phpRedisVersion + ' && ./configure --with-php-config=/usr/local/' + version + '/bin/php-config && make && make install')
    # 启动php的redis扩展
    if res == 0:
        document = open('/usr/local/' + version + '/etc/php.ini', 'a')
        document.write('extension=redis.so\n')
        document.close()
        print('php-redis扩展安装成功')
    else:
        print('php-redis扩展安装失败')



# memcached
question = raw_input('是否需要为您安装memcached? 请填写 y/n \n')
if question == 'n':
    cmd = 0
    pass
else:
    cmd = "yum -y install memcached"
    res = os.system(cmd)
    cmd = "systemctl start memcached"
    res = os.system(cmd)
    # memcached
    if res == 0:
        print('memcached启动成功')
    else:
        print('memcached启动失败')


# php-memcached
question = raw_input('是否需要为您安装php-memcached扩展? 请填写 y/n \n')
if question == 'n':
    cmd = 0
    pass
else:
    #安装libmemcached 作为 php连接memcached的因爱
    cmd = "wget https://launchpad.net/libmemcached/1.0/1.0.18/+download/" + libMemcached + ".tar.gz"
    res = os.system(cmd)
    cmd = "tar -zxvf " + libMemcached + ".tar.gz"
    os.system(cmd)
    cmd = "cd " + libMemcached + " && ./configure --prefix=/usr/local/libmemcached --with-memcached && make && make install"
    os.system(cmd)

    #安装php-memcached依赖
    cmd = 'wget http://pecl.php.net/get/' + phpMemcached + '.tgz'
    res = os.system(cmd)
    cmd = "tar -zxvf " + phpMemcached + ".tar.gz"
    os.system(cmd)
    os.system('cd ' + phpMemcached + ' && /usr/local/' + version + '/bin/phpize')
    res = os.system(
        'cd ' + phpMemcached + ' && ./configure --disable-memcached-sasl --with-libmemcached-dir=/usr/local/libmemcached --with-php-config=/usr/local/' + version + '/bin/php-config && make && make install')
    # 启动php的memcached.so扩展
    if res == 0:
        document = open('/usr/local/' + version + '/etc/php.ini', 'a')
        document.write('extension=memcached.so\n')
        document.close()
        print('php-memcached扩展安装成功')
    else:
        print('php-memcached扩展安装失败')



# swoole
question = raw_input('是否需要为您安装swoole扩展? 请填写 y/n \n')
if question == 'n':
    cmd = 0
    pass
else:
    swVerion = raw_input('请选择需要安装的swoole版本, (' + swooleVersion + '/' + swooleSubVersion + ') \n')
    if swVerion != swooleSubVersion:
        swVerion = swooleVersion
    cmd = 'wget http://pecl.php.net/get/' + swVerion + '.tgz'
    os.system(cmd)
    res = os.system('tar -zxvf ' + swVerion + '.tgz && cd ' + swVerion + ' && /usr/local/' + version + '/bin/phpize && ./configure --enable-sockets --enable-openssl --enable-mysqlnd --enable-async-mysql'
                    ' --with-php-config=/usr/local/' + version + '/bin/php-config && make && make install')

    # 启动php的swoole扩展
    if res == 0:
        document = open('/usr/local/' + version + '/etc/php.ini', 'a')
        document.write('extension=swoole.so\n')
        document.close()
        print('swoole扩展安装成功')
    else:
        print('swoole扩展安装失败')

# mongodb
question = raw_input('是否需要为您安装php-mongodb扩展? 请填写 y/n \n')
if question == 'n':
    cmd = 0
    pass
else:
    cmd = 'wget http://pecl.php.net/get/' + mongodbVersion + '.tgz'
if cmd != 0:
    os.system(cmd)
    os.system('tar -zxvf ' + mongodbVersion + '.tgz')
    res = os.system('cd ' + mongodbVersion + ' && /usr/local/' + version + '/bin/phpize && ./configure --with-php-config=/usr/local/' + version + '/bin/php-config && make && make install')

    # 启动php的mongodb扩展
    if res == 0:
        document = open('/usr/local/' + version + '/etc/php.ini', 'a')
        document.write('extension=mongodb.so\n')
        document.close()
        print('php-mongodb扩展安装成功')
    else:
        print('php-mongodb扩展安装失败')
# mongodb

# inotify扩展
question = raw_input('是否需要为您安装php-inotify扩展? 请填写 y/n \n')
if question == 'n':
    cmd = 0
    pass
else:
    cmd = 'wget http://pecl.php.net/get/' + inotifyVersion + '.tgz'
if cmd != 0:
    os.system(cmd)
    os.system('tar -zxvf ' + inotifyVersion + '.tgz')
    res = os.system('cd ' + inotifyVersion + ' && /usr/local/' + version + '/bin/phpize && ./configure --with-php-config=/usr/local/' + version + '/bin/php-config && make && make install')

    # 启动php的mongodb扩展
    if res == 0:
        document = open('/usr/local/' + version + '/etc/php.ini', 'a')
        document.write('extension=inotify.so\n')
        document.close()
        print('php-inotify扩展安装成功')
    else:
        print('php-inotify扩展安装失败')
# inotify

question = raw_input('是否需要为您打开opcache? 请填写 y/n \n')
if question == 'n':
    cmd = 0
    pass
else:
    cmd = 1
if cmd != 0:
    # 启动php的mongodb扩展
    document = open('/usr/local/' + version + '/etc/php.ini', 'a')
    document.write('zend_extension=opcache.so\n'
                   'opcache.enable=1\n'
                   'opcache.enable_cli=1\n'
                   '\n')
    document.close()
    print('opcache打开完成')

# 安装nginx
question = raw_input('是否需要为您安装nginx? 请填写 y/n \n')
if question == 'n':
    pass
else:
    cmd = 'yum -y install nginx'
    res = os.system(cmd)
    if res != 0:
        print ('通过yum源安装nginx失败')
        sys.exit(1)
    else:
        # 启动nginx
        cmd = 'service nginx start'
        res = os.system(cmd)
        if res != 0:
            print ('nginx 启动失败')
        else:
            print('nginx 启动成功')
question = raw_input('需要为您安装redis服务器吗? y/n\n')
if question == 'n':
    pass
else:
    os.system('yum -y install redis')
    print ('redis 安装完毕')
    res = os.system('service redis start')
    if res != 0:
        print('redis 启动失败')
    else:
        print('redis 启动成功')
question = raw_input('需要为您关闭selinux吗? y/n\n')
if question == 'n':
    pass
else:
    os.system('setenforce 0')

question = raw_input('需要为您关闭防火墙吗? y/n\n')
if question == 'n':
    pass
else:
    os.system('systemctl stop firewalld.service')
    os.system('systemctl disable firewalld.service')
    os.system('service iptables stop')
    print ('防火墙已关闭')

print ('所有安装完成\n' 
      '如果您安装了memcached，您可以在/etc/sysconfig/memcached中找到memcached配置文件\n'   
      '如果您安装了nginx，您可以在/etc/nginx/下找到nginx配置文件\n' 
      'php为您安装在/usr/local/' + version + '/下,配置文件则在/usr/local/' + version + '/etc/目录下\n' 
      """    __                                                       __       __           
   / /_  ____ __   _____     ____ _   ____ _____  ____  ____/ /  ____/ /___ ___  __
  / __ \/ __ `/ | / / _ \   / __ `/  / __ `/ __ \/ __ \/ __  /  / __  / __ `/ / / /
 / / / / /_/ /| |/ /  __/  / /_/ /  / /_/ / /_/ / /_/ / /_/ /  / /_/ / /_/ / /_/ / 
/_/ /_/\__,_/ |___/\___/   \__,_/   \__, /\____/\____/\__,_/   \__,_/\__,_/\__, /  
                                   /____/                                 /____/   """)

