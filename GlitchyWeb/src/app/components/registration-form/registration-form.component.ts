import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { RegistrationService } from '../../services/registration.service'


@Component({
  selector: 'app-registration-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './registration-form.component.html',
  styleUrls: ['./registration-form.component.css'],
})
export class RegistrationFormComponent {
  registrationForm: FormGroup;
  validationMessage: string;

  constructor(
      private fb: FormBuilder,
      private registrationService: RegistrationService
    ) {
      
    this.validationMessage = '';
    this.registrationForm = this.fb.group({
      firstname: ['', Validators.required],
      lastname: ['', Validators.required],
      username: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  onSubmit() {
    if (this.registrationForm.valid) {
      this.registrationService.sendData(this.registrationForm.value).subscribe(response => {
        console.log('Registration successful', response);
      }, error => {
        console.error('Registration failed', error);
        this.validationMessage = error.error.message;
      });
    } else {
      this.validationMessage = 'Please fill out all required fields.';
    }
  }

}