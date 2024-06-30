import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PowCaptchaComponent } from './pow-captcha.component';

describe('PowCaptchaComponent', () => {
  let component: PowCaptchaComponent;
  let fixture: ComponentFixture<PowCaptchaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [PowCaptchaComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(PowCaptchaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
