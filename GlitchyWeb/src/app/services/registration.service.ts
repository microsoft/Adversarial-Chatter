import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class RegistrationService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:3000/api/register'; // Adjust backend URL

  sendData(formData: { username: string; email: string }) {
    return this.http.post(this.apiUrl, formData);
  }
}
