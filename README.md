# 🔁 Go-Back-N over UDP — Computer Networks

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-1f2328?style=flat-square&logo=python&logoColor=white">
  <img alt="Course" src="https://img.shields.io/badge/Course-Computer%20Networks%20(RC)-1f2328?style=flat-square">
  <img alt="Year" src="https://img.shields.io/badge/2025%2F26-3rd%20year%2C%201st%20semester-1f2328?style=flat-square">
</p>

Assignment 2 of *Redes de Computadores* (Computer Networks), Computer Science degree at **NOVA School of Science and Technology (FCT NOVA)**.

## About

**Reliable file transfer over an unreliable network.** A sender and a receiver exchange a file over **UDP**, where both data blocks and acknowledgements are randomly dropped (about 20% of them, to simulate a lossy network). Reliability is built on top with the **Go-Back-N** protocol:

- The receiver asks for a file and chooses the block size.
- The sender keeps a **sliding window** of up to *N* unacknowledged blocks, sent by a transmission thread.
- Acknowledgements are **cumulative** and move the window forward; if no acknowledgement arrives before the **timeout**, the whole window is sent again.
- The receiver only accepts the next block in order and discards the rest.

## Running it

```bash
# sender: port, window size, timeout in seconds
python3 sender.py 9000 4 1

# receiver: sender IP, sender port, remote file, local file, block size
python3 receiver.py 127.0.0.1 9000 data.bin copy.bin 1024
```

The sender logs each block it sends and each timeout/retransmission.


## What I learned

- Why UDP needs extra mechanisms for reliability: sequence numbers, acknowledgements, timeouts and retransmission
- Sliding-window flow, and the trade-offs of Go-Back-N
- Coordinating sender threads with a condition variable

## Authors

- **Miguel Carmo** ([@MCCProgrammer](https://github.com/MCCProgrammer))
- **Tomás Ramos Alves** ([@Alvesss04](https://github.com/Alvesss04))

---

<sub>The assignment statement is not included in this repository, as it belongs to the course's teaching staff. This is a student project shared for portfolio purposes.</sub>
