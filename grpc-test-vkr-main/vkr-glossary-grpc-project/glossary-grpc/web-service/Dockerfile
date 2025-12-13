FROM python

RUN mkdir /service
COPY web-service/protobufs/ /service/protobufs/
COPY web-service/ /service/web-service/
WORKDIR /service/web-service
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
           --grpc_python_out=. ../protobufs/glossary.proto

EXPOSE 8000
ENTRYPOINT [ "uvicorn", "web:app", "--host", "0.0.0.0", "--port", "8000" ]

