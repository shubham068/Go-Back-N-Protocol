# Go-Back-N-protocol
This project simulates working of go-back-n-protocol.

Sender provides the Size of window,Time for timeout and number of packets to send as input.
Reciever takes probablity of discarding packets.

It have multithreaded sender reciever structure

If packet No.6 is the last packet received which was expected and say frame No.7 was lost,
then if subsequent invalid packets like packet No. 9 arrives , it sends the acknowledgement 
of packet Number 6 again.

Once, sender reaches window size, it timeouts and resumes to send frames from frame No.7.
