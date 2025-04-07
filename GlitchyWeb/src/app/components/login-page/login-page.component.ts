import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { LoginService } from '../../services/login.service';

@Component({
  selector: 'app-login-page',
  standalone: true,
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.css'], // Corrected this line
  imports: [ReactiveFormsModule]
})
export class LoginPageComponent {

  loginForm: FormGroup;
  username: string = '';
  password: string = '';
  validationMessage: string;


    constructor(
        private fb: FormBuilder,
        private loginService: LoginService
      ) {
        
      this.validationMessage = '';
      this.loginForm = this.fb.group({
        username: ['', Validators.required],
        password: ['', Validators.required]
      });
    }


  onSubmit() {
    if (this.loginForm.valid) {
      this.loginService.userLogin(this.loginForm.value).subscribe(response => {
        console.log('login successful', response);
      }, error => {
        console.error('login failed', error);
        this.validationMessage = error.error.message;
      });
    } else {
      this.validationMessage = 'Please fill out all required fields.';
    }
  }


  // onSubmit() {
  //   // Handle the login logic here
  //   console.log('Username:', this.username);
  //   console.log('Password:', this.password);
  // }
}
