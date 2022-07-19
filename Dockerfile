FROM ubuntu:20.04


RUN apt-get update && apt-get install -y git zsh build-essential vim htop wget curl


RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    echo "export PATH=/opt/conda/bin:\$PATH" >> ~/.bashrc

COPY env.yml /qa_web/env.yml 
RUN /opt/conda/bin/conda env create  -f /qa_web/env.yml

COPY . /qa_web/
RUN cd /qa_web && /opt/conda/bin/conda run --no-capture-output -n qa_web python setup.py install
CMD /opt/conda/envs/qa_web/bin/python /qa_web/app.py