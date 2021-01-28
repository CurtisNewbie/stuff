# Register mirror for docker hub

File location: `/etc/docker/daemon.json`

Content:

```
{
    "registry-mirrors" : ["https://registry.docker-cn.com", "https://docker.mirrors.ustc.edu.cn/", "https://hub-mirror.c.163.com/" ]
}
```

Restart docker

```sudo systemctl restart docker```
