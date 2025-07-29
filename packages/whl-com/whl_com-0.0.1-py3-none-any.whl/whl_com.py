#!/usr/bin/env python3
"""com.py
"""
import sys
import threading
import time

import click
import serial

VERSION = '0.0.1'

stop_event = threading.Event()


def recv(conn):
    """Receive data from the serial connection
    """
    while not stop_event.is_set():
        try:
            data = conn.readline()
            if not data:
                continue
            # only print lines starting with $command
            # TODO(prettyprint): not only $command, but also other lines
            if data.startswith(b'$command'):
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            break
        except KeyboardInterrupt:
            print("Keyboard interrupt received, stopping...")
            break


def safe_serial_write(conn, data, retries=10):
    """Attempt to write data to the serial connection with retries."""
    for _ in range(retries):
        try:
            conn.write(data)
            return True
        except serial.SerialException:
            # wait a while
            time.sleep(0.1)
    return False


@click.command()
@click.option('-D', '--device', required=True, type=str, help='serial device')
@click.option('-b', '--baudrate', type=int, default=460800, help='baudrate')
@click.option('-t',
              '--timeout',
              type=float,
              default=1.0,
              help='timeout in seconds')
@click.option('-f', '--input_file', type=str, help='commands file')
@click.option('--dry_run',
              is_flag=True,
              help='do not send commands, just print them')
@click.argument('commands', nargs=-1)
def main(device, baudrate, timeout, input_file, dry_run, commands):
    """whl-com"""
    conn = serial.Serial(device, baudrate=baudrate, timeout=timeout)
    # start reciever
    reciever = threading.Thread(target=recv, daemon=True, args=(conn, ))
    reciever.start()

    if input_file:
        with open(input_file, 'r', encoding='utf-8') as fin:
            commands = fin.readlines()
            for command in commands:
                command = command.strip()
                # ignore comments and empty lines
                if command and command[0] != '#':
                    if not dry_run:
                        safe_serial_write(conn, (command + '\r\n').encode())
                    print(command)

    else:
        command = ' '.join(commands).strip()
        if command:
            if not dry_run:
                # send command
                safe_serial_write(conn, (command + '\r\n').encode())
            print(command)

    # wait for a while to receive feedback
    time.sleep(2)
    stop_event.set()
    reciever.join(timeout=1)

    conn.close()


if __name__ == '__main__':
    main()
