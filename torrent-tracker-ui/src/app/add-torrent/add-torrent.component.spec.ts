import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddTorrentComponent } from './add-torrent.component';

describe('AddTorrentComponent', () => {
  let component: AddTorrentComponent;
  let fixture: ComponentFixture<AddTorrentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AddTorrentComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(AddTorrentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
