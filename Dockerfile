FROM python:3.10.13
WORKDIR /code
COPY requirements.txt /code
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install nltk && \
    mkdir ~/nltk_data && \
    python -c "import nltk; nltk.download(['punkt', 'stopwords'])"
COPY . /code/
CMD [ "python", "backend/main.py"]
