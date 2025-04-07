import { Routes } from '@angular/router';
import { AppComponent } from './app.component';
import {LoginPageComponent}  from './components/login-page/login-page.component';
import {BlogPageComponent}  from './components/blog-page/blog-page.component';
import { RegistrationFormComponent } from './components/registration-form/registration-form.component';
import { ContactPageComponent } from './components/contact-page/contact-page.component';

export const routes: Routes = [ 
    { path: '', component: LoginPageComponent },
    { path: 'blogs', component: BlogPageComponent },
    { path: 'register', component: RegistrationFormComponent },
    {path: 'contact', component:ContactPageComponent},

];
