declare namespace NodeJS {
    interface ProcessEnv {
      DB_USER: string;
      DB_PASSWORD: string;
      DB_SERVER: string;
      DB_NAME: string;
    }
  }