import { Component, OnInit, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { Torrent } from '../models/torrent.model';
import { TorrentService } from '../torrent.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-torrents-list',
  templateUrl: './torrents-list.component.html',
  styleUrls: ['./torrents-list.component.css']
})
export class TorrentsListComponent implements OnInit {
  torrents: Torrent[] = [];
  displayedColumns: string[] = ['name', 'info_hash', 'description', 'category', 'actions'];
  categories: string[] = ['catagory1', 'catagory2', 'catagory3', 'etc'];
  selectedCategory: string = 'All';
  searchQuery: string = '';
  dataSource: MatTableDataSource<Torrent> = new MatTableDataSource<Torrent>();

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  constructor(private torrentService: TorrentService, private snackBar: MatSnackBar) {}

  ngOnInit() {
    this.loadTorrents();
  }

  loadTorrents(): void {
    this.torrentService.getTorrents().subscribe({
      next: (data) => {
        this.torrents = data;
        this.dataSource.data = data;
        this.dataSource.paginator = this.paginator;
        this.applyFilter();
      },
      error: (_error) => {
        this.snackBar.open('Failed to load torrents', 'Close', { duration: 3000 });
      }
    });
  }

  filterTorrents(): void {
    if (this.selectedCategory === 'All') {
      this.applyFilter();
    } else {
      this.dataSource.data = this.torrents.filter(torrent => torrent.category.includes(this.selectedCategory));
      this.applyFilter();
    }
  }

  applyFilter(): void {
    const filteredData = this.torrents.filter(torrent => {
      const matchesCategory = this.selectedCategory === 'All' || torrent.category.includes(this.selectedCategory);
      const matchesQuery = torrent.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        torrent.description.toLowerCase().includes(this.searchQuery.toLowerCase());
      return matchesCategory && matchesQuery;
    });
    this.dataSource.data = filteredData;
  }
}
