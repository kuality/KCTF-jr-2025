# Hidden In Stream

## Description
I have a server that sends exactly 100,000 bytes of data. Somewhere in this massive stream, I've hidden a flag. Can you find it?

The server might be a bit slow... but patience is a virtue, right?

## Challenge Information
- **Category**: Misc
- **Points**: 200
- **Author**: KUality

## Connection Info
```bash
nc [SERVER_IP] 11000
```

## Hints
1. The flag format is `KCTF_Jr{...}`
2. You might want to capture all the output and search through it
3. The flag is somewhere in the middle of the stream

## Sample Interaction
```
$ nc localhost 11000
Welcome to Hidden Stream Challenge!
I will send you 100,000 bytes... Can you find the hidden flag?
Starting stream...

[... lots of random bytes ...]
```

## Notes
- The server sends one byte at a time
- The total stream is exactly 100,000 bytes (excluding welcome/completion messages)
- The flag appears as a continuous string somewhere in the stream
- Be prepared to handle various types of bytes (printable and non-printable)