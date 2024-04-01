# async-stuff

- https://medium.com/@chenymj23/diving-into-golang-how-does-it-effectively-wrap-the-functionality-of-epoll-26065f0654ba
- https://gist.github.com/Lisprez/7b52f4a55cd0fcf96324b5f02b865e54#file-epoll-go-L17

## multiplexing over tcp

- https://github.com/hashicorp/yamux/tree/master

Essentially wraping the tcp payload with extra session id, such that both end recognises the session that the messages belong to. And then we can have multiple sessions operate over the same tcp connection.

## Other Stuff

- https://github.com/antirez/smallchat/tree/main