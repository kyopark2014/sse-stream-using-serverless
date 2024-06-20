# SSE를 이용한 Streaming Chatbot

## SSE와 WebSocket 차이점

- Websocket은 양방향세션을 생성하고, SSE는 server to client로만 메시지를 전송합니다. 즉, 클라이언트는 수신만 가능합니다.
- 일반적인 HTTP는 서버에서 응답을 전송하고 TCP를 disconnection 하지만 content-type이 text/event-stream으로 등록하면, disconnection을 수행하지 않습니다.
- SSE의 경우에 Cache-Control은 no-cache로 설정합니다.
- SSE는 GET method만 허용합니다.
- SSE는 연결이 끊어질때 자동으로 재연결을 하므로 편리하다. (Websocket은 세션관리를 직접 해야 함)
- Keep alive 하지 않아도 되므로 불필요한 배터리 소모를 최소화합니다.

<img src="https://github.com/kyopark2014/streaming-chatbot-using-sse/assets/52392004/f7a2c834-d11c-44ed-9f87-36e8b6afd864" width="400">

## Issue: Load balancing

- SSE의 경우에 HTTP GET을 사용하므로 N개의 서버가 Load balancer를 통해 연결되어 있다면, 매번 Client의 요청은 N개의 서버중에 하나에 전달되게 됩니다. 
- 서버는 user의 요청이 올때, history를 가지고 있지 않다면, DynamoDB와 같은 데이터베이스에서 관련 history를 가져와서 chat에서 활용해야 합니다. 따라서 매번 다른 서버로 전달되면 chat history를 관리할 수 없습니다. (WebSocket도 첫 Request는 N개의 서버중 하나에 요청이 전달되지만, dedicated session 이용하므로 같은 문제가 발생하지 않음)
- 이를 위해 2가지 방법이 알려져 있는것으로 보엽니다. 1) pubsub 서버를 두어서 HTTP GET 요청을 subscribe 하고 있는 서버들에게 전달하면, 현재 open된 연결을 가진 서버에서 응답하는 방식 2) ALB의 sticky session을 이용해 항상 같은 서버로 연결하는 방식이 있습니다. [Server-Sent events in scalable backend](https://stackoverflow.com/questions/30458969/server-sent-events-in-scalable-backend)
- [Bedrock Access Gateway](https://github.com/aws-samples/bedrock-access-gateway): ALB 이용
- [streaming response from Amazon Bedrock with FastAPI](https://github.com/awslabs/aws-lambda-web-adapter/tree/main/examples/fastapi-response-streaming): PUBSUB (Our event source server will be a publisher and FastAPI app will be subscriber. Publishers send messages to channels, while subscribers listen to specific channels for messages.)
- [Realtime Log Streaming with FastAPI and Server-Sent Events](https://amittallapragada.github.io/docker/fastapi/python/2020/12/23/server-side-events.html): FAST API 구현 사례
- [Server-Sent Events in FastAPI using Redis Pub/Sub](https://medium.com/deepdesk/server-sent-events-in-fastapi-using-redis-pub-sub-eba1dbfe8031): PUBSUB 사용
- [How to Stream JSON Data Using Server-Sent Events and FastAPI in Python over HTTP?](https://www.workfall.com/learning/blog/how-to-stream-json-data-using-server-sent-events-and-fastapi-in-python-over-http/): Kafka
- [Server-Sent Events(SSE), Redis pub/sub, Kafka로 알림 기능 개선하기](https://velog.io/@xogml951/Server-Sent-EventsSSE-Redis-pubsub-Kafka%EB%A1%9C-%EC%95%8C%EB%A6%BC-%EA%B8%B0%EB%8A%A5-%EA%B0%9C%EC%84%A0%ED%95%98%EA%B8%B0): Redis PUBSUB
  
- [FastAPI with streaming data and Materialize](https://devdojo.com/bobbyiliev/how-to-use-server-sent-events-sse-with-fastapi): PUBSUB
- [What are SSE (Server-Sent Events) and how do they work?](https://bunny.net/academy/http/what-is-sse-server-sent-events-and-how-do-they-work/)
- [Redis Pub/Sub 기반 SSE(Server-Sent Events) 실시간 알림 적용기](https://velog.io/@wwlee94/Redis-PubSub-Base-Server-Sent-Event)

## 구현

### 필요한 패키지

mangum: API를 핸들러로 래핑할 수 있게 해주며, 이를 AWS Lambda 함수로 패키징하고 배포할 수 있습니다. 

AWS API Gateway를 사용하여 모든 수신 요청을 라우팅하여 Lambda를 호출하고 애플리케이션 내부에서 라우팅을 처리할 수 있습니다. 




## 결론
- SSE로 구현시 단순하고 쉽게 구현가능하지만, Scale 고려시 pubsub을 위한 Redis cluster를 구성하여야 합니다.
- WebSocket는 세션관리에 대한 부담등의 이슈가 있고, WebSocket용 API Gateway를 써야하지만 Redis가 불필요합니다.


## Reference 

[Deploy an ML serverless inference endpoint using FastAPI, AWS Lambda and AWS CDK](https://github.com/aws-samples/lambda-serverless-inference-fastapi/tree/main)

[Data Streams with Server-Sent Events](https://bytewax.io/blog/data-stream-server-sent-events)

[How to use server-sent events (SSE) with FastAPI?](https://devdojo.com/bobbyiliev/how-to-use-server-sent-events-sse-with-fastapi)

