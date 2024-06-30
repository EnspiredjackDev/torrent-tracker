import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { TorrentService } from '../torrent.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-add-torrent',
  templateUrl: './add-torrent.component.html',
  styleUrls: ['./add-torrent.component.css']
})
export class AddTorrentComponent implements OnInit {
  torrentForm: FormGroup;
  categories = ["catagory1", "catagory2", "catagory3", "etc"];
  deleteKey: string = "";
  powSolved: boolean = false;
  nonce: number | null = null;
  challenge: string = '';

  constructor(private torrentService: TorrentService, private snackBar: MatSnackBar, private http: HttpClient) {
    this.torrentForm = new FormGroup({
      magnet_link: new FormControl('', [Validators.required]),
      description: new FormControl('', [Validators.maxLength(200)]),
      category: new FormControl([], [Validators.required])
    });
  }

  ngOnInit() {
    this.powSolved = false;
  }

  onPoWSolved(event: { nonce: number, challenge: string }) {
    this.nonce = event.nonce;
    this.challenge = event.challenge;
    this.powSolved = true;
  }

  onSubmit() {
    if (this.torrentForm.valid && this.powSolved) {
      const formValue = { ...this.torrentForm.value, nonce: this.nonce, challenge: this.challenge };
      this.torrentService.addTorrent(formValue).subscribe({
        next: (response) => {
          this.snackBar.open(response.message, 'Close', { duration: 3000 });
          this.deleteKey = response.delete_key;
          this.torrentForm.reset();
          this.powSolved = false;  // Reset the PoW status for the next submission
          this.nonce = null;  // Clear nonce
          this.challenge = '';  // Clear challenge
        },
        error: (error) => {
          this.snackBar.open('Failed to add the torrent: ' + error.error.message, 'Close');

        }
      });
    }
  }
}
