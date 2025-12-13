FROM python

RUN mkdir /service
COPY glossary-service/protobufs/ /service/protobufs/
COPY glossary-service/ /service/glossary-service/
WORKDIR /service/glossary-service
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
           --grpc_python_out=. ../protobufs/glossary.proto

EXPOSE 50052
ENTRYPOINT [ "python", "glossary.py" ]

