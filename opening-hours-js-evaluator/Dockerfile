FROM node:20

WORKDIR /usr/app

RUN npm install opening_hours express body-parser

COPY server.js server.js

# ENTRYPOINT ["node", "./evaluate_opening_hours.js"]
ENTRYPOINT ["node", "./server.js"]