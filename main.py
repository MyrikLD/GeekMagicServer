import socket

import psutil

PORT = 8010
HOST = "0.0.0.0"


def generate_aida64_data(
    cpu_freq: int,
    cpu_usage: int,
    ram_usage: int,
    drive_c_percent: int,
    drive_c_free: int,
    t_cpu: int,
    pw_cpu: int,
):
    _data = {
        "F_CPU": f"{cpu_freq} MHz",
        "UP_CPU": f"{cpu_usage}%",
        # "S_FAN": f"{s_fan}%",
        "UP_RAM": f"{ram_usage}%",
        # "U_DRIVE_C": f"{drive_c_used} GB",
        "T_CPU": f"{t_cpu}%",
        "UP_DRIVE_C": f"{drive_c_percent}%",
        # "$CHIPSET": f"{chipset}%",
        "FR_DRIVE_C": f"{drive_c_free} GB",
        # "U_RAM": f"{ram_used} MB",
        # "TIME": f"{current_time}",
        # "GPU1": f"{gpu1}%",
        # "GPU2": f"{gpu2}%",
        "PW_CPU": f"{pw_cpu}W",
    }

    return (
        "Page0|"
        + "".join(
            [
                "{|}" + f"Sample{n+1}|{key}: {value}"
                for n, (key, value) in enumerate(_data.items())
            ]
        )
        + "{|}"
    )


def get_payload():
    header = (
        b"HTTP/1.1 200 OK\n"
        b"Content-Type: text/event-stream\n"
        b"\n"
    )

    disk = psutil.disk_usage("/home")

    data = generate_aida64_data(
        cpu_freq=psutil.cpu_freq().current,
        cpu_usage=psutil.cpu_percent(),
        ram_usage=psutil.virtual_memory().percent,
        drive_c_percent=disk.percent,
        drive_c_free=int(disk.free / (2**30)),
        t_cpu=psutil.sensors_temperatures()["k10temp"][0].current,
        pw_cpu=psutil.swap_memory().percent,
    )
    return header + f"data: {data}\n\n".encode("utf-8")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server is listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            with conn:
                # print(f"Connected by {addr}")
                try:
                    conn.sendall(get_payload())
                except ConnectionResetError:
                    print(f"Connection from {addr} was reset")
                except BrokenPipeError:
                    print(f"Connection to {addr} was broken")


if __name__ == "__main__":
    main()
