import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class BlogService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:3000/api/blogs'; // Base API URL

  // Fetch all blog posts
  getAllBlogs(): Observable<{ id: number; title: string; content: string; author: string; publish_date: string }[]> {
    return this.http.get<{ id: number; title: string; content: string; author: string; publish_date: string }[]>(this.apiUrl);
  }

  // Fetch a specific blog post by ID
  getBlogById(blogId: number): Observable<{ id: number; title: string; content: string; author: string; publish_date: string }> {
    return this.http.get<{ id: number; title: string; content: string; author: string; publish_date: string }>(`${this.apiUrl}/${blogId}`);
  }

  // Create a new blog post (assuming backend accepts POST requests)
  createBlog(formData: { title: string; content: string; author: string }): Observable<any> {
    return this.http.post(this.apiUrl, formData);
  }
}