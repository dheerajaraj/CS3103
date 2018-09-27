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


int main()  //AaBee TCP Client

{

        int sock, bytes_recieved;  
        char send_data[1024] = "GET /tools/yourip.php HTTP/1.1\nHost:varlabs.comp.nus.edu.sg\n\n";
        char recv_data[1024];
        struct hostent *host;
        struct sockaddr_in server_addr;  

        host = gethostbyname("varlabs.comp.nus.edu.sg");

		//create a Socket structure   - "Client Socket"
		if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == -1) { //sock indicates if it is SOCK_DGRAM, SOCK_STREAM or SOCK_SEQPACKET
            perror("Socket");
            exit(1);
        }
        server_addr.sin_family = AF_INET;     
        server_addr.sin_port = htons(80); // Converts from host byte order (little endian) to network byte order (big endian)  
        /*sin_addr is the IP host address/internet address. The in_addr has only 1 attribute; s_addr.
		    This s_addr is the address in network byte order. 
        */ 
        server_addr.sin_addr = *((struct in_addr *)host->h_addr); 
        bzero(&(server_addr.sin_zero),8); //bzero erases 8 bytes of memory starting at the location pointed by 1st argument by writing \0. 
		    
        //connect to server at port 80
        if (connect(sock, (struct sockaddr *)&server_addr,
                    sizeof(struct sockaddr)) == -1) 
        {
            perror("Connect");
            exit(1);
        }
        printf("\nI am conneted to (%s , %d)", inet_ntoa(server_addr.sin_addr),ntohs(server_addr.sin_port));  //ntoa - forms dotted decimal notation

        while(1)
        {
    			//send data to server
    			send(sock,send_data,strlen(send_data), 0); 
    			  
    			//get reply from server  
    			bytes_recieved=recv(sock,recv_data,1024,0);
          printf("\nBytes Received: %d", bytes_recieved);
    			recv_data[bytes_recieved] = '\0';
    			  
    			//process data. Here, we simply print it  
    			//printf("\n This is the received text: %s ", recv_data);
           
           break;
        }

        close(sock);

        char *iter, *body, *rbody, *cpy;
        char pin[7]="<body>"; //indicator for beginning of IP address
        char pinr[8]="</body>"; //Indicator for end of IP address
        char IP[200]; // Final IP address parsed
        cpy=IP;

        body=strstr(recv_data,pin); //returns starting of <body>
        rbody=strstr(body,pinr); // returns starting of </body>
        body=body+6;//points to the end of <body> tag. 
      
        while(body<rbody){
          //Eliminates newline and copies to IP array pointed by cpy pointer. 
          if(*body!='\n'){
            *cpy=*body;
            cpy++;
          }
            body++;
        }
        cpy='\0';
        printf("\nMy public IP address is: %s\n",IP);
  
return 0;
}