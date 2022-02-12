import processing.net.*; 

Client myClient; 
int dataIn; 
int count = 0;

int pos8 = 0;
int pos9 = 0;
void setup() { 
  size(200, 200); 
  // Connect to the local machine at port 5204.
  // This example will not run if you haven't
  // previously started a server on this port.
  myClient = new Client(this, "127.0.0.1", 3458); 
} 
 
void draw() { 
  if (myClient.available() > 0) { 
    dataIn = myClient.read(); 
  if(dataIn==87)
  {
    println("");
   println("data = ", pos8 , " ",pos9 );
    count = 0;
  }
  count= count +1 ;
  print(dataIn," ");
  if(count == 8)
  {pos8 = dataIn;}
  if(count ==9)
  {pos9 = dataIn;}
} 
  
} 
