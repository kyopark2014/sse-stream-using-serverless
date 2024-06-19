# SSE를 이용한 Streaming Chatbot

## SSE와 WebSocket 차이점

- Websocket은 양방향세션을 생성하고, SSE는 server to client로만 메시지를 전송합니다. 즉, 클라이언트는 수신만 가능합니다.
- 일반적인 HTTP는 서버에서 응답을 전송하고 TCP를 disconnection 하지만 content-type이 text/event-stream으로 등록하면, disconnection을 수행하지 않습니다.
- SSE의 경우에 Cache-Control은 no-cache로 설정합니다.
- SSE는 GET method만 허용합니다.

<img src="https://github.com/kyopark2014/streaming-chatbot-using-sse/assets/52392004/f7a2c834-d11c-44ed-9f87-36e8b6afd864" width="400">

## Issue: Load balancing

- SSE의 경우에 HTTP GET을 사용하므로 N개의 서버가 Load balancer를 통해 연결되어 있다면, 매번 Client의 요청은 N개의 서버중에 하나에 전달되게 됩니다.
- 서버는 user의 요청이 올때, history를 가지고 있지 않다면, DynamoDB와 같은 데이터베이스에서 관련 history를 가져와서 chat에서 활용해야 합니다. 따라서 매번 다른 서버로 전달되면 chat history를 관리할 수 없습니다.
- 이를 위해 2가지 방법이 알려져 있는것으로 보엽니다. 1) pubsub 서버를 두어서 HTTP GET 요청을 subscribe 하고 있는 서버들에게 전달하면, 현재 open된 연결을 가진 서버에서 응답하는 방식 2) ALB의 sticky session을 이용해 항상 같은 서버로 연결하는 방식이 있습니다. [Server-Sent events in scalable backend](https://stackoverflow.com/questions/30458969/server-sent-events-in-scalable-backend),
- [Bedrock Access Gateway](https://github.com/aws-samples/bedrock-access-gateway)
- [streaming response from Amazon Bedrock with FastAPI](https://github.com/awslabs/aws-lambda-web-adapter/tree/main/examples/fastapi-response-streaming) 

## Reference 

[Data Streams with Server-Sent Events](https://bytewax.io/blog/data-stream-server-sent-events)

[How to use server-sent events (SSE) with FastAPI?](https://devdojo.com/bobbyiliev/how-to-use-server-sent-events-sse-with-fastapi)

