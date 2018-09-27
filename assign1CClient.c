/*
Mini FTP Client Program:
Written by R Dheeraj.
NUS (National University of Singapore)
Matric Number: A0135769N
*/

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
void  childProc(int newport, char pass[1024], int option);                /* child process prototype  */
int  inputParsing(char uname[1024], char pass[1024]);
void clientcomms(char url[300]);
int main()  //AaBee TCP Client

{
printf("Please Enter the IP address that you want to connect to: ");
char url[300];
scanf("%s",url);
clientcomms(url);
return 0;
}

void clientcomms(char url[300])
{
        int sock, bytes_recieved;
        int option;
        char send_data[1024], input_str[1024];
        char recv_data[1024];
        struct hostent *host;
        struct sockaddr_in server_addr, sec_server_addr;  
        int startnew=0, quit=0;
        pid_t p; 
        int fd1[2], fd2[2];
        int newport=0;
        char delimport[10]="|||";
        char *portptr;
        char portnum[10];

        host = gethostbyname(url);
        //host=getaddrinfo()
    //create a Socket structure   - "Client Socket"
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == -1) { //sock indicates if it is SOCK_DGRAM, SOCK_STREAM or SOCK_SEQPACKET
            perror("Socket");
            exit(1);
        }

        server_addr.sin_family = AF_INET;     
        server_addr.sin_port = htons(21); 
        server_addr.sin_addr = *((struct in_addr *)host->h_addr); 
        bzero(&(server_addr.sin_zero),8); 

        //connect to server at port 21
        if (connect(sock, (struct sockaddr *)&server_addr, sizeof(struct sockaddr)) == -1) 
        {
            perror("Connect");
            exit(1);
        }

         printf("\n I am conneted to (%s , %d)",
         inet_ntoa(server_addr.sin_addr),ntohs(server_addr.sin_port));  //ntoa - forms dotted decimal notation

         bytes_recieved=recv(sock,recv_data,1024,0);
         recv_data[bytes_recieved] = '\0';
         printf("%s\n",recv_data);
        while(1)
        {
              char uname[1024]="USER ", pass[1024]="PASS ";

              option=inputParsing(uname, pass);
           
            if(option==7){
             strcpy(send_data,"QUIT\r\n");
             send(sock,send_data,strlen(send_data), 0);   
             close(sock);
             break;
              }
             

            if(option==1){
              strcpy(send_data,uname);
              send(sock,send_data,strlen(send_data), 0); 
              bytes_recieved=recv(sock,recv_data,1024,0);
              recv_data[bytes_recieved] = '\0';
              printf("\n%s",recv_data);

              strcpy(send_data,pass);
              send(sock,send_data,strlen(send_data), 0); 
              bytes_recieved=recv(sock,recv_data,1024,0);
              recv_data[bytes_recieved] = '\0';
              printf("\n%s",recv_data);

            }
            else{
              if(option==4||option==5||option==6){
                startnew=1;  
              }

              else{
                 startnew=0;
              }

              strcpy(send_data,uname);
              //send data to server
               send(sock,send_data,strlen(send_data), 0); 
               bytes_recieved=recv(sock,recv_data,1024,0);
               recv_data[bytes_recieved] = '\0';
               printf("\n%s",recv_data);
             //printf("startnew: %d", startnew);
           

               if(startnew){
                  portptr=strstr(recv_data,delimport)+3;
                 // printf("portptr: %s", portptr);
                  int c=0;
                  while((*portptr)!='|'){
                    portnum[c++]=*portptr;
                    portptr++;
                  }
                  portnum[c]='\0';
                  newport=atoi(portnum);
                  //printf("portnum: %d",newport);

                  p=fork();
                  if(p==0){
                    childProc(newport,pass,option);
                  }
                  if(option==4||option==6||option==5){
                  strcpy(send_data,pass);
                  send(sock,send_data,strlen(send_data), 0);

                    bytes_recieved=recv(sock,recv_data,1024,0);
                    recv_data[bytes_recieved] = '\0';
                    printf("\n%s\r\n",recv_data);

                    bytes_recieved=recv(sock,recv_data,1024,0);
                    recv_data[bytes_recieved] = '\0';
                    printf("\n%s\r\n",recv_data);

                  }
                   

                    
                }
      
               }


        }

    }   


void childProc(int port,char pass[1024], int option){

  //printf("I am in child process now");
  int sock, bytes_recieved;  
        char send_data[1024],recv_data[1024];
        struct hostent *host;
        struct sockaddr_in server_addr;  

        host = gethostbyname("192.168.1.127");
        if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == -1) { //sock indicates if it is SOCK_DGRAM, SOCK_STREAM or SOCK_SEQPACKET
            perror("Socket");
            exit(1);
        }

        server_addr.sin_family = AF_INET;     
        server_addr.sin_port = htons(port); 
        server_addr.sin_addr = *((struct in_addr *)host->h_addr); 
        bzero(&(server_addr.sin_zero),8);

        if (connect(sock, (struct sockaddr *)&server_addr, sizeof(struct sockaddr)) == -1) 
        {
            perror("Connect");
            exit(1);
        }
        // printf("port number: %d\n", port);
         printf("\n I am conneted to (%s , %d)",
         inet_ntoa(server_addr.sin_addr),ntohs(server_addr.sin_port));

          //printf("pass in child:%s",pass);
           if(option==5){
              char key[10] = "STOR";
              char *trk;
              trk = strstr(pass, key);
              if(trk!=NULL){
                trk+=5;
                trk[strlen(trk)-2]='\0';
              }
              FILE *file=fopen(trk,"r+");
              if(file == NULL) {
              perror("Error in opening file");
              return;
             }

            while(!feof(file)) {
              char filebuffer[1024];
              int wasRead = fread(filebuffer, sizeof(char), 1024, file);
              send (sock, filebuffer, (sizeof (char) * wasRead), 0);
              }
              //fflush(stdout);
           
         printf("Exited child process\r\n");
         exit(0);
         close(sock);
          }

          char needle[10] = "RETR";
          char *ret;
          ret = strstr(pass, needle);

          bytes_recieved=recv(sock,recv_data,1024,0);
          recv_data[bytes_recieved] = '\0';
          printf("\n%s\r\n",recv_data);

          if(ret!=NULL){
            ret+=5;
            ret[strlen(ret)-2]='\0';
            FILE *fp = fopen(ret,"a");
            fprintf(fp, "%s",recv_data);
          }

          fflush(stdout);
           
         printf("Exited child process\r\n");
         exit(0);
         close(sock);
}

int inputParsing(char username[1024], char pass[1024]){
    char bufferu[1024]="", bufferp[1024]="";
    int opt;
    do{
      printf("********************************************** \n");
      printf("*************** MINI-FTP Client ************** \n");
      printf("********************************************** \n");
      printf("1. Connect to FTP server\n");
      printf("2. Print working directory\n");
      printf("3. Change working directory\n");
      printf("4. List all files\n");
      printf("5. Upload file\n");
      printf("6. Download file\n");
      printf("7. Quit\n\n");
      printf("Please Enter an option: \n");
      scanf("%d", &opt);
      if(opt<1||opt>7){
        printf("Error! Enter a valid option from 1 to 7\n");
      }  
    } while(opt<1||opt>7);
      if(opt==1){
        printf("Enter username:\n");
        scanf("%s",bufferu);
        strcat(username,bufferu);
        strcat(username,"\r\n");
        printf("Enter Password:\n");
        scanf("%s",bufferp);
        strcat(pass,bufferp);
        strcat(pass,"\r\n");
      }
      else if(opt==7){
        strcpy(username,"");
        strcpy(pass,"");
      }
      else if(opt==2){
        strcpy(username,"PWD\r\n");
        strcpy(pass,"");
      }
      else if(opt==3){
        strcpy(username,"CWD ");
        printf("Please enter the new directory: ");
        scanf("%s",bufferu);
        strcat(username,bufferu);
        strcat(username, "\r\n");
        strcpy(pass,"");
      }
      else if(opt==4){
        strcpy(username,"EPSV\r\n");
        strcpy(pass, "LIST\r\n");
      }
      else if(opt==6){
        strcpy(username,"EPSV\r\n");
        printf("Please enter the file name: ");
        scanf("%s",bufferp);
        strcpy(pass, "RETR ");
        strcat(pass, bufferp);
        strcat(pass,"\r\n");
      }
      else if(opt==5){
        strcpy(username,"EPSV\r\n");
        printf("Please enter the absolute file path or file name: ");
        scanf("%s",bufferp);
        strcpy(pass, "STOR ");
        strcat(pass, bufferp);
        strcat(pass,"\r\n");
      }
      
    return opt;
}