# GlitchyWeb

This project was generated using [Angular CLI](https://github.com/angular/angular-cli) version 19.0.1.

## Prerequisites

```
1. Download and install VSCode
2. Download and install latest version of NodeJS and NPM
4. Download and install following extensions on VSCode
    1. nodeJS
    2. Prettier ESLINT
    3. Standard JS - Javascript Standard Style
    4. Angular Schematics
```

## Installing Project

```
1. Download GlitchyWeb Locally
    Note: 
        Make sure that there is no node_modules or package-lock.json, in either the root or server directory.
        If these exists you will need to run the command below in the GlitchyWeb directory from a PowerShell terminal  
        as admin. 

        Remove-Item -Recurse -Force .\node_modules, .\package-lock.json

        Remove-Item -Recurse -Force .\server\node_modules, .\server\package-lock.json

2. cd  to "GlitchyWeb" in terminal
    
    Run: npm install 

3. cd to "GlitchyWeb\server"  in terminal

    Run: npm install 
```


## Running Project

To run GlitchyWeb Locally, follow the steps below. You'll need two instances of terminal open, 
one for each command below. 


```
1. First terminal, cd /GlitchyWeb
    Run:  npx ng serve
2. Second terminal, cd /GlitchyWeb/server
    Run: node server.js
```

Once the server is running, open your browser and navigate to `http://localhost:4200/`. The application will automatically reload whenever you modify any of the source files.

## Code scaffolding

Angular CLI includes powerful code scaffolding tools. To generate a new component, run:

```bash
ng generate component component-name
```

For a complete list of available schematics (such as `components`, `directives`, or `pipes`), run:

```bash
ng generate --help
```

## Building

To build the project run:

```bash
ng build
```

This will compile your project and store the build artifacts in the `dist/` directory. By default, the production build optimizes your application for performance and speed.

## Running unit tests

To execute unit tests with the [Karma](https://karma-runner.github.io) test runner, use the following command:

```bash
ng test
```

## Running end-to-end tests

For end-to-end (e2e) testing, run:

```bash
ng e2e
```

Angular CLI does not come with an end-to-end testing framework by default. You can choose one that suits your needs.

## Additional Resources

For more information on using the Angular CLI, including detailed command references, visit the [Angular CLI Overview and Command Reference](https://angular.dev/tools/cli) page.
