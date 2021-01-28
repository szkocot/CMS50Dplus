import argparse
from functools import partial
import pandas as pd


class Converter(object):

    def __init__(self, input_file, output_file):
        self.output_file = output_file
        self.input_file = input_file
        self.file = None

        self.package_size = 5  # 5 bytes
        self.columns = ["Time", "PulseRate", "SpO2", "PulseWaveform",
                        "BarGraph", "SignalStrength", "Beep", "FingerOut",
                        "Searching", "DroppingSpO2", "ProbeError"]

    def get_readings(self):

        readings = []

        with open(self.input_file, "rb") as file:
            reader = partial(file.read1, self.package_size)
            file_iterator = iter(reader, bytes())

            for i, data in enumerate(file_iterator):

                if [d & 0x80 != 0 for d in data] !=\
                        [True, False, False, False, False]:
                    raise ValueError("Invalid data packet.")

                # 1st byte
                signalStrength = data[0] & 0x0f
                fingerOut = bool(data[0] & 0x10)
                droppingSpO2 = bool(data[0] & 0x20)
                beep = bool(data[0] & 0x40)

                # 2nd byte
                pulseWaveform = data[1]

                # 3rd byte
                barGraph = data[2] & 0x0f
                probeError = bool(data[2] & 0x10)
                searching = bool(data[2] & 0x20)
                pulseRate = (data[2] & 0x40) << 1

                # 4th byte
                pulseRate |= data[3] & 0x7f

                # 5th byte
                bloodSpO2 = data[4] & 0x7f

                # time
                time = i/60

                reading = [time, pulseRate, bloodSpO2, pulseWaveform,
                           barGraph, signalStrength, beep,
                           fingerOut, searching, droppingSpO2,
                           probeError]

                readings.append(reading)

        return readings


def dumpFileData(input_file, output_file):

    converter = Converter(input_file, output_file)
    readings = converter.get_readings()
    df = pd.DataFrame(readings, columns=converter.columns)
    df.to_csv(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Binary data converted based on cms50dplus.py v1.2 - Contec CMS50D+ Data Downloader (c) 2015 atbrask")
    parser.add_argument("input", help="Input binary file.")
    parser.add_argument("output", help="Output CSV file.")

    args = parser.parse_args()

    dumpFileData(args.input, args.output)
