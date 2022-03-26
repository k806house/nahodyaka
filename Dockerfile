# FROM python:3.7-slim as watcher

# WORKDIR /workdir

# RUN apt-get update && apt-get install -y python3-opencv

# RUN pip3 install \
#     opencv-python==4.5.3.56 \
#     torch==1.9.0

# RUN pip3 install \
#     torchvision==0.10.0 \
#     pandas \
#     matplotlib \
#     seaborn \
#     pyyaml \
#     requests \
#     tqdm

# COPY models models
# COPY app app
# ENTRYPOINT [ "python3", "/workdir/app/camera/watcher.py" ]

FROM python:3.7-slim as storage

WORKDIR /workdir

RUN pip3 install flask numpy

COPY app app

ENTRYPOINT [ "python3", "/workdir/app/storage/server.py" ]


FROM python:3.7-slim as telegram-bot

WORKDIR /workdir

RUN pip3 install \
    tensorflow==2.6.0

RUN pip3 install \
    keras==2.6.0

RUN pip3 install \
    python-telegram-bot \
    python-dotenv \
    Pillow \
    numpy

COPY app app
COPY models models
COPY .env .env
COPY setup.py setup.py

RUN pip3 install .

ENTRYPOINT [ "python3", "/workdir/app/tg_bot/tg_bot.py" ]