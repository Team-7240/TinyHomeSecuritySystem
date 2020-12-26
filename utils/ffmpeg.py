import subprocess


def ffmpeg_streaming(input_addr, output_addr, resolution="1024x768"):
    command = [
        "ffmpeg",
        "-i", input_addr,
        "-f", "flv",
        "-s", resolution,
        "-c:v", "libx264",
        output_addr
    ]
    return subprocess.Popen(command)
