import { ApplicationConfig, provideZoneChangeDetection, importProvidersFrom  } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { provideClientHydration, withEventReplay } from '@angular/platform-browser';

//Custom Imports
import { FormsModule } from '@angular/forms';

export const appConfig: ApplicationConfig = {
  providers: [provideZoneChangeDetection({ eventCoalescing: true }), 
    provideRouter(routes) , provideClientHydration(withEventReplay()), 
    importProvidersFrom(FormsModule),provideHttpClient(),CommonModule]
};
