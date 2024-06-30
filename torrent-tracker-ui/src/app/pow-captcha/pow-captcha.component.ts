import { Component, Output, EventEmitter, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import * as CryptoJS from 'crypto-js';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-pow-captcha',
  templateUrl: './pow-captcha.component.html',
  styleUrls: ['./pow-captcha.component.css']
})
export class PowCaptchaComponent implements OnInit {
  @Output() powSolved = new EventEmitter<{ nonce: number, challenge: string }>();

  challenge: string = '';
  nonce: number | null = null;
  solved: boolean = false;
  solving: boolean = false;

  constructor(private http: HttpClient, private readonly snackbar: MatSnackBar) {}

  ngOnInit() {
    // this.fetchPoWChallenge();
  }

  fetchPoWChallenge() {
    this.http.get<{ challenge: string, threshold: string }>('/pow-challenge').subscribe({
      next: (response) => {
        this.challenge = response.challenge;
        this.solvePoWChallenge(response.challenge, response.threshold);
      },
      error: () => {
        this.snackbar.open('Failed to fetch PoW challenge', 'Close');
      }
    });
  }

  solvePoWChallenge(challenge: string, threshold: string) {
    this.solving = true;
    setTimeout(() => {  // Simulate async processing
      let nonce = 0;
      while (true) {
        const hash = CryptoJS.SHA256(challenge + nonce).toString(CryptoJS.enc.Hex);
        if (this.lessThan(hash, threshold)) {
          this.nonce = nonce;
          this.solved = true;
          this.solving = false;
          this.powSolved.emit({ nonce, challenge });
          break;
        }
        nonce++;
      }
    }, 100);  // Allow UI to update before starting the PoW solving
  }

  lessThan(hash: string, threshold: string): boolean {
    // Compare hash and threshold as hexadecimal strings
    return BigInt('0x' + hash) < BigInt('0x' + threshold);
  }
}
