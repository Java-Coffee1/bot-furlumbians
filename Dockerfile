# Use a base Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt (if you have one) and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the bot's files to the container
COPY . /app/

# Set environment variables for Discord bot token and other settings
ENV DISCORD_TOKEN=${TOKEN}
ENV SERVER_ID=${SERVER_ID}
ENV C_QOTD=${C_QOTD}
ENV QOTD_ROLE_NAME=${QOTD_ROLE_NAME}
ENV ADMIN_USER_ID=${ADMIN_USER_ID}
ENV ROLE_MENTION=${ROLE_MENTION}
ENV ROLE_IDV=${ROLE_IDV}

# Run the bot script when the container starts
CMD ["python", "Main.py"]