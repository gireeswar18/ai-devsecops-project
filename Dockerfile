FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Train the model at build time so the container is self-contained.
# If trained_model.pkl was already committed to the repo it is already
# present and these steps are harmless (they just overwrite it).
RUN mkdir -p data && \
    python generate_dataset.py && \
    python feature_engineering.py && \
    python train_model.py

EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]