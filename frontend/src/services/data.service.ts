import {Injectable} from '@angular/core';
import {BehaviorSubject} from 'rxjs';
import {Products} from '../models/products';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import { formatDate } from '@angular/common';  

@Injectable()
export class DataService {
  
  //private readonly API_URL = 'http://localhost:${BACKEND_FLASK_PORT}/api';
  private readonly API_URL = 'http://localhost:8081/api';

  dataChange: BehaviorSubject<Products[]> = new BehaviorSubject<Products[]>([]);
  dialogData: any;
  imageSrc: string;

  constructor (private httpClient: HttpClient) {}

  get data(): Products[] {
    return this.dataChange.value;
  }

  getDialogData() {
    return this.dialogData;
  }

  /** CRUD METHODS */
  getAllIssues(): void {
    this.httpClient.get<Products[]>(this.API_URL+"/data").subscribe(data => {
        console.log(data);
        this.dataChange.next(data);
      },
      (error: HttpErrorResponse) => {
        console.log (error.name + ' ' + error.message);
      });
  }

  onUploadImage(uploadData:any,id:any) {
    const postData: any = {id:id, image:uploadData};
    this.httpClient.post(this.API_URL+"/api/image", uploadData, {
      reportProgress: true,
      observe: 'events'
    }).subscribe(event => {
        console.log(event); // handle event here
    });
  }

  //['id', 'copyright', 'title', 'image', 'datecreated', 'datemodified', 'actions'];-->
  // ADD, POST METHOD
  addIssue (product: Products): void {
    //product.datecreated =formatDate(product.datecreated,"yyyy-MM-dd","es-ES");
    //product.datemodified =formatDate(product.datemodified,"yyyy-MM-dd","es-ES");
    console.log('addIssue:: add product='+product.id);
    console.log('addIssue:: add product='+product);
    const postData: any = {id:product.id, copyright:product.copyright, title:product.title, 
                          image:product.image, imagename:product.imagename, datecreated:product.datecreated};
    this.httpClient.post(this.API_URL+"/add",postData).subscribe(data => {
      console.log("addIssue:: Successfully add id="+product.id);
      console.log("addIssue:: Successfully add product="+product);
    },
    (err: HttpErrorResponse) => {
      console.log('Error occurred. Details: ' + err.name + ' ' + err.message);
    });
    this.dialogData = product;
  }

  // UPDATE, PUT METHOD
  updateIssue (product: Products): void {
    //product.datecreated =formatDate(product.datecreated,"yyyy-MM-dd","es-ES");
    //product.datemodified =formatDate(product.datemodified,"yyyy-MM-dd","es-ES");
    console.log('updateIssue:: edit product='+product.id);
    console.log('updateIssue:: edit product='+product);
    const postData: any = {id:product.id, copyright:product.copyright, title:product.title, 
                          image:product.image, imagename:product.imagename, datecreated:product.datecreated, datemodified:product.datemodified};
    this.httpClient.post(this.API_URL+"/update",postData).subscribe(data => {
        console.log('updateIssue:: Successfully edited id='+product.id);
        console.log('updateIssue:: Successfully edited product='+product);
    },
    (err: HttpErrorResponse) => {
        console.log('Error occurred. Details: ' + err.name + ' ' + err.message);
      }
    );
    this.dialogData = product;
  }

  // DELETE METHOD
  deleteIssue (id: number): void {
    const postData: any = { id: id};
    this.httpClient.post(this.API_URL+"/delete",postData).subscribe(data => {
        console.log("deleteIssue::delete="+id);
      },
      (err: HttpErrorResponse) => {
        console.log('Error occurred. Details: ' + err.name + ' ' + err.message);
      }
    );
  }  
}