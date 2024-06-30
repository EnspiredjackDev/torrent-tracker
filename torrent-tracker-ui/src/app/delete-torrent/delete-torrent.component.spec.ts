import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeleteTorrentComponent } from './delete-torrent.component';

describe('DeleteTorrentComponent', () => {
  let component: DeleteTorrentComponent;
  let fixture: ComponentFixture<DeleteTorrentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DeleteTorrentComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DeleteTorrentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
