import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import {Component, Inject} from '@angular/core';
import {DataService} from '../../services/data.service';
import {FormControl, Validators} from '@angular/forms';
import { formatDate } from '@angular/common';

@Component({
  selector: 'app-baza.dialog',
  templateUrl: '../../dialogs/edit/edit.dialog.html',
  styleUrls: ['../../dialogs/edit/edit.dialog.css']
})
export class EditDialogComponent {

  date = new FormControl(new Date());

  constructor(public dialogRef: MatDialogRef<EditDialogComponent>,@Inject(MAT_DIALOG_DATA) public data: any, public dataService: DataService) { }

  public urlvalidate = /(^|\s)((https?:\/\/)?[\w-]+(\.[\w-]+)+\.?(:\d+)?(\/\S*)?)/gi

  url = new FormControl('', [Validators.required, Validators.pattern(this.urlvalidate)]);

  formControl = new FormControl('', [
    Validators.required
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
    // emppty stuff
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  stopEdit(): void {
    console.log("stopEdit::Edit="+this.data);
    //this.data.datecreated =formatDate(this.data.datecreated,"yyyy-MM-dd","es-ES");
    ///this.data.datemodified =formatDate(this.data.datemodified,"yyyy-MM-dd","es-ES");
    if(this.imageSrc){
      this.data.image=this.imageSrc;
      this.data.imagename=this.imagename;
    }
    this.dataService.updateIssue(this.data);
  }
}
