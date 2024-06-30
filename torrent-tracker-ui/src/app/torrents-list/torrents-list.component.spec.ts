import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TorrentsListComponent } from './torrents-list.component';

describe('TorrentsListComponent', () => {
  let component: TorrentsListComponent;
  let fixture: ComponentFixture<TorrentsListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [TorrentsListComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(TorrentsListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
