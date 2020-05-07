# Nextcloud

- apache2 + php7.0
- memcached 加速

## 启动文件

```yaml
nextcloud:
    image: skywind3000/nextcloud:default
    restart: always
    ports:
        - 8543:443
    volumes:
        - ./data:/var/www/nextcloud/data
        - ./config:/var/www/nextcloud/config
```

## 安装步骤

启动镜像：

```bash
docker-compose up -d
```

访问网络： https://www.example.com/ 并初始化管理员和数据库。

## 修改配置

编辑 `config/config.php`，保证有下面两行（注意 `overwrite.cli.url` 后面要有斜杆）：

```php
'overwrite.cli.url' => 'https://www.example.com/',
'htaccess.RewriteBase' => '/',  
```

然后重启容器会自动生成 `.htaccess` 保证 url 重定向。

## 增加缓存

容器内自带 memcached 服务，需要修改 `config/config.php`，增加相关配置：

```php
  'memcache.local' => '\OC\Memcache\APCu',
  'memcache.distributed' => '\OC\Memcache\Memcached',
  'memcached_servers' => array( array('localhost', 11211),), 
```

重启容器即可。

