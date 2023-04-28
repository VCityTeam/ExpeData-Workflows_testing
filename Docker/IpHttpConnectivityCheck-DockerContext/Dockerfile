# References
# - on chosing your Python base container
#   https://pythonspeed.com/articles/base-image-python-docker-images/
#   https://stackoverflow.com/questions/52740556/python-3-7-docker-images

FROM python:3.11

RUN pip install dnspython
COPY entrypoint.py /src/entrypoint.py
WORKDIR /src

ENTRYPOINT ["python", "entrypoint.py"] 
