// import express from 'express';
// import { resolve } from 'node:path';
// import { fileURLToPath } from 'url';
// import { dirname } from 'path';
// import cors from 'cors';
// import { registerRoute } from './api/db/register'; // Adjust the path as needed
// import { testRoute } from './api/db/testApi';
// import { connectToDatabase } from './server/services/DBService2'; // Corrected import

// // Import Angular Universal and Angular App Engine APIs
// import {
//   AngularNodeAppEngine,
//   createNodeRequestHandler,
//   isMainModule,
//   writeResponseToNodeResponse,
// } from '@angular/ssr/node';

// require('dotenv').config();

// // Define __dirname for ES modules
// const __filename = fileURLToPath(import.meta.url);
// const __dirname = dirname(__filename);

// const serverDistFolder = dirname(fileURLToPath(import.meta.url));
// const browserDistFolder = resolve(serverDistFolder, '../browser');

// const app = express();
// const angularApp = new AngularNodeAppEngine();

// app.use(cors({
//   origin: 'http://localhost:4200', // Replace with your Angular app's URL
//   methods: 'GET,POST,PUT,DELETE',
//   allowedHeaders: 'Content-Type,Authorization'
// }));

// app.use(express.json());

// // // Use API Routes
// // testRoute(app);
// // registerRoute(app);

// // Serve static files from /browser
// app.use(
//   express.static(browserDistFolder, {
//     maxAge: '1y',
//     index: false,
//     redirect: false,
//   }),
// );

// // Handle all other requests by rendering the Angular application.
// app.use('/**', (req, res, next) => {
//   angularApp
//     .handle(req)
//     .then((response) =>
//       response ? writeResponseToNodeResponse(response, res) : next(),
//     )
//     .catch(next);
// });

// // Start the server if this module is the main entry point.
// if (isMainModule(import.meta.url)) {
//   const port = process.env['PORT'] || 4000;
//   app.listen(port, async () => {
//     try {
//       await connectToDatabase(); // Connect to the database when the server starts
//       console.log(`Node Express server listening on http://localhost:${port}`);
//     } catch (err) {
//       console.error('Failed to connect to the database:', err);
//     }
//   });
// }

// // The request handler used by the Angular CLI (dev-server and during build).
// export const reqHandler = createNodeRequestHandler(app);


import {
  AngularNodeAppEngine,
  createNodeRequestHandler,
  isMainModule,
  writeResponseToNodeResponse,
} from '@angular/ssr/node';
import express from 'express';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const serverDistFolder = dirname(fileURLToPath(import.meta.url));
const browserDistFolder = resolve(serverDistFolder, '../browser');

const app = express();
const angularApp = new AngularNodeAppEngine();

/**
 * Example Express Rest API endpoints can be defined here.
 * Uncomment and define endpoints as necessary.
 *
 * Example:
 * ```ts
 * app.get('/api/**', (req, res) => {
 *   // Handle API request
 * });
 * ```
 */

/**
 * Serve static files from /browser
 */
app.use(
  express.static(browserDistFolder, {
    maxAge: '1y',
    index: false,
    redirect: false,
  }),
);

/**
 * Handle all other requests by rendering the Angular application.
 */
app.use('/**', (req, res, next) => {
  angularApp
    .handle(req)
    .then((response) =>
      response ? writeResponseToNodeResponse(response, res) : next(),
    )
    .catch(next);
});

/**
 * Start the server if this module is the main entry point.
 * The server listens on the port defined by the `PORT` environment variable, or defaults to 4000.
 */
if (isMainModule(import.meta.url)) {
  const port = process.env['PORT'] || 4000;
  app.listen(port, () => {
    console.log(`Node Express server listening on http://localhost:${port}`);
  });
}

/**
 * The request handler used by the Angular CLI (dev-server and during build).
 */
export const reqHandler = createNodeRequestHandler(app);





// import {
//   AngularNodeAppEngine,
//   createNodeRequestHandler,
//   isMainModule,
//   writeResponseToNodeResponse,
// } from '@angular/ssr/node';
// import express from 'express';
// import { resolve } from 'node:path';
// import { fileURLToPath } from 'url';
// import { dirname } from 'path';
// import cors from 'cors';
// import { registerRoute } from '../src/api/db/register'; // Adjust the path as needed
// import { testRoute } from '../src/api/db/testApi'
// import { connectToDatabase } from '../src/server/services/DBService2'

// require('dotenv').config();

// // Define __dirname for ES modules
// const __filename = fileURLToPath(import.meta.url);
// const __dirname = dirname(__filename);

// const serverDistFolder = dirname(fileURLToPath(import.meta.url));
// const browserDistFolder = resolve(serverDistFolder, '../browser');

// const app = express();
// const angularApp = new AngularNodeAppEngine();

// app.use(cors({
//   origin: 'http://localhost:4200', // Replace with your Angular app's URL
//   methods: 'GET,POST,PUT,DELETE',
//   allowedHeaders: 'Content-Type,Authorization'
// }));

// app.use(express.json());
// // app.use('/api', registerRouter); // Use the registration router
// // const port = 5000;


// // Use API Routes
// testRoute(app);
// registerRoute(app);


// // app.listen(port, () => {
// //     console.log(`Server is running on http://localhost:${port}`);
// // });


// /**
//  * Serve static files from /browser
//  */
// app.use(
//   express.static(browserDistFolder, {
//     maxAge: '1y',
//     index: false,
//     redirect: false,
//   }),
// );

// /**
//  * Handle all other requests by rendering the Angular application.
//  */
// app.use('/**', (req, res, next) => {
//   angularApp
//     .handle(req)
//     .then((response) =>
//       response ? writeResponseToNodeResponse(response, res) : next(),
//     )
//     .catch(next);
// });

// /**
//  * Start the server if this module is the main entry point.
//  * The server listens on the port defined by the `PORT` environment variable, or defaults to 4000.
//  */
// // if (isMainModule(import.meta.url)) {
// //   const port = process.env['PORT'] || 4000;
// //   app.listen(port, () => {
// //     console.log(`Node Express server listening on http://localhost:${port}`);
// //   });
// // }

// // Start the server if this module is the main entry point.
// if (isMainModule(import.meta.url)) {
//   const port = process.env['PORT'] || 4000;
//   app.listen(port, async () => {
//     try {
//       // await connectToDatabase(); // Connect to the database when the server starts
//       console.log(`Node Express server listening on http://localhost:${port}`);
//     } catch (err) {
//       console.error('Failed to connect to the database:', err);
//     }
//   });
// }




// /**
//  * The request handler used by the Angular CLI (dev-server and during build).
//  */
// export const reqHandler = createNodeRequestHandler(app);