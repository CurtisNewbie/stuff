# Register mirror for docker hub

File location: `/etc/docker/daemon.json`

Content:

```
{
    "registry-mirrors" : ["https://registry.docker-cn.com"]
}
```

Restart docker

```sudo systemctl restart docker```
