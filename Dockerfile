FROM python:3.8-alpine
COPY ./ /workspace/IMAG_Internal/
WORKDIR /workspace/IMAG_Internal/
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
EXPOSE 5000
CMD [ "python", "main.py" ]