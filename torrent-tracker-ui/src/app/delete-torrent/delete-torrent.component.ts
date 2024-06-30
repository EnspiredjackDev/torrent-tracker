import { Component } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { TorrentService } from '../torrent.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-delete-torrent',
  templateUrl: './delete-torrent.component.html',
  styleUrls: ['./delete-torrent.component.css']
})
export class DeleteTorrentComponent {
  deleteForm: FormGroup;

  constructor(private torrentService: TorrentService, private snackBar: MatSnackBar) {
    this.deleteForm = new FormGroup({
      info_hash: new FormControl('', [Validators.required]),
      delete_key: new FormControl('', [Validators.required])
    });
  }

  onSubmit() {
    if (this.deleteForm.valid) {
      const { info_hash, delete_key } = this.deleteForm.value;
      this.torrentService.deleteTorrent(info_hash, delete_key).subscribe({
        next: (response) => {
          this.snackBar.open(response.message, 'Close', { duration: 3000 });
          this.deleteForm.reset();
        },
        error: () => {
          this.snackBar.open('Failed to delete the torrent', 'Close', { duration: 3000 });
        }
      });
    }
  }
}
