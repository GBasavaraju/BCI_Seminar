import time

if __name__ == "__main__":
    numbers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
               1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, \
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    with open("predict.txt", 'w') as f:
        for number in numbers:
            f.write(str(number) + "\n")
            f.flush()
            time.sleep(1)