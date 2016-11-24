FROM tiangolo/uwsgi-nginx-flask:flask-python3.5

RUN pip install requests
RUN pip install pymongo


# Add app configuration to Nginx
COPY nginx.conf /etc/nginx/conf.d/

# Copy sample app
COPY ./app /app


