import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Torrent } from './models/torrent.model';

@Injectable({
  providedIn: 'root'
})
export class TorrentService {
  
  constructor(private http: HttpClient) { }

  getTorrents(): Observable<Torrent[]> {
    return this.http.get<Torrent[]>(`/torrents`);
  }

  addTorrent(torrent: { magnet_link: string; description: string; category: string }): Observable<{ message: string; delete_key: string }> {
    return this.http.post<{ message: string; delete_key: string }>(`/add_torrent`, torrent);
  }
  
  deleteTorrent(info_hash: string, delete_key: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`/remove_torrent`, {
      body: { info_hash, delete_key }
    });
  }
  
}
