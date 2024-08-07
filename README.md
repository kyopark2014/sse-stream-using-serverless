# SSE를 이용한 Streaming Chatbot (Serverless로 구현하다가 실패)


## 구현 이슈

RESTful API Gateway에서 설정할 수 있는 최대 timeout이 30초이므로, SSE를 이용해 stream으로 서비스가 어려운것으로 보여집니다. [관련링크](https://stackoverflow.com/questions/76139485/how-to-support-sse-with-api-gateway-in-aws-while-maintaining-an-external-authent)

관련 에러 메시지는 아래와 같습니다.

![image](https://github.com/kyopark2014/streaming-chatbot-using-sse/assets/52392004/ebf249f9-99f8-4fc3-9ae3-71245d05d040)

SSE의 경우에 세션이 계속 유지 되어야 하므로 서버리스보다는 ECS/EKS, EC2의 구조에 적절할것으로 보여집니다. 

## Architecture 

전체적인 Architecture는 아래와 같습니다. (API Gateway으로 SSE를 지원할 수 없음이 확인되어 현 상태에서 구현을 중지합니다.)

<img src="https://github.com/kyopark2014/streaming-chatbot-using-sse/assets/52392004/54a73196-dc68-4e24-8652-c0fdd6844f5b" width="800">

## SSE (Server-Sent-Events)

### WebSocket과 비교

- Websocket은 양방향세션을 생성하고, SSE는 server to client로만 메시지를 전송합니다. 즉, 클라이언트는 수신만 가능합니다.
- 일반적인 HTTP는 server에서 응답을 전송하고 TCP를 disconnection 하지만 content-type을 text/event-stream로 등록하면, disconnection을 수행하지 않습니다.
- SSE의 경우에 Cache-Control은 no-cache로 설정합니다.
- SSE는 GET method만 허용합니다.
- SSE는 연결이 끊어질때 자동으로 재연결을 하므로 편리합니다. (Websocket은 세션관리를 직접 수행)

<img src="https://github.com/kyopark2014/streaming-chatbot-using-sse/assets/52392004/f7a2c834-d11c-44ed-9f87-36e8b6afd864" width="400">


### Load balancing

- SSE의 경우에 HTTP GET을 사용하므로 N개의 Server가 Load balancer를 이용해 서비스 된다면, Client의 요청은 N개의 server중에 하나에 전달되게 됩니다.
- SSE의 경우에 HTTP 세션이 유지되므로, client와 server는 항상 매칭되어야 합니다. 또한, server는 chat history를 가지고 있으므로, 매번 다른 server로 request가 전달된다면, 일관된 history를 유지할 수 없습니다. (WebSocket API Gateway는 세션이 유지되는 동안에 항상 같은 server로 client의 요청을 전달됩니다.)
- SSE에서는 HTTP 세션을 유지하기 위하여 아래 방법을 이용할 수 있습니다.

1) pubsub server를 이용하여 HTTP GET 요청을 subscribe 하고 있는 server들에게 요청을 전달하고, 현재 open된 연결을 가진 server에서 응답하도록 합니다.
   
2) ALB의 sticky session을 이용해 항상 같은 server로 연결할 수 있습니다. [Server-Sent events in scalable backend](https://stackoverflow.com/questions/30458969/server-sent-events-in-scalable-backend)

여기서는 pubsub을 이용하여 구현하는 방법을 활용하고자 합니다. 

## 구현 방안

user-id를 key로하는 pubsub을 통해 SSE 세션을 가지고 있는 lambda(chat)에 질문을 전달합니다. 상세한 call flow는 아래를 참조합니다.

<img src="https://github.com/kyopark2014/sse-stream-using-serverless/assets/52392004/e9c67e00-d04c-4eb4-8e93-55f2794de89e" width="600">


1) Client에서 SSE 세션을 연결하기 위해 '/chat'으로 connect를 요청하면, lambda(chat)은 session-id를 생성하여 SSE로 client에 전달합니다. 또한, lambda(chat)은 session-id를 key로 Redis를 subscribe 합니다.
2) 사용자가 질문을 하면, Client는 '/redis'를 이용하여 질문(question)을 전달합니다. lambda(redis)가 질문을 받아서 Redis에 publish 합니다.
3) Redis를 통해 질문이 lambda(chat)에 전달됩니다.
4) lambda(chat)은 LLM에 질문을 전달합여 답변(answer)를 얻습니다.
5) LLM의 answer는 SSE를 이용해 stream 방식으로 Client에 전달합니다.



### 필요한 패키지

mangum: API를 핸들러로 래핑할 수 있게 해주며, 이를 AWS Lambda 함수로 패키징하고 배포할 수 있습니다. 

AWS API Gateway를 사용하여 모든 수신 요청을 라우팅하여 Lambda를 호출하고 애플리케이션 내부에서 라우팅을 처리할 수 있습니다. 

ASGI(Asynchronous Server Gateway Interface)



## 결론

- SSE로 구현시 단순하고 쉽게 구현가능하지만, Scale 고려시 pubsub을 위한 Redis를 구성하여야 합니다.
- WebSocket는 세션관리에 대한 부담등의 이슈가 있고, WebSocket용 API Gateway를 써야하지만 Redis가 불필요합니다.
- SSE의 경우에 API Gateway은 미지원하므로, ALB/NLB를 적용해야 할 것으로 보여집니다.


### SSE 방식에 대한 검토

[Stream Responses from OpenAI API with Python: A Step-by-Step Guide](https://www.codingthesmartway.com/stream-responses-from-openai-api-with-python/)와 같이 OpenAPI의 인터페이스는 HTTP Post로 질문을 보내고 Answer를 SSE로 받는 구조입니다.

```python
def performRequestWithStreaming():
    reqUrl = 'https://api.openai.com/v1/completions'
    reqHeaders = {
        'Accept': 'text/event-stream',
        'Authorization': 'Bearer ' + API_KEY
    }
    reqBody = {
      "model": "text-davinci-003",
      "prompt": "What is Python?",
      "max_tokens": 100,
      "temperature": 0,
      "stream": True,
    }
    request = requests.post(reqUrl, stream=True, headers=reqHeaders, json=reqBody)
    client = sseclient.SSEClient(request)
    for event in client.events():
        if event.data != '[DONE]':
            print(json.loads(event.data)['choices'][0]['text'], end="", flush=True),
```

LangChain의 경우에는 invoke()하면 stream으로 content를 받는 방식입니다. 

```python
def general_conversation(requestId, chat, query):
    system = (
            "다음의 Human과 Assistant의 친근한 이전 대화입니다. Assistant은 상황에 맞는 구체적인 세부 정보를 충분히 제공합니다. Assistant의 이름은 서연이고, 모르는 질문을 받으면 솔직히 모른다고 말합니다."
        )    
    human = "{input}"    
    prompt = ChatPromptTemplate.from_messages([("system", system), MessagesPlaceholder(variable_name="history"), ("human", human)])    
    history = memory_chain.load_memory_variables({})["chat_history"]
                
    chain = prompt | chat    
    try: 
        isTyping(requestId)  
        stream = chain.invoke(
            {
                "history": history,
                "input": query,
            }
        )        
        for event in stream.content:
            print('event', event)
```

따라서, LangChain을 쓰면서 SSE 방식으로 Web Interface를 쓰려는것은 Layer가 다르다고 보여집니다. 


## Reference 

[FastAPI with streaming data and Materialize](https://devdojo.com/bobbyiliev/how-to-use-server-sent-events-sse-with-fastapi): PUBSUB


[Deploy an ML serverless inference endpoint using FastAPI, AWS Lambda and AWS CDK](https://github.com/aws-samples/lambda-serverless-inference-fastapi/tree/main)

[Data Streams with Server-Sent Events](https://bytewax.io/blog/data-stream-server-sent-events)

[How to use server-sent events (SSE) with FastAPI?](https://devdojo.com/bobbyiliev/how-to-use-server-sent-events-sse-with-fastapi)

[Server Sent Events](https://ko.javascript.info/server-sent-events)

[Bedrock Access Gateway](https://github.com/aws-samples/bedrock-access-gateway): ALB 이용

[streaming response from Amazon Bedrock with FastAPI](https://github.com/awslabs/aws-lambda-web-adapter/tree/main/examples/fastapi-response-streaming): PUBSUB (Our event source server will be a publisher and FastAPI app will be subscriber. Publishers send messages to channels, while subscribers listen to specific channels for messages.)

[Realtime Log Streaming with FastAPI and Server-Sent Events](https://amittallapragada.github.io/docker/fastapi/python/2020/12/23/server-side-events.html): FAST API 구현 사례

[Server-Sent Events in FastAPI using Redis Pub/Sub](https://medium.com/deepdesk/server-sent-events-in-fastapi-using-redis-pub-sub-eba1dbfe8031): PUBSUB 사용

[How to Stream JSON Data Using Server-Sent Events and FastAPI in Python over HTTP?](https://www.workfall.com/learning/blog/how-to-stream-json-data-using-server-sent-events-and-fastapi-in-python-over-http/): Kafka

[Server-Sent Events(SSE), Redis pub/sub, Kafka로 알림 기능 개선하기](https://velog.io/@xogml951/Server-Sent-EventsSSE-Redis-pubsub-Kafka%EB%A1%9C-%EC%95%8C%EB%A6%BC-%EA%B8%B0%EB%8A%A5-%EA%B0%9C%EC%84%A0%ED%95%98%EA%B8%B0): Redis PUBSUB
  

[What are SSE (Server-Sent Events) and how do they work?](https://bunny.net/academy/http/what-is-sse-server-sent-events-and-how-do-they-work/)

[Redis Pub/Sub 기반 SSE(Server-Sent Events) 실시간 알림 적용기](https://velog.io/@wwlee94/Redis-PubSub-Base-Server-Sent-Event)

[Stream Responses from OpenAI API with Python: A Step-by-Step Guide](https://www.codingthesmartway.com/stream-responses-from-openai-api-with-python/)


[Real-Time Communication with SSE in FastAPI: Enhancing Task Processing Efficiency](https://princyprakash.medium.com/real-time-communication-with-sse-in-fastapi-enhancing-task-processing-efficiency-bc8ba9b3c29f)

[Sever Sent Event(SSE) 사용하기](https://blog.naver.com/pjt3591oo/223274970013)


