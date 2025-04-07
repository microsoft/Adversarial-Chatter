import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { BannerComponent } from './components/banner/banner.component';



@Component({
  selector: 'app-root',
  imports: [RouterOutlet,BannerComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
  
})
export class AppComponent {
  // title = 'Glitchy Web';
}
