"""
:author:    J.M. Algarín
:email:     josalggui@i3m.upv.es
:affiliation: MRILab, i3M, CSIC, Valencia, Spain
"""

import os
import time
import shutil
import platform
import subprocess
import threading
import numpy as np

from marge.widgets.widget_toolbar_marcos import MarcosToolBar
import marge.marcos.marcos_client.experiment as ex
import marge.configs.hw_config as hw
from marge.autotuning import autotuning


class MarcosController(MarcosToolBar):
    """
    Controller class for managing MaRCoS functionality.
    """

    def __init__(self, *args, **kwargs):
        super(MarcosController, self).__init__(*args, **kwargs)

        # Copy relevant files from marcos_extras
        shutil.copy("marcos/marcos_extras/copy_bitstream.sh", "../marge")
        shutil.copy("marcos/marcos_extras/marcos_fpga_rp-122.bit", "../marge")
        shutil.copy("marcos/marcos_extras/marcos_fpga_rp-122.bit.bin", "../marge")
        shutil.copy("marcos/marcos_extras/marcos_fpga_rp-122.dtbo", "../marge")
        shutil.copy("marcos/marcos_extras/readme.org", "../marge")

        self.action_server.setCheckable(True)
        self.action_start.triggered.connect(self.startMaRCoS)
        self.action_server.triggered.connect(self.controlMarcosServer)
        self.action_copybitstream.triggered.connect(self.copyBitStream)
        self.action_gpa_init.triggered.connect(self.initgpa)  # <- Tu as eu l'erreur ici

        thread = threading.Thread(target=self.search_sdrlab)
        thread.start()

        # Arduino to control the interlock
        self.arduino = autotuning.Arduino(baudrate=19200, name="interlock", serial_number=hw.ard_sn_interlock)
        self.arduino.connect()

    def search_sdrlab(self):
        if not self.main.demo:
            try:
                hw.rp_ip_address = self.get_sdrlab_ip()[0]
            except:
                print("ERROR: No SDRLab found.")
                try:
                    hw.rp_ip_address = self.get_sdrlab_ip()[0]
                except:
                    print("ERROR: No communication with SDRLab.")
                    print("ERROR: Try manually.")

    @staticmethod
    def get_sdrlab_ip():
        print("Searching for SDRLabs...")
        ip_addresses = []
        subnet = '192.168.1.'
        timeout = 0.1

        for i in range(101, 132):
            ip = subnet + str(i)
            try:
                if platform.system() == 'Linux':
                    result = subprocess.run(['ping', '-c', '1', ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
                elif platform.system() == 'Windows':
                    result = subprocess.run(['ping', '-n', '1', ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
                else:
                    continue

                if result.returncode == 0:
                    print(f"Checking ip {ip}...")
                    ssh_command = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=5', f'root@{ip}', 'exit']
                    ssh_result = subprocess.run(ssh_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if ssh_result.returncode == 0:
                        ip_addresses.append(ip)
                    else:
                        print(f"WARNING: No SDRLab found at ip {ip}.")
            except:
                continue

        for ip in ip_addresses:
            print("READY: SDRLab found at IP " + ip)

        return ip_addresses

    def startMaRCoS(self):
        if not self.main.demo:
            try:
                subprocess.run([hw.bash_path, "--", "./communicateRP.sh", hw.rp_ip_address, "killall marcos_server"])
                subprocess.run([hw.bash_path, "--", "./startRP.sh", hw.rp_ip_address, hw.rp_version])
                self.initgpa()
                print("READY: MaRCoS updated, server connected, gpa initialized.")
            except:
                print("ERROR: Server connection not found! Please verify if the blue LED is illuminated on the Red Pitaya.")
        else:
            print("This is a demo\n")

        self.action_server.setChecked(True)
        self.main.toolbar_sequences.serverConnected()

    def controlMarcosServer(self):
        if not self.main.demo:
            if not self.action_server.isChecked():
                subprocess.run([hw.bash_path, "--", "./communicateRP.sh", hw.rp_ip_address, "killall marcos_server"])
                self.action_server.setStatusTip('Connect to marcos server')
                self.action_server.setToolTip('Connect to marcos server')
                print("Server disconnected")
            else:
                try:
                    subprocess.run([hw.bash_path, "--", "./communicateRP.sh", hw.rp_ip_address, "killall marcos_server"])
                    time.sleep(1.5)
                    subprocess.run([hw.bash_path, "--", "./communicateRP.sh", hw.rp_ip_address, "~/marcos_server"])
                    time.sleep(1.5)
                    self.action_server.setStatusTip('Kill marcos server')
                    self.action_server.setToolTip('Kill marcos server')

                    expt = ex.Experiment(init_gpa=False)
                    expt.add_flodict({'grad_vx': (np.array([100]), np.array([0]))})
                    expt.run()
                    expt.__del__()

                    print("READY: Server connected!")
                except Exception as e:
                    print("ERROR: Server not connected!")
                    print("ERROR: Try to connect to the server again.")
                    print(e)
        else:
            print("This is a demo\n")

    def copyBitStream(self):
        if not self.main.demo:
            try:
                subprocess.run([hw.bash_path, "--", "./communicateRP.sh", hw.rp_ip_address, "killall marcos_server"])
                subprocess.run([hw.bash_path, '--', './copy_bitstream.sh', hw.rp_ip_address, 'rp-122'], timeout=10)
                print("READY: MaRCoS updated")
            except subprocess.TimeoutExpired as e:
                print("ERROR: MaRCoS init timeout")
                print(e)
        else:
            print("This is a demo\n")

        self.action_server.setChecked(False)
        self.main.toolbar_sequences.serverConnected()

    def initgpa(self):
        """
        Initializes the GPA (Gradient Power Amplifier) hardware.
        """
        if not self.main.demo:
            try:
                subprocess.run([hw.bash_path, "--", "./initGPA.sh", hw.rp_ip_address], timeout=10)
                print("READY: GPA initialized")
            except subprocess.TimeoutExpired as e:
                print("ERROR: GPA init timeout")
                print(e)
        else:
            print("This is a demo\n")
