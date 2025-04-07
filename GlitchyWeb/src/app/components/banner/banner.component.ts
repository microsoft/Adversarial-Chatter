import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-banner',
  imports: [],
  templateUrl: './banner.component.html',
  styleUrl: './banner.component.css',
  standalone: true
})
export class BannerComponent {

  constructor(private router: Router) {}


  pageTitle: string = 'Glitchy Web';

  onButtonClick(buttonName: string) {
    console.log(`${buttonName} button clicked`);
    // Add your button click logic here
  }

  navigateHome(){
    this.router.navigate(['']);
  }

  navigateToBlogs(){
      this.router.navigate(['/blogs']);
    }

  navigateToRegistration(){
    this.router.navigate(['/register']);
  }

  navigateToContact(){
    this.router.navigate(['/contact']);
  }


}
