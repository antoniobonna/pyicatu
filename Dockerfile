FROM quay.io/astronomer/astro-runtime:12.7.1

# Install PostgreSQL development libraries
USER root
RUN apt-get update && \
    apt-get install -y libpq-dev gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Switch back to astronomer user
USER astro