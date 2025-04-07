import { Component, OnInit } from '@angular/core';
import { BlogService } from '../../services/blog.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-blog-page',
  templateUrl: './blog-page.component.html',
  styleUrls: ['./blog-page.component.css'],
  standalone: true,
  imports: [CommonModule] // Ensure CommonModule is imported here
})
export class BlogPageComponent implements OnInit {
  blogPosts: { title: string; content: string; author: string; publish_date: string }[] = [];
  currentPage: number = 1;
  pageSize: number = 40; // Number of posts per page
  totalPosts: number = 0;
  Math = Math; // Add Math to the component class

  constructor(private blogService: BlogService) {}

  ngOnInit() {
    this.loadBlogPosts();
  }

  loadBlogPosts() {
    this.blogService.getAllBlogs().subscribe((posts) => {
      this.totalPosts = posts.length;
      this.blogPosts = posts.slice((this.currentPage - 1) * this.pageSize, this.currentPage * this.pageSize);
    });
  }

  changePage(page: number) {
    this.currentPage = page;
    this.loadBlogPosts();
  }
}