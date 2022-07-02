FROM python:3.7-buster
RUN /bin/bash -c "apt-get install libcurl4-openssl-dev libssl-dev"
# RUN /bin/bash -c "apt-get upgrade -yy && apt-get update -yy"


WORKDIR /app
ARG root_dir=/home/davide/Projects/BeeLurer/
COPY requirements.txt requirements.txt
RUN python3.7 -m pip install -r requirements.txt


COPY src/* ./
# CMD ["/bin/bash"]
# CMD python3.7 main.py