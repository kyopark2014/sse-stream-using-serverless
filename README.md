# SSE를 이용한 Streaming Chatbot

## SSE와 WebSocket 차이점

- Websocket은 양방향세션을 생성하고, SSE는 server to client로만 메시지를 전송합니다. 즉, 클라이언트는 수신만 가능합니다.
- 일반적인 HTTP는 서버에서 응답을 전송하고 TCP를 disconnection 하지만 content-type이 text/event-stream으로 등록하면, disconnection을 수행하지 않습니다.
- SSE의 경우에 Cache-Control은 no-cache로 설정합니다.
- SSE는 GET method만 허용합니다.

<img src="https://github.com/kyopark2014/streaming-chatbot-using-sse/assets/52392004/f7a2c834-d11c-44ed-9f87-36e8b6afd864" width="500">



## Reference 

[Data Streams with Server-Sent Events](https://bytewax.io/blog/data-stream-server-sent-events)

[How to use server-sent events (SSE) with FastAPI?](https://devdojo.com/bobbyiliev/how-to-use-server-sent-events-sse-with-fastapi)

