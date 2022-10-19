# dark_dimension

## Write-up

- [Challenge source code](./dark_dimension.dart).  

The major goal of the challenge, which was built in Dart (as many have already guessed), was to make it extremely difficult to reverse (even though one team actually used GDB and IDA to do so) and to teach the player about "time attacks", so it's like a blind SQL time injection, but in a binary.  

> The description focused on Dr. Strange, a fictional character who has control over time.  

The binary requests a code, validates its length and character by character, and then sleeps for 50 to 100 milliseconds after each test.  

The player considers optimizing the brute force because the length of the code was not provided to avoid simple brute forces.  

A straightforward [Dockerfile](./Dockerfile) and a [Python script](./speedtest.py) that brute forces the code are supplied.  

The purpose of the Docker file is to enable precise outcomes by controlling CPU execution.  

```bash
docker image build -t speedtestdarkdimention:0.0.1 .
docker run -it --cpus="1" speedtestdarkdimention:0.0.1
```
