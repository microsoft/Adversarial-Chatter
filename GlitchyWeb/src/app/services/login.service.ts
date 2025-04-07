import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class LoginService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:3000/api/login'; // Adjust backend URL

  userLogin(formData: { username: string; password: string }) {
    return this.http.post(this.apiUrl, formData);
  }
}
