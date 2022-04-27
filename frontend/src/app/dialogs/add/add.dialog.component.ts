import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import {Component, Inject} from '@angular/core';
import {DataService} from '../../services/data.service';
import {FormControl, Validators} from '@angular/forms';
import {Products} from '../../models/products';
//import { formatDate } from '@angular/common';  

@Component({
  selector: 'app-add.dialog',
  templateUrl: '../../dialogs/add/add.dialog.html',
  styleUrls: ['../../dialogs/add/add.dialog.css']
})

export class AddDialogComponent {
  //formattedDate; 
  date = new FormControl(new Date());

  constructor(public dialogRef: MatDialogRef<AddDialogComponent>,@Inject(MAT_DIALOG_DATA) public data: Products,public dataService: DataService) { }

  formControl = new FormControl('', [
    Validators.required,
    // Validators.email,
  ]);

  imagename: string;
  imageSrc: any;

  onSelectFile(event:any):void {
    if (event.target.files && event.target.files[0]) {
      var reader = new FileReader();
      this.imagename=event.target.files[0].name;
      reader.readAsDataURL(event.target.files[0]); // read file as data url
      reader.onload = (event) => { // called once readAsDataURL is completed
        this.imageSrc = event.target.result;
      }
    }
  }

  numberOnly(event): boolean {
    const charCode = (event.which) ? event.which : event.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
      return false;
    }
    return true;
  }

  getErrorMessage() {
    return this.formControl.hasError('required') ? 'Required field' : '';
  }

  submit() {
  // empty stuff
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  public confirmAdd(): void {
    console.log(this.data);
    console.log("confirmAdd::Add id="+this.data.id+" data="+this.data);
    //this.data.datecreated =formatDate(this.data.datecreated,"yyyy-MM-dd","es-ES");
    //this.data.datemodified =formatDate(this.data.datemodified,"yyyy-MM-dd","es-ES");
    this.data.image=this.imageSrc;
    this.data.imagename=this.imagename;
    this.dataService.addIssue(this.data);
  }
}
