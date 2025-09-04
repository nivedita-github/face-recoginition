FROM python:3.8
RUN apt update && apt install -y libgl1-mesa-glx cmake
RUN pip install --no-cache-dir dlib
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
