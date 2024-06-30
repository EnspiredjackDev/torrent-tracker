import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AddTorrentComponent } from './add-torrent/add-torrent.component';
import { DeleteTorrentComponent } from './delete-torrent/delete-torrent.component';
import { TorrentsListComponent } from './torrents-list/torrents-list.component';

const routes: Routes = [
  { path: 'add-torrent', component: AddTorrentComponent },
  { path: 'delete-torrent', component: DeleteTorrentComponent },
  { path: '', component: TorrentsListComponent, pathMatch: 'full' },
  { path: '**', redirectTo: '/' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
