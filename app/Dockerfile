FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app/

# Install Poetry
RUN pip3 install poetry
RUN poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=true
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

RUN pip3 install --force-reinstall httpcore==0.15

COPY . /app/
ENV PYTHONPATH=/app