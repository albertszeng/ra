# Ra Frontend

## Getting Started

The front-end uses the `React` framework. 

- Install `npm` and `node` from https://nodejs.org/en/download/.
- Run `npm install` from this directory to install dependencies.
- Run `npm start` to run the frontend locally.

Note that by default, hot-reloading is available. The entry-point for the application is `index.tsx` so start there.

## Environment Variables
We use `REACT_APP_BACKEND` as an enviornment variable to read the backend to connect to when making game moves. If you wish to change this, the easiest way is to define a `.env` file within the `frontend/` directory and set the variable there:

```shell
# This will connect to the live production server.
REACT_APP_BACKEND=ra-server.fly.dev
```

Note that you should not use any protocol prefixes (eg, `https://`) and the path should terminate without a trailing `/`.

## Deployment

This is triggered on github. Backend is now https://ra-server.fly.dev/.