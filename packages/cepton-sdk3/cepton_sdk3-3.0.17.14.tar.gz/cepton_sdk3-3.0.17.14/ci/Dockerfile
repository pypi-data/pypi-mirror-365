# Use official Python 3.12 base image
FROM python:3.12-slim


WORKDIR /app

COPY . .
RUN pip install --upgrade pip && pip install .

# Copy all calibration files from the mounted folder into the 
# sdk directory so it can find them.
COPY calibration_*.json /app/cepton_sdk3/lib/linux-x64/

CMD ["/bin/bash"]
