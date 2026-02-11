import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  imports: [
    BrowserModule,
    ReactiveFormsModule,
    HttpClientModule
  ]
})
export class AppModule {}
<h2>Transfer Funds</h2>

<form [formGroup]="transferForm" (ngSubmit)="submitTransfer()">

  <label>From Account ID</label>
  <input type="number" formControlName="fromAccountId" />

  <label>To Account ID</label>
  <input type="number" formControlName="toAccountId" />

  <label>Amount</label>
  <input type="number" formControlName="amount" />

  <button type="submit" [disabled]="transferForm.invalid">
    Transfer
  </button>
</form>

<p style="color: green" *ngIf="successMessage">
  {{ successMessage }}
</p>

<p style="color: red" *ngIf="errorMessage">
  {{ errorMessage }}
</p>
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { v4 as uuidv4 } from 'uuid';
import { TransferService } from '../../services/transfer.service';

@Component({
  selector: 'app-transfer',
  templateUrl: './transfer.component.html'
})
export class TransferComponent {

  transferForm: FormGroup;
  successMessage = '';
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private transferService: TransferService
  ) {
    this.transferForm = this.fb.group({
      fromAccountId: ['', Validators.required],
      toAccountId: ['', Validators.required],
      amount: ['', [Validators.required, Validators.min(1)]]
    });
  }

  submitTransfer() {
    this.successMessage = '';
    this.errorMessage = '';

    if (this.transferForm.invalid) {
      return;
    }

    const request = {
      ...this.transferForm.value,
      idempotencyKey: uuidv4()
    };

    this.transferService.transferFunds(request).subscribe({
      next: (res) => {
        this.successMessage = res.message;
        this.transferForm.reset();
      },
      error: (err) => {
        this.errorMessage = err.error?.message || 'Transfer failed';
      }
    });
  }
}
